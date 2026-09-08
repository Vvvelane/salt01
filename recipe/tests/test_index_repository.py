from __future__ import annotations

import json
from pathlib import Path

import duckdb
import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from recipe.index_repository import IndexContractError, IndexRepository, IndexUnavailable
from recipe.settings import Settings


def config(tmp_path: Path) -> Settings:
    return Settings(
        salt_data_root=tmp_path / "salt-data",
        research_root=None,
        static_dir=tmp_path / "static",
        index_dsn=":memory:",
    )


def test_relative_locator_resolves_below_salt_data_root(tmp_path: Path) -> None:
    root = tmp_path / "salt-data"
    path = root / "派生数据" / "CU.parquet"
    path.parent.mkdir(parents=True)
    pq.write_table(pa.table({"时间": ["2026-01-01"], "收盘价": [1.0]}), path)

    resolved = IndexRepository(config(tmp_path))._resolve_locator_paths(["派生数据/CU.parquet"], "series-cu")

    assert resolved == [str(path.resolve())]


def test_locator_rejects_escape_and_missing_files(tmp_path: Path) -> None:
    repository = IndexRepository(config(tmp_path))
    with pytest.raises(IndexContractError):
        repository._resolve_locator_paths(["../outside.parquet"], "series-escape")
    with pytest.raises(IndexUnavailable):
        repository._resolve_locator_paths(["missing.parquet"], "series-missing")


def test_read_locator_uses_resolved_relative_path(tmp_path: Path) -> None:
    root = tmp_path / "salt-data"
    path = root / "派生数据" / "CU.parquet"
    path.parent.mkdir(parents=True)
    pq.write_table(
        pa.table({"时间": ["2026-01-01 09:00:00"], "开盘价": [10.0], "收盘价": [11.0]}),
        path,
    )
    repository = IndexRepository(config(tmp_path))
    con = duckdb.connect(":memory:")
    try:
        rows = repository._read_locator(
            con,
            {
                "series_id": "series-cu",
                "storage_locator": json.dumps({
                    "paths": ["派生数据/CU.parquet"],
                    "field_map": {"timestamp": "时间", "open": "开盘价", "close": "收盘价"},
                    "contract_code": "CU",
                }, ensure_ascii=False),
                "content_revision": "test",
            },
            None,
            None,
            10,
        )
    finally:
        con.close()

    assert len(rows) == 1
    assert rows[0]["open"] == 10.0
    assert rows[0]["close"] == 11.0


def test_latest_catalog_contract_is_available() -> None:
    repository = IndexRepository()
    state = repository.state()
    assert state.available is True
    assert state.contract_ready is True
    assert state.schema_version == "catalog-v2"
    assert len(repository.exchanges()) == 6

from __future__ import annotations

import csv
import os
from pathlib import Path

from recipe.catalog import parse_market_path, refresh_catalog
from recipe.settings import Settings


def write_csv(root: Path, relative: str, header: list[str], rows: list[list[object]]) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)


def test_path_parser_families_and_alias():
    main = parse_market_path("主要合约/1min/CFFEX/IC/IC.csv")
    assert main.asset_kind == "continuous"
    assert main.contract == "continuous"
    contract = parse_market_path("全部合约/1min/SHFE/RB/RB2501.csv")
    assert contract.asset_kind == "contract"
    assert contract.contract == "RB2501"
    alias = parse_market_path("全部合约/1min/CFFEX/IC/1min/IC2401.csv")
    assert alias.status == "alias"
    assert "suspected_alias" in alias.warning_codes
    assert alias.canonical_relative_path == "全部合约/1min/CFFEX/IC/IC2401.csv"
    index = parse_market_path("IM指数数据/SH.000852-daily.csv")
    assert index.asset_kind == "cash_index"
    assert index.exchange == "SSE"


def test_unknown_and_hidden_paths_are_safe():
    assert parse_market_path(".ipynb_checkpoints/x.csv").status == "excluded"
    assert parse_market_path("weird/x.csv").status == "unclassified"
    assert parse_market_path("全部合约/2hour/X/Y/Z.csv").status == "unclassified"


def test_refresh_identifies_schemas_and_deduplicates_alias(tmp_path: Path):
    root = tmp_path / "market"
    headers = {
        "m": ["datetime", "open", "high", "low", "close", "volume", "amount", "position", "symbol"],
        "cm": ["datetime", "open", "high", "low", "close", "volume", "money", "open_interest"],
        "cd": ["symbol", "open", "high", "low", "close", "volume", "money", "open_interest", "datetime"],
        "cp": ["datetime", "symbol", "open", "high", "low", "close", "volume", "money", "open_interest"],
        "i": ["datetime", "open", "high", "low", "close", "volume", "amount"],
    }
    row = ["2026-01-01 09:00:00", 1, 2, 0.5, 1.5, 10, 20, 3, "IC"]
    write_csv(root, "主要合约/1min/CFFEX/IC/IC.csv", headers["m"], [row])
    write_csv(root, "全部合约/1min/CFFEX/IC/IC2401.csv", headers["cm"], [row[:7] + [3]])
    write_csv(root, "全部合约/1min/CFFEX/IC/1min/IC2401.csv", headers["cm"], [row[:7] + [3]])
    write_csv(root, "全部合约/日/IC/CFFEX.IC2401.csv", headers["cd"], [["CFFEX.IC2401", 1, 2, .5, 1.5, 10, 20, 3, "2026-01-01"]])
    write_csv(root, "全部合约/周/IC/CFFEX.IC2401.csv", headers["cp"], [["2026-01-01", "CFFEX.IC2401", 1, 2, .5, 1.5, 10, 20, 3]])
    write_csv(root, "IM指数数据/SH.000852.csv", headers["i"], [["2026-01-01", 1, 2, .5, 1.5, 10, 20]])
    write_csv(root, ".ipynb_checkpoints/x.csv", headers["i"], [])
    db = tmp_path / "catalog.sqlite"
    config = Settings(root, None, db, tmp_path / "static")
    result = refresh_catalog(config)
    assert result["file_count"] == 7
    assert result["schema_count"] == 5
    import sqlite3
    with sqlite3.connect(db) as conn:
        assert conn.execute("select count(*) from files").fetchone()[0] == 7
        assert conn.execute("select count(*) from assets").fetchone()[0] == 5
        assert conn.execute("select count(*) from files where status='alias'").fetchone()[0] == 1
        assert conn.execute("select count(*) from files where status='excluded'").fetchone()[0] == 1


def test_refresh_is_incremental_for_unchanged_files(tmp_path: Path):
    root = tmp_path / "market"
    header = ["datetime", "open", "high", "low", "close", "volume", "amount", "position", "symbol"]
    write_csv(root, "主要合约/1min/CFFEX/IC/IC.csv", header, [["2026-01-01", 1, 2, 0, 1, 1, 1, 1, "IC"]])
    config = Settings(root, None, tmp_path / "catalog.sqlite", tmp_path / "static")
    first = refresh_catalog(config)
    second = refresh_catalog(config)
    assert second["file_count"] == first["file_count"]
    assert second["asset_count"] == first["asset_count"]

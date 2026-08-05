from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from recipe.adapters.market_csv import InvalidQuery, MarketCSVAdapter, RangeTooLarge, parse_timestamp
from recipe.catalog import refresh_catalog
from recipe.settings import Settings


def write(path: Path, header: list[str], rows: list[list[object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        csv.writer(handle).writerows([header] + rows)


def build(tmp_path: Path) -> tuple[Settings, str]:
    root = tmp_path / "market"
    write(root / "主要合约/1min/CFFEX/IC/IC.csv", ["datetime", "open", "high", "low", "close", "volume", "amount", "position", "symbol"], [
        ["2026-01-01 09:00:00", 1, 2, 0, 1.5, 10, 20, 3, "IC"],
        ["2026-01-01 09:01:00", 1.5, 2.5, 1, 2, 11, "NaN", 4, "IC"],
        ["2026-01-01 09:02:00", 2, 3, 1.5, 2.5, 12, 22, 5, "IC"],
    ])
    config = Settings(root, None, tmp_path / "catalog.sqlite", tmp_path / "static")
    refresh_catalog(config)
    import sqlite3
    with sqlite3.connect(config.catalog_db) as conn:
        asset_id = conn.execute("select asset_id from assets limit 1").fetchone()[0]
    return config, asset_id


def test_datetime_formats_and_raw_semantics(tmp_path: Path):
    assert parse_timestamp("2026-01-01 09:00:00").hour == 9
    assert parse_timestamp("2026-1-2") is not None
    assert parse_timestamp("2026/2/27").month == 2
    config, asset_id = build(tmp_path)
    result = MarketCSVAdapter(config).bars(asset_id, "2026-01-01 09:00:00", "2026-01-01 09:02:00", ["open", "close", "volume"], 10)
    assert len(result["bars"]) == 3
    assert result["bars"][0]["activity_raw_field"] == "amount"
    assert result["bars"][0]["position_raw_field"] == "position"
    assert result["bars"][0]["timezone"] is None
    assert result["bars"][0]["trading_date"] is None
    assert any(w["code"] == "non_finite_value" for w in result["warnings"])


def test_range_limit_and_no_default_scan(tmp_path: Path):
    config, asset_id = build(tmp_path)
    adapter = MarketCSVAdapter(config)
    with pytest.raises(InvalidQuery):
        adapter.bars(asset_id, None, None, None, 10)
    with pytest.raises(RangeTooLarge):
        adapter.bars(asset_id, "2026-01-01", "2026-01-02", None, 2)


def test_context_uses_selected_asset_only(tmp_path: Path):
    config, asset_id = build(tmp_path)
    result = MarketCSVAdapter(config).context(asset_id, "2026-01-01 09:01:00", 1, 1)
    assert len(result["bars"]) == 3
    assert result["selected_timestamp"] == "2026-01-01 09:01:00"


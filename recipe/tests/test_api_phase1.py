from __future__ import annotations

import csv
from pathlib import Path

from fastapi.testclient import TestClient

from recipe.catalog import refresh_catalog
from recipe.settings import Settings


def test_api_does_not_leak_absolute_root(monkeypatch, tmp_path: Path):
    market = tmp_path / "行情根目录"
    file = market / "主要合约" / "1min" / "CFFEX" / "IC" / "IC.csv"
    file.parent.mkdir(parents=True)
    with file.open("w", newline="", encoding="utf-8") as handle:
        csv.writer(handle).writerows([
            ["datetime", "open", "high", "low", "close", "volume", "amount", "position", "symbol"],
            ["2026-01-01 09:00:00", 1, 2, 0, 1, 1, 2, 3, "IC"],
        ])
    db = tmp_path / "catalog.sqlite"
    config = Settings(market, None, db, tmp_path / "static")
    refresh_catalog(config)
    import recipe.api.catalog as catalog_api
    import recipe.api.health as health_api
    monkeypatch.setattr(catalog_api, "settings", config)
    monkeypatch.setattr(health_api, "settings", config)
    from recipe.app import app
    with TestClient(app) as client:
        response = client.get("/api/v1/catalog/assets")
        assert response.status_code == 200
        assert str(market) not in response.text
        assert response.json()["data"][0]["asset_kind"] == "continuous"
        assert client.get("/api/v1/health").json()["data"]["service"] == "ok"


def test_api_catalog_unavailable_is_explicit(monkeypatch, tmp_path: Path):
    config = Settings(tmp_path / "missing", None, tmp_path / "missing.sqlite", tmp_path / "static")
    import recipe.api.catalog as catalog_api
    monkeypatch.setattr(catalog_api, "settings", config)
    from recipe.app import app
    with TestClient(app) as client:
        payload = client.get("/api/v1/catalog/summary").json()
        assert payload["status"] == "catalog_unavailable"
        assert "python -m recipe.catalog refresh" in payload["warnings"][0]["message"]


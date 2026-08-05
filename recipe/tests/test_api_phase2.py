from __future__ import annotations

from fastapi.testclient import TestClient

from recipe.app import app
from recipe.catalog import catalog_meta


def test_market_api_no_catalog_is_explicit(monkeypatch, tmp_path):
    import recipe.api.market as market_api
    from recipe.settings import Settings
    monkeypatch.setattr(market_api, "settings", Settings(tmp_path / "missing", None, tmp_path / "missing.sqlite", tmp_path / "static"))
    assert TestClient(app).get("/api/v1/market/bars", params={"asset_id": "12345678", "start": "2026-01-01", "end": "2026-01-02"}).json()["status"] == "catalog_unavailable"


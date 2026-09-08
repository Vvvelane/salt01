from __future__ import annotations

from fastapi.testclient import TestClient

from recipe.app import app


def test_only_v2_api_is_exposed() -> None:
    with TestClient(app) as client:
        health = client.get("/api/v2/health")
        assert health.status_code == 200
        assert health.json()["status"] == "ok"
        assert client.get("/api/v1/health").status_code == 404


def test_v2_catalog_is_readable() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v2/catalog/products", params={"exchange": "CFFEX"})
        assert response.status_code == 200
        assert response.json()["data"]
        assert response.json()["meta"]["catalog_schema_version"] == "catalog-v2"

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from ..catalog import anomalies, catalog_meta, catalog_options, get_asset, get_schema, list_assets, list_schemas
from ..settings import settings

router = APIRouter(prefix="/catalog", tags=["catalog"])


def _unavailable() -> dict:
    return {"data": None, "meta": {}, "warnings": [{"code": "catalog_unavailable", "message": "Catalog has not been built. Run python -m recipe.catalog refresh."}], "status": "catalog_unavailable"}


@router.get("/summary")
def summary() -> dict:
    meta = catalog_meta(settings)
    if not meta:
        return _unavailable()
    return {"data": meta, "meta": {"catalog_revision": meta["catalog_revision"]}, "warnings": [], "status": "ok"}


@router.get("/assets")
def assets(family: Optional[str] = None, frequency: Optional[str] = None, exchange: Optional[str] = None, product: Optional[str] = None, asset_kind: Optional[str] = None, status: Optional[str] = None, search: Optional[str] = Query(default=None, max_length=80), page_size: int = Query(default=50, ge=1, le=200), cursor: Optional[str] = Query(default=None, max_length=80)) -> dict:
    meta = catalog_meta(settings)
    if not meta:
        return _unavailable()
    data, next_cursor = list_assets(settings, {"family": family, "frequency": frequency, "exchange": exchange, "product": product, "asset_kind": asset_kind, "status": status, "search": search}, page_size, cursor)
    return {"data": data, "meta": {"catalog_revision": meta["catalog_revision"], "next_cursor": next_cursor}, "warnings": [], "status": "ok"}


@router.get("/options")
def options(family: Optional[str] = None, frequency: Optional[str] = None, exchange: Optional[str] = None, product: Optional[str] = None, asset_kind: Optional[str] = None) -> dict:
    meta = catalog_meta(settings)
    if not meta:
        return _unavailable()
    data = catalog_options(settings, {"family": family, "frequency": frequency, "exchange": exchange, "product": product, "asset_kind": asset_kind})
    return {"data": data, "meta": {"catalog_revision": meta["catalog_revision"]}, "warnings": [], "status": "ok"}


@router.get("/assets/{asset_id}")
def asset(asset_id: str) -> dict:
    item = get_asset(settings, asset_id)
    if item is None:
        if not catalog_meta(settings):
            return _unavailable()
        raise HTTPException(status_code=404, detail="asset_not_found")
    return {"data": item, "meta": {"catalog_revision": catalog_meta(settings)["catalog_revision"]}, "warnings": [], "status": "ok"}


@router.get("/schemas")
def schemas() -> dict:
    meta = catalog_meta(settings)
    if not meta:
        return _unavailable()
    return {"data": list_schemas(settings), "meta": {"catalog_revision": meta["catalog_revision"]}, "warnings": [], "status": "ok"}


@router.get("/schemas/{schema_id}")
def schema(schema_id: str) -> dict:
    item = get_schema(settings, schema_id)
    if item is None:
        if not catalog_meta(settings):
            return _unavailable()
        raise HTTPException(status_code=404, detail="schema_not_found")
    return {"data": item, "meta": {"catalog_revision": catalog_meta(settings)["catalog_revision"]}, "warnings": [], "status": "ok"}


@router.get("/fields/{schema_id}")
def fields(schema_id: str) -> dict:
    item = get_schema(settings, schema_id)
    if item is None:
        raise HTTPException(status_code=404, detail="schema_not_found")
    return {"data": item["fields"], "meta": {"catalog_revision": catalog_meta(settings)["catalog_revision"]}, "warnings": [], "status": "ok"}


@router.get("/anomalies")
def anomaly_list() -> dict:
    meta = catalog_meta(settings)
    if not meta:
        return _unavailable()
    return {"data": anomalies(settings), "meta": {"catalog_revision": meta["catalog_revision"]}, "warnings": [], "status": "ok"}

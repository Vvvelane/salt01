from __future__ import annotations

import hashlib
import json
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Request, Response

from ..adapters.market_csv import AssetNotFound, InvalidQuery, MarketCSVAdapter, RangeTooLarge, UnsupportedField, query_cache
from ..catalog import catalog_meta
from ..settings import settings

router = APIRouter(prefix="/market", tags=["market"])


def _error(exc: Exception) -> None:
    code = getattr(exc, "code", "market_error")
    status = 413 if code == "range_too_large" else 422 if code in {"invalid_query", "unsupported_field"} else 404
    raise HTTPException(status_code=status, detail={"code": code, "message": str(exc)})


@router.get("/bars")
def bars(request: Request, response: Response, asset_id: str = Query(min_length=8, max_length=80), start: Optional[str] = Query(default=None, max_length=40), end: Optional[str] = Query(default=None, max_length=40), fields: Optional[str] = Query(default=None, max_length=500), limit: int = Query(default=500, ge=1, le=5000)) -> dict:
    meta = catalog_meta(settings)
    if not meta:
        return {"data": None, "meta": {}, "warnings": [{"code": "catalog_unavailable", "message": "Catalog has not been built."}], "status": "catalog_unavailable"}
    field_list = [field.strip() for field in fields.split(",")] if fields else None
    adapter = MarketCSVAdapter(settings)
    try:
        asset = adapter._asset_and_path(asset_id)
        stat = asset[1].stat()
        key = json.dumps([asset_id, stat.st_size, stat.st_mtime_ns, start, end, field_list, limit, adapter.schema_version], ensure_ascii=False)
        cached = query_cache.get(key)
        if cached is None:
            cached = adapter.bars(asset_id, start, end, field_list, limit)
            query_cache.put(key, cached)
        payload = {"data": cached, "meta": {"catalog_revision": meta["catalog_revision"], "request_id": hashlib.sha256(key.encode()).hexdigest()[:16]}, "warnings": cached.get("warnings", []), "status": "ok" if cached.get("bars") else "no_data"}
        etag = hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str).encode()).hexdigest()
        response.headers["ETag"] = etag
        if request.headers.get("if-none-match") == etag:
            response.status_code = 304
            return {}
        return payload
    except (AssetNotFound, InvalidQuery, RangeTooLarge, UnsupportedField) as exc:
        _error(exc)


@router.get("/context")
def context(asset_id: str = Query(min_length=8, max_length=80), timestamp: str = Query(max_length=40), before: int = Query(default=3, ge=0, le=100), after: int = Query(default=3, ge=0, le=100)) -> dict:
    meta = catalog_meta(settings)
    if not meta:
        return {"data": None, "meta": {}, "warnings": [{"code": "catalog_unavailable", "message": "Catalog has not been built."}], "status": "catalog_unavailable"}
    try:
        data = MarketCSVAdapter(settings).context(asset_id, timestamp, before, after)
        return {"data": data, "meta": {"catalog_revision": meta["catalog_revision"]}, "warnings": data.get("warnings", []), "status": "ok" if data.get("bars") else "no_data"}
    except (AssetNotFound, InvalidQuery, RangeTooLarge, UnsupportedField) as exc:
        _error(exc)


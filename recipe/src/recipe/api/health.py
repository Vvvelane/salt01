from __future__ import annotations

from fastapi import APIRouter

from ..catalog import catalog_meta
from ..settings import settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    return {"data": {"service": "ok", "catalog": "ready" if catalog_meta(settings) else "unavailable"}, "meta": {}, "warnings": [], "status": "ok"}


@router.get("/status")
def status() -> dict:
    meta = catalog_meta(settings)
    return {"data": {"service": "recipe", "catalog": "ready" if meta else "unavailable", "market_root": "configured" if settings.market_root.is_dir() else "unavailable", "research_sources": 1 if settings.research_root else 0, "cache": "ready", "current_revisions": {"catalog": meta["catalog_revision"] if meta else None}}, "meta": {}, "warnings": [] if meta else [{"code": "catalog_unavailable", "message": "Catalog has not been built."}], "status": "ok" if meta else "catalog_unavailable"}


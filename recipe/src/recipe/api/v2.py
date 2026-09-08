from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from ..index_repository import (
    IndexContractError,
    IndexErrorBase,
    IndexRepository,
    IndexUnavailable,
    QueryValidationError,
)
from ..settings import settings

router = APIRouter(prefix="/api/v2", tags=["recipe-v2"])


def _meta(repository: IndexRepository) -> dict:
    state = repository.state()
    return {
        "catalog_revision": state.catalog_revision,
        "catalog_schema_version": state.schema_version,
        "index_contract_ready": state.contract_ready,
    }


def _error(exc: IndexErrorBase) -> None:
    status = 503 if isinstance(exc, (IndexUnavailable, IndexContractError)) else 422
    raise HTTPException(status_code=status, detail={"code": exc.code, "message": str(exc)})


def _ok(repository: IndexRepository, data, warnings: list | None = None, **meta) -> dict:
    return {"data": data, "meta": {**_meta(repository), **meta}, "warnings": warnings or [], "status": "ok"}


@router.get("/health")
def health() -> dict:
    repository = IndexRepository(settings)
    state = repository.state()
    return {
        "data": {
            "service": "ok",
            "index": "ready" if state.contract_ready else "unavailable",
            "index_dsn_configured": bool(state.dsn),
            "missing_views": list(state.missing_views),
        },
        "meta": {"catalog_revision": state.catalog_revision, "catalog_schema_version": state.schema_version},
        "warnings": [] if state.contract_ready else [{"code": state.message or "index_contract_incomplete", "message": state.message or "DuckDB index contract is incomplete."}],
        "status": "ok" if state.contract_ready else "index_unavailable",
    }


@router.get("/catalog/exchanges")
def exchanges() -> dict:
    repository = IndexRepository(settings)
    try:
        return _ok(repository, repository.exchanges())
    except IndexErrorBase as exc:
        _error(exc)


@router.get("/catalog/products")
def products(exchange: str | None = Query(default=None, max_length=32)) -> dict:
    repository = IndexRepository(settings)
    try:
        return _ok(repository, repository.products(exchange))
    except IndexErrorBase as exc:
        _error(exc)


@router.get("/products/{product_id}/availability")
def availability(product_id: str) -> dict:
    repository = IndexRepository(settings)
    try:
        product = repository.product(product_id)
        if not product:
            raise HTTPException(status_code=404, detail={"code": "product_not_found", "message": product_id})
        return _ok(repository, {"product": product, "datasets": repository.availability(product_id)})
    except HTTPException:
        raise
    except IndexErrorBase as exc:
        _error(exc)


@router.get("/catalog/fields")
def fields(dataset_key: str | None = Query(default=None, max_length=80)) -> dict:
    repository = IndexRepository(settings)
    try:
        return _ok(repository, repository.fields(dataset_key))
    except IndexErrorBase as exc:
        _error(exc)


@router.get("/market/daily")
def daily(
    product_id: str,
    mode: str = Query(default="main"),
    contracts: str | None = Query(default=None, max_length=1000),
    start: str | None = Query(default=None, max_length=40),
    end: str | None = Query(default=None, max_length=40),
    limit: int = Query(default=20000, ge=1, le=200000),
) -> dict:
    repository = IndexRepository(settings)
    try:
        contract_values = [item.strip() for item in contracts.split(",") if item.strip()] if contracts else None
        payload = repository.market(product_id, "daily", mode, start, end, contract_values, None, limit)
        return _ok(repository, payload, payload.pop("warnings", []), frequency="daily")
    except IndexErrorBase as exc:
        _error(exc)


@router.get("/market/intraday")
def intraday(
    product_id: str,
    trading_date: str,
    mode: str = Query(default="main"),
    contract: str | None = Query(default=None, max_length=32),
    limit: int = Query(default=50000, ge=1, le=200000),
) -> dict:
    repository = IndexRepository(settings)
    try:
        payload = repository.intraday(product_id, trading_date, mode, contract, limit)
        return _ok(repository, payload, payload.pop("warnings", []), frequency="1min", trading_date=trading_date)
    except IndexErrorBase as exc:
        _error(exc)


@router.get("/market/rolls")
def rolls(product_id: str, start: str | None = None, end: str | None = None) -> dict:
    repository = IndexRepository(settings)
    try:
        # Roll events are a daily selection concern.  Use the same authoritative
        # selector as /market/daily instead of requesting an arbitrarily long
        # 1min range (which is intentionally capped for raw intraday queries).
        payload = repository.market(product_id, "daily", "main", start, end, limit=200000)
        bars = payload["bars"]
        events = []
        previous = None
        for bar in bars:
            current = bar.get("contract_code")
            if current and previous and current != previous:
                events.append({"timestamp": bar.get("timestamp"), "old_contract": previous, "new_contract": current, "series_id": bar.get("series_id")})
            if current:
                previous = current
        return _ok(repository, {"events": events, "source": payload.get("selection_source", "market.main.1min -> market.contract.daily")}, payload.pop("warnings", []), frequency="daily")
    except IndexErrorBase as exc:
        _error(exc)


@router.get("/quality/products/{product_id}/summary")
def quality_summary(product_id: str) -> dict:
    repository = IndexRepository(settings)
    try:
        rows = repository.quality_summary(product_id)
        if not rows:
            return {"data": [], "meta": _meta(repository), "warnings": [{"code": "quality_not_published", "message": "No versioned quality run is published for this product."}], "status": "unknown"}
        return _ok(repository, rows)
    except IndexErrorBase as exc:
        _error(exc)


@router.get("/quality/products/{product_id}/gaps")
def quality_gaps(product_id: str, limit: int = Query(default=200, ge=1, le=2000)) -> dict:
    repository = IndexRepository(settings)
    try:
        rows = repository.quality_events(product_id, limit)
        if not rows:
            return {"data": [], "meta": _meta(repository), "warnings": [{"code": "quality_not_published", "message": "No versioned quality events are published for this product."}], "status": "unknown"}
        return _ok(repository, rows)
    except IndexErrorBase as exc:
        _error(exc)


@router.get("/related/{dataset_key}")
def related(dataset_key: str, product_id: str, start: str | None = None, end: str | None = None) -> dict:
    repository = IndexRepository(settings)
    try:
        allowed = {"warehouse_receipts", "daily_positions", "spot_daily", "price_limits", "main_contract_map", "daily_settlement"}
        if dataset_key not in allowed:
            raise QueryValidationError(f"unsupported dataset_key: {dataset_key}")
        rows = repository.availability(product_id)
        item = next((row for row in rows if row.get("dataset_key") == dataset_key), None)
        if not item:
            raise IndexUnavailable(f"dataset availability not published: {dataset_key}")
        if item.get("status") != "available":
            return _ok(repository, {"dataset_key": dataset_key, "status": "NOT_APPLICABLE", "rows": []}, [{"code": "dataset_not_recorded", "message": f"{dataset_key} is not recorded for {product_id}."}])
        return _ok(repository, {"dataset_key": dataset_key, "status": "available", "rows": [], "availability": item}, [{"code": "related_query_pending", "message": "The first backend slice publishes availability; dataset-specific aggregation is next."}])
    except IndexErrorBase as exc:
        _error(exc)

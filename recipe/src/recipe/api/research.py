from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, HTTPException

from ..research import discover_runs
from ..settings import settings

router = APIRouter(prefix="/research", tags=["research"])


def no_data() -> dict[str, Any]:
    return {"data": None, "meta": {"expected_manifest_schema": "recipe-research-v1", "research_source_configured": bool(settings.research_root)}, "warnings": [{"code": "research_no_data", "message": "No research outputs configured."}, {"code": "research_contract", "message": "Add a valid research manifest and refresh the research catalog."}], "status": "no_data"}


def runs() -> list[dict[str, Any]]:
    return discover_runs(settings.research_root)


@router.get("/status")
def research_status() -> dict[str, Any]:
    items = runs()
    if not items:
        return no_data()
    return {"data": {"run_count": len(items), "runs": [{"identity": item.get("identity"), "valid": item.get("validation", {}).get("valid", True)} for item in items]}, "meta": {"expected_manifest_schema": "recipe-research-v1"}, "warnings": [], "status": "ok"}


@router.get("/runs")
def research_runs() -> dict[str, Any]:
    items = runs()
    if not items:
        return no_data()
    return {"data": [{"identity": item.get("identity"), "valid": item.get("validation", {}).get("valid", True)} for item in items], "meta": {}, "warnings": [], "status": "ok"}


def find_run(run_id: str) -> dict[str, Any]:
    for item in runs():
        if item.get("identity", {}).get("run_id") == run_id:
            return item
    if not settings.research_root:
        raise HTTPException(status_code=404, detail="research_run_not_found")
    raise HTTPException(status_code=404, detail="research_run_not_found")


@router.get("/runs/{run_id}")
def run(run_id: str) -> dict[str, Any]:
    if not settings.research_root:
        return no_data()
    item = find_run(run_id)
    return {"data": {"identity": item.get("identity"), "manifest": item.get("manifest"), "validation": item.get("validation", {"valid": True, "issues": []})}, "meta": {}, "warnings": [], "status": "ok" if item.get("validation", {}).get("valid", True) else "partial"}


def artifact(run_id: str, name: str) -> dict[str, Any]:
    if not settings.research_root:
        return no_data()
    item = find_run(run_id); manifest = item.get("manifest") or {}; spec = (manifest.get("artifacts") or {}).get(name)
    if not spec or spec.get("status") in {"no_data", "unavailable", "pending"}:
        return {"data": None, "meta": {}, "warnings": [{"code": "artifact_no_data", "artifact": name}], "status": "no_data"}
    return {"data": None, "meta": {}, "warnings": [{"code": "artifact_not_implemented", "artifact": name}], "status": "unsupported"}


for _name in ("factors", "policies", "pnl", "summary", "breakdowns", "trades", "timeline", "entry-examples", "shortlist", "audit"):
    endpoint_name = _name.replace("-", "_")
    router.add_api_route(f"/runs/{{run_id}}/{_name}", lambda run_id, _artifact=_name: artifact(run_id, _artifact), methods=["GET"], name=f"research_{endpoint_name}")

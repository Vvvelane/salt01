from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from saltcore.read import data_root

from .database import router as database_router
from .market import router as market_router
from .research import REGISTRY, catalog, read_json, replay, result

STATIC_DIR = Path(__file__).resolve().parents[2] / "static/dist"
app = FastAPI(title="SALT Research Terminal", version="0.2.0", docs_url="/api/docs")
app.include_router(market_router)
app.include_router(database_router)


@app.get("/api/health")
def health() -> dict:
    registry = read_json(REGISTRY)
    try:
        market_root, market_status = str(data_root()), "ready"
    except RuntimeError as exc:
        market_root, market_status = str(exc), "unavailable"
    return {
        "status": "ok",
        "service": "recipe",
        "market": market_status,
        "salt_data_root": market_root,
        "cards": len(registry["cards"]),
        "families": len(registry["families"]),
    }


@app.get("/api/cards")
def cards() -> dict:
    practiced: dict[str, list[dict]] = {}
    for strategy in catalog()["strategies"]:
        if strategy["ready"]:
            practiced.setdefault(strategy["factor_id"], []).append(
                {key: strategy[key] for key in ["strategy_id", "name", "frequency"]}
            )
    return {**read_json(REGISTRY), "factorlab": practiced}


@app.get("/api/research")
def research() -> dict:
    return catalog()


@app.get("/api/results")
def results(strategy: str) -> dict:
    return result(strategy)


@app.get("/api/replay")
def replay_example(strategy: str) -> dict:
    return replay(strategy)


if (STATIC_DIR / "assets").is_dir():
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    page = STATIC_DIR / "index.html"
    if not page.is_file():
        raise HTTPException(503, "Run npm run build to build the Recipe frontend")
    return FileResponse(page)

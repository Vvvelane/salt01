from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .api.catalog import router as catalog_router
from .api.health import router as health_router
from .api.market import router as market_router
from .api.research import router as research_router
from .settings import settings

app = FastAPI(title="Recipe", version="0.1.0", docs_url=None, redoc_url=None)
app.include_router(health_router, prefix="/api/v1")
app.include_router(catalog_router, prefix="/api/v1")
app.include_router(market_router, prefix="/api/v1")
app.include_router(research_router, prefix="/api/v1")

if settings.static_dir.is_dir():
    app.mount("/static", StaticFiles(directory=settings.static_dir), name="static")


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(settings.static_dir / "index.html")

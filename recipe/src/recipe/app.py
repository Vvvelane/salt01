from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .api.v2 import router as v2_router
from .settings import settings

app = FastAPI(title="Recipe", version="0.1.0", docs_url=None, redoc_url=None)
app.include_router(v2_router)

if settings.static_dir.is_dir():
    app.mount("/static", StaticFiles(directory=settings.static_dir), name="static")
    frontend_assets = settings.static_dir / "dist" / "assets"
    if frontend_assets.is_dir():
        app.mount("/assets", StaticFiles(directory=frontend_assets), name="frontend-assets")


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    frontend_index = settings.static_dir / "dist" / "index.html"
    return FileResponse(frontend_index)

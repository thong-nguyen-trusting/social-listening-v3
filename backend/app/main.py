from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.browser import router as browser_router
from app.api.health import router as health_router
from app.api.insights import router as insights_router
from app.api.labels import router as labels_router
from app.api.plans import router as plans_router
from app.api.runtime import router as runtime_router
from app.api.runs import router as runs_router
from app.adapters.http.api.v1.router import api_router
from app.infrastructure.config import get_settings
from app.infrastructure.lifespan import build_lifespan

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=build_lifespan(settings),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
app.include_router(browser_router)
app.include_router(health_router)
app.include_router(plans_router)
app.include_router(runs_router)
app.include_router(labels_router)
app.include_router(insights_router)
app.include_router(runtime_router)

static_dir = Path(settings.static_dir)
index_file = static_dir / "index.html"
if index_file.exists():
    app.mount("/assets", StaticFiles(directory=static_dir / "assets"), name="assets")

    @app.get("/", include_in_schema=False)
    async def frontend_index() -> FileResponse:
        return FileResponse(index_file)

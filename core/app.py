import sys
from contextlib import asynccontextmanager
from pathlib import Path

# Ensure repository root containing 'core' package is always resolvable in sys.path
_repo_root = str(Path(__file__).resolve().parent.parent)
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core import __version__
from core.api.v1.router import v1_router
from core.config.settings import get_settings
from core.db.orm import Automation, Result, Run  # noqa: F401
from core.db.session import Base, engine
from core.scheduler.service import scheduler_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure DB tables exist
    Base.metadata.create_all(bind=engine)

    # Startup: Start scheduler if enabled
    settings = get_settings()
    if settings.enable_scheduler:
        scheduler_service.start(check_interval_seconds=30)

    yield

    # Shutdown: Stop scheduler
    if settings.enable_scheduler:
        scheduler_service.shutdown()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Orbit",
        description="Autonomous Goal-Driven Web Data Operations",
        version=__version__,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(v1_router, prefix="/api/v1")

    return app


app = create_app()

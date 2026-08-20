from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from orbit import __version__
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

    # Mount versioned API
    app.include_router(v1_router, prefix="/api/v1")
    # Legacy mount for backward compatibility
    app.include_router(v1_router, prefix="/api")

    @app.get("/")
    def root():
        return {
            "name": "Orbit API",
            "version": __version__,
            "docs": "/docs",
            "principle": "Set the goal. Walk away.",
        }

    return app


app = create_app()

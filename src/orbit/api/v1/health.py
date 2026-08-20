from fastapi import APIRouter
from orbit import __version__
from orbit.config.settings import get_settings

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check():
    settings = get_settings()
    return {
        "status": "ok",
        "version": __version__,
        "environment": settings.app_env,
        "scheduler_enabled": settings.enable_scheduler,
    }

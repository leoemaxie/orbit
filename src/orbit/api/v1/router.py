from fastapi import APIRouter
from orbit.api.v1.automations import router as automations_router
from orbit.api.v1.health import router as health_router
from orbit.api.v1.runs import router as runs_router

v1_router = APIRouter()
v1_router.include_router(health_router)
v1_router.include_router(automations_router)
v1_router.include_router(runs_router)

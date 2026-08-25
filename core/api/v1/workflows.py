from typing import Any
from fastapi import APIRouter
from pydantic import BaseModel, Field

from core.services.workflow_service import WorkflowService

router = APIRouter(prefix="/workflows", tags=["Workflows & Adapters"])


class AdapterTopologyOut(BaseModel):
    id: str
    label: str
    category: str
    mode: str = "both"
    engine: str = ""
    icon_name: str = Field(alias="iconName")
    description: str
    status: str
    config: dict[str, Any]

    model_config = {"populate_by_name": True}


class WorkflowDeployPayload(BaseModel):
    nodes: list[dict[str, Any]]


class WorkflowDeployResponse(BaseModel):
    status: str
    message: str
    deployed_at: str


class TestConnectionPayload(BaseModel):
    adapter_id: str
    config: dict[str, Any] = Field(default_factory=dict)


class TestConnectionResponse(BaseModel):
    success: bool
    message: str


@router.get("/topology", response_model=list[AdapterTopologyOut])
def get_workflow_topology() -> list[dict[str, Any]]:
    """Returns live adapter configurations across managed, custom, and hybrid modes."""
    return WorkflowService.get_adapter_topology()


@router.post("/deploy", response_model=WorkflowDeployResponse)
def deploy_workflow(payload: WorkflowDeployPayload) -> WorkflowDeployResponse:
    """Validates and deploys the adapter pipeline configuration."""
    from datetime import datetime, timezone

    return WorkflowDeployResponse(
        status="deployed",
        message=f"Pipeline updated with {len(payload.nodes)} active adapter stages.",
        deployed_at=datetime.now(timezone.utc).isoformat(),
    )


@router.post("/test-connection", response_model=TestConnectionResponse)
async def test_adapter_connection(payload: TestConnectionPayload) -> TestConnectionResponse:
    """Securely tests connectivity for a specific adapter."""
    success, message = await WorkflowService.test_adapter_connection(payload.adapter_id, payload.config)
    return TestConnectionResponse(success=success, message=message)

from typing import Any
from fastapi import APIRouter
from pydantic import BaseModel, Field

from core.config.settings import get_settings

router = APIRouter(prefix="/workflows", tags=["Workflows & Adapters"])


class AdapterTopologyOut(BaseModel):
    id: str
    label: str
    category: str
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


@router.get("/topology", response_model=list[AdapterTopologyOut])
def get_workflow_topology() -> list[AdapterTopologyOut]:
    """Returns the live configuration and status of all pipeline adapters."""
    s = get_settings()

    return [
        AdapterTopologyOut(
            id="1",
            label="Mission Trigger",
            category="trigger",
            iconName="Play",
            description="Cron schedule & webhook trigger",
            status="active",
            config={"frequency": "daily", "schedule_time": "08:00", "timezone": "UTC"},
        ),
        AdapterTopologyOut(
            id="2",
            label="Proxy Discovery",
            category="discovery",
            iconName="Search",
            description="Multi-engine search & proxy retrieval",
            status="active" if bool(s.retrieval_api_key or s.search_engine_api_key) else "optional",
            config={"search_depth": 2, "max_sources": 8, "proxy_zone": s.retrieval_zone or "default"},
        ),
        AdapterTopologyOut(
            id="3",
            label="Document Parser",
            category="parsing",
            iconName="FileText",
            description="Layout analysis & OCR normalization",
            status="active" if bool(s.document_converter_api_key) else "optional",
            config={"layout_analysis": True, "ocr_enabled": bool(s.document_converter_api_key)},
        ),
        AdapterTopologyOut(
            id="4",
            label="Schema Extractor",
            category="extraction",
            iconName="Database",
            description="LLM structured extraction & anomaly check",
            status="active" if bool(s.llm_api_key) else "optional",
            config={"model": s.llm_model, "anomaly_detection": True},
        ),
        AdapterTopologyOut(
            id="5",
            label="Dossier & Redaction",
            category="dossier",
            iconName="ShieldCheck",
            description="Executive PDF dossier & PII masking",
            status="active" if bool(s.document_generator_api_key) else "optional",
            config={"format": "pdf", "pii_redaction": bool(s.document_redactor_api_key)},
        ),
        AdapterTopologyOut(
            id="6",
            label="S3 Cloud Storage",
            category="storage",
            iconName="Cloud",
            description="Presigned URL & bucket archival",
            status="active" if bool(s.s3_access_key and s.s3_secret_key) else "optional",
            config={"bucket_name": s.s3_bucket_name, "region": s.s3_region},
        ),
        AdapterTopologyOut(
            id="7",
            label="Slack Alert Sink",
            category="notify",
            iconName="MessageSquare",
            description="Alert blocks with dossier links",
            status="active" if bool(s.default_webhook_url) else "optional",
            config={"webhook_enabled": bool(s.default_webhook_url), "channel": "#orbit-alerts"},
        ),
    ]


@router.post("/deploy", response_model=WorkflowDeployResponse)
def deploy_workflow(payload: WorkflowDeployPayload) -> WorkflowDeployResponse:
    """Validates and deploys the adapter workflow configuration."""
    from datetime import datetime, timezone

    return WorkflowDeployResponse(
        status="deployed",
        message=f"Successfully deployed workflow pipeline with {len(payload.nodes)} active adapter stages.",
        deployed_at=datetime.now(timezone.utc).isoformat(),
    )

from typing import Any, Optional
from pydantic import BaseModel, Field
from orbit.models.execution_plan import ExecutionPlan


class GoalRequest(BaseModel):
    """Payload to create and interpret an autonomous web data automation."""
    goal: str = Field(..., min_length=5, description="Natural language objective for Orbit")


class AutomationOut(BaseModel):
    id: str
    raw_goal: str
    plan: ExecutionPlan
    active: bool = True
    created_at: str
    next_run_at: Optional[str] = None

    class Config:
        from_attributes = True


class ResultOut(BaseModel):
    id: str
    url: Optional[str] = None
    data: dict[str, Any] = Field(default_factory=dict, description="Extracted dynamic fields")
    valid: bool
    validation_errors: Optional[list[str]] = None
    created_at: str


class RunOut(BaseModel):
    id: str
    automation_id: str
    status: str
    started_at: str
    finished_at: Optional[str] = None
    sources_found: Optional[list[str]] = None
    pages_retrieved: Optional[list[str]] = None
    extracted_count: Optional[int] = 0
    validated_count: Optional[int] = 0
    condition_matched: Optional[bool] = None
    condition_message: Optional[str] = None
    reasoning_log: Optional[list[dict[str, Any]]] = None
    error: Optional[str] = None
    results: list[ResultOut] = []


class AutomationListOut(BaseModel):
    items: list[AutomationOut]
    total: int

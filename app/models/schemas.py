from typing import Optional
from pydantic import BaseModel, Field


class AutomationSpec(BaseModel):
    """Structured objective produced by the Goal Interpreter."""
    objective: str
    product_query: str = Field(..., description="Search-ready product description, e.g. 'iPhone 16 Pro 256GB'")
    geography: str = "Nigeria"
    data_fields: list[str] = Field(default_factory=lambda: ["price", "currency", "availability", "seller", "url"])
    frequency: str = "daily"
    time: Optional[str] = None          # e.g. "08:00"
    timezone: str = "Africa/Lagos"
    condition: Optional[str] = None     # e.g. "price < 1000000"


class GoalRequest(BaseModel):
    goal: str


class AutomationOut(BaseModel):
    id: str
    raw_goal: str
    spec: AutomationSpec
    next_run_at: Optional[str] = None

    class Config:
        from_attributes = True


class ResultOut(BaseModel):
    product: Optional[str]
    price: Optional[float]
    currency: Optional[str]
    availability: Optional[str]
    seller: Optional[str]
    url: Optional[str]
    valid: bool
    validation_errors: Optional[list[str]] = None


class RunOut(BaseModel):
    id: str
    status: str
    started_at: str
    finished_at: Optional[str] = None
    sources_found: Optional[list[str]] = None
    pages_retrieved: Optional[list[str]] = None
    error: Optional[str] = None
    results: list[ResultOut] = []

from typing import Any, Optional
from pydantic import BaseModel, Field
from core.models.enums import Frequency


class ExtractionField(BaseModel):
    """Definition of a single field to extract dynamically from web pages."""
    name: str = Field(..., description="Field identifier e.g. 'title', 'price', 'salary'")
    type: str = Field(default="string", description="Type: 'string', 'number', 'boolean', 'array', 'object'")
    description: str = Field(default="", description="Description of what to extract for this field")
    required: bool = Field(default=False, description="Whether this field must be present for a valid record")
    enum_values: Optional[list[str]] = Field(default=None, description="Allowed values if categorical")


class DynamicExtractionSchema(BaseModel):
    """Dynamic schema produced by the Goal Interpreter tailored to the specific goal domain."""
    entity_name: str = Field(default="item", description="Entity name e.g. 'product', 'job_listing', 'flight', 'article'")
    fields: list[ExtractionField] = Field(default_factory=list)
    description: Optional[str] = None

    def to_json_schema(self) -> dict[str, Any]:
        """Convert dynamic fields into a standard JSON Schema representation for LLM structured output."""
        properties = {}
        required = []
        for f in self.fields:
            prop: dict[str, Any] = {"type": f.type if f.type != "number" else ["number", "null"]}
            if f.description:
                prop["description"] = f.description
            if f.enum_values:
                prop["enum"] = f.enum_values
            properties[f.name] = prop
            if f.required:
                required.append(f.name)

        return {
            "type": "object",
            "properties": properties,
            "required": required,
        }


class ExecutionPlan(BaseModel):
    """The complete domain-agnostic execution plan produced by the Goal Interpreter."""
    objective: str = Field(..., description="Concise summary of the goal")
    domain: str = Field(default="general", description="Identified domain: e.g. 'ecommerce', 'jobs', 'real_estate', 'travel', 'news', 'finance'")
    search_query: str = Field(..., description="Optimized search query to find candidate sources")
    source_hints: list[str] = Field(default_factory=list, description="Target domain hints or specific URLs requested by user (empty for open web)")
    geography: Optional[str] = Field(default=None, description="Target country or location (e.g. 'Nigeria', 'United States', 'Global')")
    country_code: Optional[str] = Field(default=None, description="2-letter ISO country code for proxy routing if applicable (e.g. 'ng', 'us')")
    extraction_schema: DynamicExtractionSchema = Field(default_factory=DynamicExtractionSchema)
    frequency: Frequency = Field(default=Frequency.once)
    schedule_time: Optional[str] = Field(default=None, description="Preferred execution time e.g. '08:00'")
    timezone: str = Field(default="UTC", description="Timezone name e.g. 'Africa/Lagos', 'UTC'")
    condition: Optional[str] = Field(default=None, description="Alert or filter condition e.g. 'min(price) < 400000' or 'salary >= 120000'")
    notification_channel: Optional[str] = Field(default=None, description="Notification target e.g. 'webhook', 'email', 'log'")

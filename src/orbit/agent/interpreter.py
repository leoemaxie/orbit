from orbit.llm.openrouter import OpenRouterLLMClient
from orbit.llm.prompts import GOAL_INTERPRETER_PROMPT
from orbit.models.execution_plan import (
    DynamicExtractionSchema,
    ExecutionPlan,
    ExtractionField,
)


class GoalInterpreter:
    """Interprets natural language goals into structured domain-agnostic ExecutionPlans."""

    def __init__(self, llm_client: OpenRouterLLMClient | None = None):
        self.llm = llm_client or OpenRouterLLMClient()

    async def interpret(self, goal: str) -> ExecutionPlan:
        raw = await self.llm.call_json(
            system_prompt=GOAL_INTERPRETER_PROMPT,
            user_prompt=f"USER GOAL: {goal}",
            temperature=0.0,
        )

        # Parse dynamic extraction schema
        schema_raw = raw.get("extraction_schema", {})
        fields = [
            ExtractionField(
                name=f.get("name"),
                type=f.get("type", "string"),
                description=f.get("description", ""),
                required=f.get("required", False),
                enum_values=f.get("enum_values"),
            )
            for f in schema_raw.get("fields", [])
            if f.get("name")
        ]

        # Ensure a fallback identifier field exists if LLM didn't define any
        if not fields:
            fields = [
                ExtractionField(name="title", type="string", description="Name or title of the item", required=True),
                ExtractionField(name="details", type="string", description="Key details or metrics", required=False),
            ]

        dynamic_schema = DynamicExtractionSchema(
            entity_name=schema_raw.get("entity_name", "item"),
            description=schema_raw.get("description"),
            fields=fields,
        )

        return ExecutionPlan(
            objective=raw.get("objective", goal),
            domain=raw.get("domain", "general"),
            search_query=raw.get("search_query", goal),
            source_hints=raw.get("source_hints", []),
            geography=raw.get("geography"),
            country_code=raw.get("country_code"),
            extraction_schema=dynamic_schema,
            frequency=raw.get("frequency", "once"),
            schedule_time=raw.get("schedule_time"),
            timezone=raw.get("timezone", "UTC"),
            condition=raw.get("condition"),
            notification_channel=raw.get("notification_channel"),
        )

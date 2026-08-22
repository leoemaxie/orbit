import json
from typing import Any
from core.llm.openrouter import OpenRouterLLMClient
from core.llm.prompts import DYNAMIC_EXTRACTION_PROMPT
from core.models.execution_plan import ExecutionPlan


class LLMExtractor:
    """Schema-driven LLM extraction that adapts to any entity schema."""

    llm: OpenRouterLLMClient

    def __init__(self, llm_client: OpenRouterLLMClient | None = None):
        self.llm = llm_client or OpenRouterLLMClient()

    async def extract(
        self, url: str, content: str, plan: ExecutionPlan
    ) -> dict[str, Any]:
        if not content or not content.strip():
            return {"url": url, "extracted": False, "data": {}, "notes": "Empty content"}

        # Token cost safeguard: trim markdown content
        trimmed_content = content[:18000]

        schema_json = json.dumps(plan.extraction_schema.to_json_schema(), indent=2)

        user_prompt = (
            f"TARGET URL: {url}\n\n"
            f"TARGET ENTITY: {plan.extraction_schema.entity_name}\n\n"
            f"EXPECTED EXTRACTION SCHEMA:\n{schema_json}\n\n"
            f"PAGE CONTENT (markdown):\n{trimmed_content}"
        )

        try:
            raw = await self.llm.call_json(
                system_prompt=DYNAMIC_EXTRACTION_PROMPT,
                user_prompt=user_prompt,
                temperature=0.0,
            )
            data = raw.get("data", {})
            extracted = raw.get("extracted", True)
            return {
                "url": url,
                "extracted": extracted,
                "data": data,
                "notes": raw.get("notes"),
            }
        except Exception as e:
            return {
                "url": url,
                "extracted": False,
                "data": {},
                "notes": f"Extraction error: {str(e)}",
            }

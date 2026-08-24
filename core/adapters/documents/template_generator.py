import json
import logging
from typing import Any
import httpx

from core.config.settings import get_settings

logger = logging.getLogger("core.adapters.documents.template_generator")


class TemplateDossierGenerator:
    """Template merging client for structured document population."""

    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        settings = get_settings()
        self.api_key = api_key or settings.document_generator_api_key
        self.base_url = (base_url or settings.document_generator_base_url).rstrip("/")

    async def generate_dossier(
        self,
        automation_id: str,
        run_id: str,
        records: list[dict[str, Any]],
        plan_summary: str | None = None,
        template_id: str | None = None,
    ) -> bytes:
        """Merges extracted records into a document template."""
        data_payload = {
            "automation_id": automation_id,
            "run_id": run_id,
            "summary": plan_summary or "Orbit Data Briefing",
            "record_count": len(records),
            "records": [r.get("data", {}) for r in records],
        }

        if not self.api_key:
            return json.dumps(data_payload, indent=2).encode("utf-8")

        url = f"{self.base_url}/generation/merge-template"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        body = {
            "template_id": template_id or "default-executive-brief",
            "data": data_payload,
            "output_format": "pdf",
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(url, headers=headers, json=body)
                res.raise_for_status()
                return res.content
        except Exception as e:
            logger.warning(f"Template merging failed: {e}. Falling back to raw JSON.")
            return json.dumps(data_payload).encode("utf-8")

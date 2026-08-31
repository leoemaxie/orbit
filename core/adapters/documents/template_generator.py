import json
import logging
from typing import Any
import httpx

from core.config.settings import get_settings

logger = logging.getLogger("core.adapters.documents.template_generator")


class TemplateDossierGenerator:
    """Enterprise template merging client for populating Word/PDF templates."""

    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        settings = get_settings()
        self.api_key = api_key or settings.document_template_api_key
        self.base_url = (base_url or settings.document_template_base_url).rstrip("/")

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

        # Support both Doctavian (/v1/documents/...) and generic REST template endpoints
        url = f"{self.base_url}/documents/document/generate" if not self.base_url.endswith("/generate") else self.base_url
        headers = {
            "X-Api-Key": self.api_key,
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        body = {
            "externalContext": {"id": f"orbit-{run_id[:8]}"},
            "template": {
                "name": f"{template_id or 'briefing'}.docx",
                "urn": template_id or "default-executive-brief",
                "fileFormat": "docx",
                "loadMethod": "Storage",
            },
            "data": {
                "loadMethod": "Inline",
                "payload": data_payload,
            },
            "document": {
                "name": f"orbit_briefing_{run_id[:8]}",
                "fileFormat": "pdf",
                "deliveryMethod": "Direct",
            },
        }

        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                res = await client.post(url, headers=headers, json=body)
                if res.status_code in (200, 201):
                    # Direct binary response or download link
                    if res.headers.get("content-type", "").startswith("application/pdf"):
                        return res.content
                    data = res.json()
                    download_url = data.get("downloadUrl") or data.get("result", {}).get("downloadUrl")
                    if download_url:
                        dl_res = await client.get(download_url, headers=headers)
                        dl_res.raise_for_status()
                        return dl_res.content
                res.raise_for_status()
                return res.content
        except Exception as e:
            logger.warning(f"Template merging failed: {e}. Falling back to raw structured JSON.")
            return json.dumps(data_payload, indent=2).encode("utf-8")

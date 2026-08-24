import json
import logging
from typing import Any
import httpx

from core.config.settings import get_settings

logger = logging.getLogger("core.adapters.documents.html_generator")


class HtmlDossierGenerator:
    """HTML/CSS rendering client for high-fidelity dossier generation."""

    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        settings = get_settings()
        self.api_key = api_key or settings.document_generator_api_key
        self.base_url = (base_url or settings.document_generator_base_url).rstrip("/")

    def _build_html_template(
        self, automation_id: str, run_id: str, records: list[dict[str, Any]], plan_summary: str | None
    ) -> str:
        rows = "".join(
            f"<tr><td>{i+1}</td><td>{r.get('url', 'N/A')}</td><td><code>{json.dumps(r.get('data', {}))}</code></td></tr>"
            for i, r in enumerate(records)
        )
        return f"""<!DOCTYPE html>
<html>
<head><meta charset='utf-8'><title>Orbit Dossier {run_id[:8]}</title>
<style>
body {{ font-family: monospace; padding: 24px; color: #1e293b; background: #f8fafc; }}
h1 {{ color: #0f172a; border-bottom: 2px solid #06b6d4; padding-bottom: 8px; }}
table {{ width: 100%; border-collapse: collapse; margin-top: 16px; font-size: 11px; }}
th, td {{ border: 1px solid #cbd5e1; padding: 6px 10px; text-align: left; }}
th {{ background: #e2e8f0; }}
</style></head>
<body>
<h1>Orbit Mission Intelligence Dossier</h1>
<p><strong>Mission:</strong> {automation_id} | <strong>Run:</strong> {run_id}</p>
<p><strong>Objective:</strong> {plan_summary or 'Autonomous Data Extraction'}</p>
<p><strong>Validated Records:</strong> {len(records)}</p>
<table><thead><tr><th>#</th><th>Source URL</th><th>Extracted Payload</th></tr></thead>
<tbody>{rows}</tbody></table>
</body></html>"""

    async def generate_dossier(
        self,
        automation_id: str,
        run_id: str,
        records: list[dict[str, Any]],
        plan_summary: str | None = None,
        template_id: str | None = None,
    ) -> bytes:
        html = self._build_html_template(automation_id, run_id, records, plan_summary)
        if not self.api_key:
            return html.encode("utf-8")

        url = f"{self.base_url}/render/html-to-pdf"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {"html": html, "pdf_options": {"page_size": "A4", "margin": "10mm"}}

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(url, headers=headers, json=payload)
                res.raise_for_status()
                return res.content
        except Exception as e:
            logger.warning(f"HTML-to-PDF generation failed: {e}. Falling back to HTML bytes.")
            return html.encode("utf-8")

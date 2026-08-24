import json
import logging
from typing import Any

logger = logging.getLogger("core.adapters.documents.text_generator")


class TextDossierGenerator:
    """Local text and markdown dossier generator for offline environments."""

    async def generate_dossier(
        self,
        automation_id: str,
        run_id: str,
        records: list[dict[str, Any]],
        plan_summary: str | None = None,
        template_id: str | None = None,
    ) -> bytes:
        """Generates a markdown briefing from validated records."""
        header = "# Orbit Intelligence Dossier\n\n"
        header += f"- **Mission ID**: `{automation_id}`\n"
        header += f"- **Run ID**: `{run_id}`\n"
        header += f"- **Objective**: {plan_summary or 'Autonomous Extraction'}\n"
        header += f"- **Total Records**: {len(records)}\n\n"
        header += "## Extracted Data Records\n\n"

        rows = []
        for i, r in enumerate(records):
            rows.append(
                f"### Record {i+1}\n- **Source**: {r.get('url', 'N/A')}\n- **Data**: ```json\n{json.dumps(r.get('data', {}), indent=2)}\n```\n"
            )

        dossier = header + "\n".join(rows)
        return dossier.encode("utf-8")

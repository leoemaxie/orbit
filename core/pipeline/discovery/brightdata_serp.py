import re

import httpx

from core.config.settings import get_settings
from core.models.execution_plan import ExecutionPlan


class BrightDataSerpDiscovery:
    """Discovery strategy using Bright Data SERP API endpoint."""

    def __init__(self):
        self.settings = get_settings()

    async def discover(self, plan: ExecutionPlan, max_results: int = 10) -> list[str]:
        if not self.settings.brightdata_api_key or not self.settings.brightdata_zone:
            return []

        query = plan.search_query.strip()
        if plan.source_hints:
            site_filters = " OR ".join(f"site:{d.strip()}" for d in plan.source_hints if d.strip())
            if site_filters:
                query = f"{query} ({site_filters})"

        # Google search via Bright Data Web Unlocker/SERP API
        search_url = f"https://www.google.com/search?q={query}&num={max_results}"

        headers = {
            "Authorization": f"Bearer {self.settings.brightdata_api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "zone": self.settings.brightdata_zone,
            "url": search_url,
            "format": "raw",
            "data_format": "markdown",
        }
        if plan.country_code:
            payload["country"] = plan.country_code.lower()

        request_url = f"{self.settings.brightdata_base_url}/request"

        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                resp = await client.post(request_url, headers=headers, json=payload)
                if resp.status_code != 200:
                    return []

                # Extract markdown links
                links = re.findall(r'\[.*?\]\((https?://[^\s\)]+)\)', resp.text)
                clean_links = [
                    l for l in links
                    if not any(ex in l for ex in ["google.com", "gstatic.com", "schema.org", "youtube.com"])
                ]

                seen = set()
                deduped: list[str] = []
                for l in clean_links:
                    if l not in seen:
                        seen.add(l)
                        deduped.append(l)

                return deduped[:max_results]
        except Exception:  # noqa: BLE001
            return []

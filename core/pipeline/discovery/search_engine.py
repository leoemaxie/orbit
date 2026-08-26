import httpx

from core.config.settings import get_settings
from core.models.execution_plan import ExecutionPlan


class SearchEngineDiscovery:
    """Domain-agnostic web source discovery using search engine API (SerpApi / Google)."""

    SEARCH_ENGINE_URL = "https://serpapi.com/search.json"

    def __init__(self):
        self.settings = get_settings()

    async def discover(self, plan: ExecutionPlan, max_results: int = 10) -> list[str]:
        if not self.settings.search_engine_api_key:
            raise ValueError("SEARCH_ENGINE_API_KEY (or SERPAPI_API_KEY) is not configured in settings or environment.")

        query = plan.search_query.strip()

        params: dict[str, str | int] = {
            "engine": "google",
            "q": query,
            "num": max_results * 2,
            "api_key": self.settings.search_engine_api_key,
        }

        if plan.country_code:
            params["gl"] = plan.country_code.lower()
            params["hl"] = "en"

        endpoint = self.settings.search_engine_base_url or self.SEARCH_ENGINE_URL

        try:
            async with httpx.AsyncClient(timeout=35.0) as client:
                resp = await client.get(endpoint, params=params)
                resp.raise_for_status()
                data = resp.json()
        except httpx.HTTPError as err:
            resp_err = getattr(err, "response", None)
            status = resp_err.status_code if resp_err is not None else None
            raise RuntimeError(f"Search API request failed (status: HTTP {status or 'error'})") from None

        raw_links: list[str] = []
        for item in data.get("organic_results", []):
            link = item.get("link")
            if link and link.startswith("http"):
                raw_links.append(link)

        # Prioritize source hints if present, but retain other organic results
        prioritized: list[str] = []
        other_links: list[str] = []

        for link in raw_links:
            if plan.source_hints and any(domain.lower() in link.lower() for domain in plan.source_hints if domain):
                prioritized.append(link)
            else:
                other_links.append(link)

        combined = prioritized + other_links

        # Deduplicate preserving order
        seen = set()
        deduped: list[str] = []
        for u in combined:
            if u not in seen:
                seen.add(u)
                deduped.append(u)

        return deduped[:max_results]

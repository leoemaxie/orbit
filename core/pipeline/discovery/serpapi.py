import httpx
from core.config.settings import get_settings
from core.models.execution_plan import ExecutionPlan


class SerpApiDiscovery:
    """Domain-agnostic web source discovery using Google Search via SerpApi."""

    SERPAPI_URL = "https://serpapi.com/search.json"

    def __init__(self):
        self.settings = get_settings()

    async def discover(self, plan: ExecutionPlan, max_results: int = 10) -> list[str]:
        if not self.settings.serpapi_api_key:
            raise ValueError("SERPAPI_API_KEY is not configured in settings or environment.")

        # Build search query
        query = plan.search_query.strip()
        if plan.source_hints:
            site_filters = " OR ".join(f"site:{d.strip()}" for d in plan.source_hints if d.strip())
            if site_filters:
                query = f"{query} ({site_filters})"

        params: dict[str, str | int] = {
            "engine": "google",
            "q": query,
            "num": max_results,
            "api_key": self.settings.serpapi_api_key,
        }

        if plan.country_code:
            params["gl"] = plan.country_code.lower()
        if plan.geography:
            params["location"] = plan.geography

        async with httpx.AsyncClient(timeout=35.0) as client:
            resp = await client.get(self.SERPAPI_URL, params=params)
            resp.raise_for_status()
            data = resp.json()

        urls: list[str] = []
        for item in data.get("organic_results", []):
            link = item.get("link")
            if link and link.startswith("http"):
                # If specific source hints were requested, filter to them; otherwise accept open web link
                if plan.source_hints:
                    if any(domain.lower() in link.lower() for domain in plan.source_hints):
                        urls.append(link)
                else:
                    urls.append(link)

        # Deduplicate preserving order
        seen = set()
        deduped: list[str] = []
        for u in urls:
            if u not in seen:
                seen.add(u)
                deduped.append(u)

        return deduped[:max_results]

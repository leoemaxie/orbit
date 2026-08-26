import re
from urllib.parse import parse_qs, unquote, urlparse

import httpx

from core.models.execution_plan import ExecutionPlan
from core.pipeline.discovery.source_resolver import (
    build_scoped_search_query,
    filter_urls_by_sources,
)


class OpenWebSearchDiscovery:
    """
    Zero-API-key open-web discovery using HTML search.
    Enables Orbit to discover sources without any paid search API key.
    """

    SEARCH_ENDPOINT = "https://html.duckduckgo.com/html/"

    async def discover(self, plan: ExecutionPlan, max_results: int = 10) -> list[str]:
        query = build_scoped_search_query(plan.search_query, plan.source_hints)

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }

        data = {"q": query, "b": ""}

        raw_urls: list[str] = []
        try:
            async with httpx.AsyncClient(timeout=25.0, follow_redirects=True) as client:
                resp = await client.post(self.SEARCH_ENDPOINT, data=data, headers=headers)
                if resp.status_code != 200:
                    return []

                html = resp.text
                # Extract links from result tags: href="//duckduckgo.com/l/?uddg=... or regular hrefs
                raw_links = re.findall(r'class="result__url"[^>]*href="([^"]+)"', html)
                if not raw_links:
                    raw_links = re.findall(r'href="([^"]*uddg=[^"]+)"', html)

                for link in raw_links:
                    actual_url = self._clean_search_url(link)
                    if (
                        actual_url
                        and actual_url.startswith("http")
                        and not any(excluded in actual_url for excluded in ["duckduckgo.com", "google.com/search"])
                    ):
                        raw_urls.append(actual_url)
        except Exception:  # noqa: BLE001
            return []

        # Deduplicate preserving order
        seen = set()
        deduped: list[str] = []
        for u in raw_urls:
            if u not in seen:
                seen.add(u)
                deduped.append(u)

        # If user explicitly requested specific sources/domains, strictly enforce matching links only
        if plan.source_hints:
            filtered = filter_urls_by_sources(deduped, plan.source_hints)
            return filtered[:max_results]

        return deduped[:max_results]


    def _clean_search_url(self, link: str) -> str | None:
        """Extracts and unquotes the direct target URL from search engine redirect links."""
        if "uddg=" in link:
            parsed = urlparse(link)
            params = parse_qs(parsed.query)
            uddg = params.get("uddg")
            if uddg:
                return unquote(uddg[0])

        if link.startswith("//"):
            return "https:" + link

        if link.startswith("/"):
            return None

        return link

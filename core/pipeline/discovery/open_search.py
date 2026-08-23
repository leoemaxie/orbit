import re
from urllib.parse import parse_qs, unquote, urlparse

import httpx

from core.models.execution_plan import ExecutionPlan


class OpenWebSearchDiscovery:
    """
    Zero-API-key open-web discovery using HTML search.
    Enables Orbit to discover sources without any paid search API key.
    """

    SEARCH_ENDPOINT = "https://html.duckduckgo.com/html/"

    async def discover(self, plan: ExecutionPlan, max_results: int = 10) -> list[str]:
        query = plan.search_query.strip()
        if plan.source_hints:
            site_filters = " OR ".join(f"site:{d.strip()}" for d in plan.source_hints if d.strip())
            if site_filters:
                query = f"{query} ({site_filters})"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }

        data = {"q": query, "b": ""}

        urls: list[str] = []
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
                        if plan.source_hints:
                            if any(domain.lower() in actual_url.lower() for domain in plan.source_hints):
                                urls.append(actual_url)
                        else:
                            urls.append(actual_url)
        except Exception:  # noqa: BLE001
            return []

        # Deduplicate preserving order
        seen = set()
        deduped: list[str] = []
        for u in urls:
            if u not in seen:
                seen.add(u)
                deduped.append(u)

        return deduped[:max_results]

    def _clean_search_url(self, link: str) -> str:
        if "uddg=" in link:
            parsed = urlparse(link)
            qs = parse_qs(parsed.query)
            if "uddg" in qs:
                return unquote(qs["uddg"][0])
        if link.startswith("//"):
            return "https:" + link
        return link

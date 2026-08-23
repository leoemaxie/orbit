import asyncio

import httpx

from core.config.settings import get_settings


class ProxyRetrieval:
    """Resilient proxy and unlocker-based page retrieval (returns clean markdown)."""

    def __init__(self):
        self.settings = get_settings()

    async def retrieve_one(self, url: str, country_code: str | None = None) -> str | None:
        if not self.settings.retrieval_api_key or not self.settings.retrieval_zone:
            raise ValueError("RETRIEVAL_API_KEY (or BRIGHTDATA_API_KEY) or RETRIEVAL_ZONE is not configured.")

        headers = {
            "Authorization": f"Bearer {self.settings.retrieval_api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "zone": self.settings.retrieval_zone,
            "url": url,
            "format": "raw",
            "data_format": "markdown",
        }

        if country_code:
            payload["country"] = country_code.lower()

        request_url = f"{self.settings.retrieval_base_url}/request"

        async with httpx.AsyncClient(timeout=75.0) as client:
            resp = await client.post(request_url, headers=headers, json=payload)
            resp.raise_for_status()
            return resp.text

    async def retrieve_many(
        self, urls: list[str], country_code: str | None = None, concurrency: int = 5
    ) -> dict[str, str | None]:
        """Concurrent retrieval with a semaphore to avoid hitting rate limits."""
        semaphore = asyncio.Semaphore(concurrency)
        results: dict[str, str | None] = {}

        async def fetch(u: str):
            async with semaphore:
                try:
                    content = await self.retrieve_one(u, country_code=country_code)
                    results[u] = content
                except Exception:  # noqa: BLE001
                    results[u] = None

        await asyncio.gather(*(fetch(u) for u in urls))
        return results

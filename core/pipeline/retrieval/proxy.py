import asyncio

import httpx

from core.config.settings import get_settings
from core.pipeline.retrieval.direct import DirectHttpRetrieval


class ProxyRetrieval:
    """Resilient proxy and unlocker-based page retrieval with automatic direct HTTP fallback."""

    def __init__(self):
        self.settings = get_settings()
        self.direct_fallback = DirectHttpRetrieval()

    async def retrieve_one(self, url: str, country_code: str | None = None) -> str | None:
        if self.settings.retrieval_api_key and self.settings.retrieval_zone:
            try:
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

                async with httpx.AsyncClient(timeout=45.0) as client:
                    resp = await client.post(request_url, headers=headers, json=payload)
                    if resp.status_code == 200 and resp.text:
                        return resp.text
            except Exception:  # noqa: BLE001
                pass

        # Automatic resilient fallback to Direct HTTP retrieval
        return await self.direct_fallback.retrieve_one(url, country_code=country_code)

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

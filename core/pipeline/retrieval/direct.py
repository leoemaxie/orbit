import asyncio

import httpx


class DirectHttpRetrieval:
    """Direct HTTP retrieval fallback for public/open endpoints."""

    async def retrieve_one(self, url: str, country_code: str | None = None) -> str | None:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            return resp.text

    async def retrieve_many(
        self, urls: list[str], country_code: str | None = None, concurrency: int = 5
    ) -> dict[str, str | None]:
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

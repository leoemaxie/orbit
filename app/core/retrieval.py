import httpx

from app.core.config import get_settings

settings = get_settings()

BRIGHTDATA_REQUEST_URL = f"{settings.brightdata_base_url}/request"


async def retrieve_page(url: str, country: str = "ng") -> str:
    """
    Fetches a page through Bright Data's Web Unlocker API and returns it as
    markdown (clean text, good for LLM extraction, low token cost vs raw HTML).
    Raises on failure — caller decides whether to retry.
    """
    headers = {
        "Authorization": f"Bearer {settings.brightdata_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "zone": settings.brightdata_zone,
        "url": url,
        "format": "raw",
        "data_format": "markdown",
        "country": country,
    }

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(BRIGHTDATA_REQUEST_URL, headers=headers, json=payload)
        resp.raise_for_status()
        return resp.text


async def retrieve_pages(urls: list[str], country: str = "ng") -> dict[str, str | None]:
    """
    Retrieves multiple pages. Returns {url: markdown_or_None}.
    A None value means retrieval failed for that URL (caller handles recovery).
    """
    results: dict[str, str | None] = {}
    for url in urls:
        try:
            results[url] = await retrieve_page(url, country=country)
        except Exception:
            results[url] = None
    return results

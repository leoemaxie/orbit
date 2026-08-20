import httpx

from app.core.config import get_settings

settings = get_settings()

SERPAPI_URL = "https://serpapi.com/search.json"


async def discover_sources(product_query: str, geography: str = "Nigeria", max_results: int = 8) -> list[str]:
    """
    Uses SerpApi to find candidate product detail page URLs, restricted to the
    Phase-1 allowed retailer domains.
    Returns a de-duplicated list of URLs.
    """
    allowed = settings.allowed_retailer_list
    site_filter = " OR ".join(f"site:{d}" for d in allowed)
    query = f"{product_query} price {geography} ({site_filter})"

    params = {
        "engine": "google",
        "q": query,
        "num": max_results,
        "api_key": settings.serpapi_api_key,
    }

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(SERPAPI_URL, params=params)
        resp.raise_for_status()
        data = resp.json()

    urls = []
    for item in data.get("organic_results", []):
        link = item.get("link")
        if link and any(domain in link for domain in allowed):
            urls.append(link)

    # de-dupe, preserve order
    seen = set()
    deduped = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            deduped.append(u)

    return deduped[:max_results]

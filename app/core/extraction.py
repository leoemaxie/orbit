from app.core.llm import call_llm_json

SYSTEM_PROMPT = """You are the Extraction module for Orbit, an autonomous web-data agent.

You will be given the markdown content of a product detail page and a list of required fields.
Extract EXACTLY these fields as a JSON object:

{
  "product": "the product name/title as shown on the page, or null",
  "price": <number, no currency symbols or commas, or null if not found>,
  "currency": "3-letter code e.g. NGN, or null",
  "availability": "in_stock" | "out_of_stock" | "unknown",
  "seller": "seller or store name shown on the page, or null"
}

Rules:
- Output ONLY the JSON object.
- If the page clearly is not a product detail page (e.g. a search results list, 404, captcha wall), set all fields to null and availability to "unknown".
- Do not guess a price from unrelated numbers on the page (SKUs, ratings, review counts).
- Prefer the primary/main product price, not a strikethrough original price if a discounted price is shown (in that case use the discounted price).
"""


async def extract_fields(url: str, page_markdown: str) -> dict:
    if not page_markdown:
        return {"product": None, "price": None, "currency": None, "availability": "unknown", "seller": None}

    # Trim to keep token cost sane; PDPs rarely need more than this to extract price/availability.
    trimmed = page_markdown[:15000]

    user_prompt = f"URL: {url}\n\nPAGE CONTENT (markdown):\n{trimmed}"
    raw = await call_llm_json(SYSTEM_PROMPT, user_prompt)

    return {
        "product": raw.get("product"),
        "price": raw.get("price"),
        "currency": raw.get("currency"),
        "availability": raw.get("availability", "unknown"),
        "seller": raw.get("seller"),
        "url": url,
    }

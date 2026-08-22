import json
import re
from typing import Any
import httpx
from core.config.settings import get_settings

_JSON_FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.MULTILINE)


def strip_json_fences(text: str) -> str:
    """Removes markdown code fences from LLM responses."""
    return _JSON_FENCE_RE.sub("", text).strip()


class OpenRouterLLMClient:
    """OpenRouter API client supporting JSON outputs and structured completions."""

    def __init__(self):
        self.settings = get_settings()

    async def call_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.0,
        schema: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if not self.settings.openrouter_api_key:
            raise ValueError("OPENROUTER_API_KEY is not configured in settings or environment.")

        payload: dict[str, Any] = {
            "model": self.settings.openrouter_model,
            "temperature": temperature,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "response_format": {"type": "json_object"},
        }

        headers = {
            "Authorization": f"Bearer {self.settings.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/leoemaxie/orbit",
            "X-Title": "Orbit Web Data Agent",
        }

        async with httpx.AsyncClient(timeout=90.0) as client:
            resp = await client.post(
                f"{self.settings.openrouter_base_url}/chat/completions",
                headers=headers,
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()

        choices = data.get("choices", [])
        if not choices:
            raise ValueError(f"OpenRouter returned no choices in response: {data}")

        content = choices[0]["message"]["content"]
        cleaned = strip_json_fences(content)

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            # Fallback: attempt to find first '{' and last '}'
            start = cleaned.find("{")
            end = cleaned.rfind("}")
            if start != -1 and end != -1:
                try:
                    return json.loads(cleaned[start : end + 1])
                except json.JSONDecodeError:
                    pass
            raise ValueError(f"LLM did not return valid JSON: {e}\nRaw output: {content[:400]}")

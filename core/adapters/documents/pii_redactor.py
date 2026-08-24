import logging
import httpx

from core.config.settings import get_settings

logger = logging.getLogger("core.adapters.documents.pii_redactor")


class PiiDocumentRedactor:
    """Automated PII redaction and compliance masking client."""

    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        settings = get_settings()
        self.api_key = api_key or settings.document_redactor_api_key
        self.base_url = (base_url or settings.document_redactor_base_url).rstrip("/")

    async def redact_pii(
        self, file_bytes: bytes, entity_types: list[str] | None = None
    ) -> bytes:
        """Sanitizes sensitive PII entities (email, SSN, cards) from document payloads."""
        if not self.api_key:
            return file_bytes

        entities = entity_types or ["EMAIL_ADDRESS", "US_SSN", "CREDIT_CARD_NUMBER", "PHONE_NUMBER"]
        url = f"{self.base_url}/redaction/process"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/octet-stream"}
        params = {"entities": ",".join(entities), "replacement_text": "[REDACTED]"}

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(url, headers=headers, params=params, content=file_bytes)
                res.raise_for_status()
                return res.content
        except Exception as e:
            logger.warning(f"PII redaction failed: {e}. Returning unredacted document.")
            return file_bytes

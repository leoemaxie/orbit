import asyncio
import hashlib
import hmac
import json
import logging
import time
import uuid
from typing import Any
import httpx

from core.config.settings import get_settings

logger = logging.getLogger("core.adapters.communication.webhook")


class SignedWebhookAdapter:
    """Dispatches HMAC-SHA256 signed outbound webhooks with exponential backoff retries."""

    def __init__(self, webhook_url: str | None = None, signing_secret: str | None = None, max_retries: int = 3):
        settings = get_settings()
        self.webhook_url = webhook_url or settings.default_webhook_url or ""
        self.signing_secret = signing_secret or getattr(settings, "webhook_signing_secret", "orbit-webhook-secret-key")
        self.max_retries = max_retries

    def _sign_payload(self, timestamp: int, payload_json: str) -> str:
        """Generates standard HMAC-SHA256 signature in v1={hash} format."""
        signature_payload = f"t={timestamp}.{payload_json}".encode("utf-8")
        computed = hmac.new(self.signing_secret.encode("utf-8"), signature_payload, hashlib.sha256).hexdigest()
        return f"t={timestamp},v1={computed}"

    async def send_event(self, event_type: str, data: dict[str, Any]) -> bool:
        """Sends an event payload with X-Orbit-Signature and retry policy."""
        if not self.webhook_url:
            return False

        timestamp = int(time.time())
        delivery_id = str(uuid.uuid4())
        body_dict = {"event": event_type, "timestamp": timestamp, "delivery_id": delivery_id, "data": data}
        body_json = json.dumps(body_dict, default=str)
        signature = self._sign_payload(timestamp, body_json)

        headers = {
            "Content-Type": "application/json",
            "X-Orbit-Signature": signature,
            "X-Orbit-Timestamp": str(timestamp),
            "X-Orbit-Event": event_type,
            "X-Orbit-Delivery-Id": delivery_id,
            "User-Agent": "Orbit-Webhook-Emitter/1.0",
        }

        for attempt in range(1, self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.post(self.webhook_url, headers=headers, content=body_json)
                    if resp.status_code in (200, 201, 202, 204):
                        return True
                    logger.warning(f"Webhook delivery attempt {attempt} returned HTTP {resp.status_code}")
            except Exception as e:
                logger.warning(f"Webhook delivery attempt {attempt} failed: {e}")

            if attempt < self.max_retries:
                await asyncio.sleep(0.3 * (2 ** (attempt - 1)))

        return False

    async def send_alert(self, title: str, message: str, payload: dict[str, Any] | None = None, dossier_url: str | None = None) -> bool:
        """Implements NotificationAdapter protocol using signed event emission."""
        data = {"title": title, "message": message, "payload": payload or {}, "dossier_url": dossier_url}
        return await self.send_event("alert.condition_matched", data)

    @staticmethod
    def verify_signature(payload_bytes: bytes, signature_header: str, secret: str, tolerance_sec: int = 300) -> bool:
        """Verifies signature header against secret key preventing replay attacks."""
        try:
            parts = dict(part.split("=") for part in signature_header.split(","))
            timestamp = int(parts.get("t", 0))
            received_sig = parts.get("v1", "")

            if abs(time.time() - timestamp) > tolerance_sec:
                return False

            payload_json = payload_bytes.decode("utf-8")
            signature_payload = f"t={timestamp}.{payload_json}".encode("utf-8")
            expected_sig = hmac.new(secret.encode("utf-8"), signature_payload, hashlib.sha256).hexdigest()
            return hmac.compare_digest(received_sig, expected_sig)
        except Exception:
            return False

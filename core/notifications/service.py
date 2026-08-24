import logging
from typing import Any

import httpx

from core.config.settings import get_settings

logger = logging.getLogger("core.notifications")


class NotificationService:
    """Dispatches alerts via webhook, log, or configured notification channels."""

    def __init__(self):
        self.settings = get_settings()

    async def notify(
        self,
        title: str,
        message: str,
        payload: dict[str, Any] | None = None,
        webhook_url: str | None = None,
    ) -> bool:
        target_url = webhook_url or self.settings.default_webhook_url

        # Log notification summary without raw sensitive parameters
        logger.info(f"🔔 [ORBIT ALERT] {title}: {message}")

        if not target_url:
            return True

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                body = {
                    "title": title,
                    "message": message,
                    "payload": payload or {},
                }
                resp = await client.post(target_url, json=body)
                resp.raise_for_status()
                return True
        except Exception:  # noqa: BLE001
            masked_host = target_url.split("://")[-1].split("/")[0] if "://" in target_url else "configured-webhook"
            logger.error(f"Failed to deliver webhook notification to host {masked_host}")
            return False

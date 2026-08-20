import logging
from typing import Any, Optional
import httpx
from orbit.config.settings import get_settings

logger = logging.getLogger("orbit.notifications")


class NotificationService:
    """Dispatches alerts via webhook, log, or configured notification channels."""

    def __init__(self):
        self.settings = get_settings()

    async def notify(
        self,
        title: str,
        message: str,
        payload: Optional[dict[str, Any]] = None,
        webhook_url: Optional[str] = None,
    ) -> bool:
        target_url = webhook_url or self.settings.default_webhook_url

        # Always log the notification
        logger.info(f"🔔 [ORBIT ALERT] {title}: {message} | data={payload}")

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
        except Exception as e:
            logger.error(f"Failed to deliver webhook notification to {target_url}: {e}")
            return False

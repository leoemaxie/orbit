import logging
from typing import Any

from core.adapters.communication.slack import SlackWebhookAdapter
from core.adapters.communication.webhook import SignedWebhookAdapter
from core.config.settings import get_settings

logger = logging.getLogger("core.notifications")


class NotificationService:
    """Dispatches alerts via signed webhook or Slack notification adapters."""

    def __init__(self):
        self.settings = get_settings()

    async def notify(
        self,
        title: str,
        message: str,
        payload: dict[str, Any] | None = None,
        webhook_url: str | None = None,
        dossier_url: str | None = None,
    ) -> bool:
        target_url = webhook_url or self.settings.default_webhook_url
        logger.info(f"🔔 [ORBIT ALERT] {title}: {message}")

        if not target_url:
            return True

        # Route to Slack if URL is Slack webhook
        if "hooks.slack.com" in target_url:
            slack_adapter = SlackWebhookAdapter(webhook_url=target_url)
            return await slack_adapter.send_alert(title, message, payload=payload, dossier_url=dossier_url)

        # Route to HMAC-Signed Webhook for general endpoints
        signed_adapter = SignedWebhookAdapter(webhook_url=target_url)
        return await signed_adapter.send_alert(title, message, payload=payload, dossier_url=dossier_url)

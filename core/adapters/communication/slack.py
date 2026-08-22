from typing import Any
import httpx


class SlackWebhookAdapter:
    """Dispatches alerts formatted as Slack blocks via incoming webhook."""

    webhook_url: str

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    async def send_alert(
        self, title: str, message: str, payload: dict[str, Any] | None = None
    ) -> bool:
        if not self.webhook_url:
            return False

        blocks: list[dict[str, Any]] = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": f"🛰️ {title}"},
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*{message}*"},
            },
        ]

        if payload:
            blocks.append({
                "type": "context",
                "elements": [{"type": "mrkdwn", "text": f"Payload: `{payload}`"}],
            })

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(self.webhook_url, json={"blocks": blocks})
                return resp.status_code == 200
        except Exception:
            return False

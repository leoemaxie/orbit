from typing import Any
import httpx


class SlackWebhookAdapter:
    """Dispatches alerts formatted as Slack blocks with metrics and dossier download links."""

    webhook_url: str

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    async def send_alert(
        self,
        title: str,
        message: str,
        payload: dict[str, Any] | None = None,
        dossier_url: str | None = None,
    ) -> bool:
        if not self.webhook_url:
            return False

        blocks: list[dict[str, Any]] = [
            {"type": "header", "text": {"type": "plain_text", "text": f"🛰️ {title}"}},
            {"type": "section", "text": {"type": "mrkdwn", "text": f"*{message}*"}},
        ]

        if payload:
            blocks.append({
                "type": "context",
                "elements": [{"type": "mrkdwn", "text": f"Telemetry: `{payload}`"}],
            })

        if dossier_url:
            blocks.append({
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "📄 Download Intelligence Dossier"},
                        "url": dossier_url,
                        "style": "primary",
                    }
                ],
            })

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(self.webhook_url, json={"blocks": blocks})
                return resp.status_code == 200
        except Exception:  # noqa: BLE001
            return False

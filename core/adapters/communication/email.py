import asyncio
import html
import logging
from typing import Any
import httpx

from core.config.settings import get_settings

logger = logging.getLogger("core.adapters.communication.email")


class EmailNotificationAdapter:
    """Provider-agnostic transactional email adapter supporting managed and custom delivery via HTTP gateways."""

    def __init__(
        self,
        api_key: str | None = None,
        sender_address: str | None = None,
        base_url: str | None = None,
        max_retries: int = 3,
    ):
        settings = get_settings()
        self.api_key = api_key or settings.email_api_key or ""
        self.sender_address = sender_address or settings.email_sender_address or "Orbit Alerts <alerts@orbit.dev>"
        self.base_url = base_url or settings.email_base_url or "https://api.resend.com/emails"
        self.max_retries = max_retries

    async def send_email(
        self,
        to: list[str] | str,
        subject: str,
        html_body: str,
        text_body: str | None = None,
    ) -> bool:
        """Sends an outbound transactional email with authorization headers and exponential backoff retries."""
        if not self.api_key:
            logger.warning("Email dispatch skipped: EMAIL_API_KEY is not configured.")
            return False

        recipients = [to] if isinstance(to, str) else to
        if not recipients:
            logger.warning("Email dispatch skipped: No recipient specified.")
            return False

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "Orbit-Email-Adapter/1.0",
        }

        payload: dict[str, Any] = {
            "from": self.sender_address,
            "to": recipients,
            "subject": subject,
            "html": html_body,
        }
        if text_body:
            payload["text"] = text_body

        for attempt in range(1, self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=15.0) as client:
                    resp = await client.post(self.base_url, headers=headers, json=payload)
                    if resp.status_code in (200, 201, 202):
                        logger.info(f"Email successfully delivered to {recipients} (status: HTTP {resp.status_code})")
                        return True

                    logger.warning(
                        f"Email delivery attempt {attempt} failed with HTTP {resp.status_code}: {resp.text}"
                    )
            except Exception as e:
                logger.warning(f"Email delivery attempt {attempt} encountered error: {e}")

            if attempt < self.max_retries:
                await asyncio.sleep(0.5 * (2 ** (attempt - 1)))

        logger.error(f"Email delivery failed permanently after {self.max_retries} attempts.")
        return False

    async def send_alert(
        self,
        title: str,
        message: str,
        recipient_email: str | None = None,
        payload: dict[str, Any] | None = None,
        dossier_url: str | None = None,
    ) -> bool:
        """Renders an alert template and delivers to the specified recipient (or default recipient)."""
        settings = get_settings()
        target_email = recipient_email or settings.default_recipient_email
        if not target_email:
            logger.warning("Email alert skipped: No recipient email address specified.")
            return False

        subject = f"🛰️ [Orbit Alert] {title}"
        html_content = self._render_html_template(title, message, payload=payload, dossier_url=dossier_url)
        text_content = self._render_text_template(title, message, payload=payload, dossier_url=dossier_url)

        return await self.send_email(
            to=target_email,
            subject=subject,
            html_body=html_content,
            text_body=text_content,
        )

    def _render_html_template(
        self,
        title: str,
        message: str,
        payload: dict[str, Any] | None = None,
        dossier_url: str | None = None,
    ) -> str:
        """Generates a responsive HTML email matching Orbit's modern dark theme."""
        escaped_title = html.escape(title)
        escaped_msg = html.escape(message)

        dossier_button = ""
        if dossier_url:
            dossier_button = f"""
            <div style="margin: 28px 0; text-align: center;">
                <a href="{html.escape(dossier_url)}" style="background-color: #06b6d4; color: #020617; font-weight: 600; font-size: 14px; text-decoration: none; padding: 12px 24px; border-radius: 8px; display: inline-block; box-shadow: 0 4px 12px rgba(6, 182, 212, 0.25);">
                    📄 Download Intelligence Dossier
                </a>
            </div>
            """

        telemetry_block = ""
        if payload:
            rows = ""
            for k, v in payload.items():
                if k == "dossier_url":
                    continue
                rows += f"""
                <tr>
                    <td style="padding: 8px 12px; font-family: monospace; font-size: 12px; color: #94a3b8; border-bottom: 1px solid #334155;">{html.escape(str(k))}</td>
                    <td style="padding: 8px 12px; font-family: monospace; font-size: 12px; color: #f8fafc; border-bottom: 1px solid #334155; text-align: right;">{html.escape(str(v))}</td>
                </tr>
                """
            if rows:
                telemetry_block = f"""
                <div style="margin-top: 24px; background-color: #0b1329; border: 1px solid #1e293b; border-radius: 8px; overflow: hidden;">
                    <div style="padding: 10px 14px; background-color: #0f172a; border-bottom: 1px solid #1e293b; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: #38bdf8;">
                        Mission Telemetry
                    </div>
                    <table style="width: 100%; border-collapse: collapse;">
                        {rows}
                    </table>
                </div>
                """

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{escaped_title}</title>
</head>
<body style="margin: 0; padding: 0; background-color: #020617; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #e2e8f0; line-height: 1.6;">
    <table role="presentation" style="width: 100%; border-collapse: collapse;">
        <tr>
            <td style="padding: 32px 16px; text-align: center;">
                <table role="presentation" style="max-width: 580px; width: 100%; margin: 0 auto; background-color: #090e1a; border: 1px solid #1e293b; border-radius: 12px; overflow: hidden; text-align: left; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);">
                    <!-- Header -->
                    <tr>
                        <td style="padding: 24px 32px; background-color: #0b132b; border-bottom: 1px solid #1e293b;">
                            <div style="display: flex; align-items: center; justify-content: space-between;">
                                <span style="font-size: 16px; font-weight: 700; color: #f8fafc; letter-spacing: -0.02em;">🛰️ ORBIT</span>
                                <span style="font-size: 11px; font-weight: 600; text-transform: uppercase; background-color: rgba(6, 182, 212, 0.15); color: #22d3ee; padding: 4px 10px; border-radius: 9999px; border: 1px solid rgba(6, 182, 212, 0.3);">
                                    Condition Alert
                                </span>
                            </div>
                        </td>
                    </tr>

                    <!-- Body Content -->
                    <tr>
                        <td style="padding: 32px;">
                            <h1 style="margin: 0 0 16px 0; font-size: 18px; font-weight: 600; color: #f8fafc; line-height: 1.4;">
                                {escaped_title}
                            </h1>
                            <p style="margin: 0 0 20px 0; font-size: 14px; color: #cbd5e1; line-height: 1.6; background-color: #0f172a; border-left: 3px solid #06b6d4; padding: 14px 16px; border-radius: 4px;">
                                {escaped_msg}
                            </p>

                            {dossier_button}
                            {telemetry_block}
                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td style="padding: 20px 32px; background-color: #050b14; border-top: 1px solid #1e293b; font-size: 12px; color: #64748b; text-align: center;">
                            Automated notification dispatched by Orbit Autonomous Data Operations.<br>
                            To adjust trigger conditions or sinks, configure your mission parameters in Orbit.
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""

    def _render_text_template(
        self,
        title: str,
        message: str,
        payload: dict[str, Any] | None = None,
        dossier_url: str | None = None,
    ) -> str:
        """Generates plain text alternative for fallback email clients."""
        text = f"🛰️ ORBIT ALERT: {title}\n\n"
        text += f"{message}\n\n"
        if dossier_url:
            text += f"Download Intelligence Dossier:\n{dossier_url}\n\n"
        if payload:
            text += "Telemetry:\n"
            for k, v in payload.items():
                if k != "dossier_url":
                    text += f"- {k}: {v}\n"
        text += "\n---\nOrbit Autonomous Data Operations"
        return text

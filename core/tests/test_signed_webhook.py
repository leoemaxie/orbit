import time
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from core.adapters.communication.webhook import SignedWebhookAdapter


def test_sign_and_verify_signature():
    secret = "test-orbit-secret-key-12345"
    adapter = SignedWebhookAdapter(webhook_url="https://api.external.com/webhook", signing_secret=secret)

    payload_json = '{"event":"run.completed","data":{"records_count":5}}'
    payload_bytes = payload_json.encode("utf-8")
    timestamp = int(time.time())

    signature_header = adapter._sign_payload(timestamp, payload_json)
    assert signature_header.startswith(f"t={timestamp},v1=")

    # Verification passes
    valid = SignedWebhookAdapter.verify_signature(payload_bytes, signature_header, secret)
    assert valid is True

    # Tampered payload fails
    tampered_bytes = '{"event":"run.completed","data":{"records_count":999}}'.encode("utf-8")
    assert SignedWebhookAdapter.verify_signature(tampered_bytes, signature_header, secret) is False

    # Wrong secret fails
    assert SignedWebhookAdapter.verify_signature(payload_bytes, signature_header, "wrong-secret") is False


@pytest.mark.asyncio
async def test_signed_webhook_send_event_success():
    adapter = SignedWebhookAdapter(webhook_url="https://api.example.com/webhook", signing_secret="secret")

    mock_resp = MagicMock(status_code=200)
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp

        success = await adapter.send_event("run.completed", {"automation_id": "auto-1", "records": 10})
        assert success is True
        assert mock_post.called

        headers = mock_post.call_args.kwargs["headers"]
        assert "X-Orbit-Signature" in headers
        assert "X-Orbit-Timestamp" in headers
        assert headers["X-Orbit-Event"] == "run.completed"
        assert "X-Orbit-Delivery-Id" in headers

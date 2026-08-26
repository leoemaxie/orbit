import pytest
from core.services.workflow_service import WorkflowService


def test_get_adapter_topology_modes():
    topology = WorkflowService.get_adapter_topology()
    assert len(topology) >= 7

    modes = {node["id"]: node.get("mode") for node in topology}
    # Check that 3 distinct modes exist
    assert "managed" in [node.get("mode") for node in topology]
    assert "both" in [node.get("mode") for node in topology]
    assert "custom" in [node.get("mode") for node in topology]

    # Verify Docling parser is managed
    doc_node = next(n for n in topology if n["label"] == "Document & Table Parser")
    assert doc_node["mode"] == "managed"

    # Verify Slack is custom
    slack_node = next(n for n in topology if n["label"] == "Slack Notifications")
    assert slack_node["mode"] == "custom"


@pytest.mark.asyncio
async def test_test_adapter_connection():
    # Test S3 connection probe
    ok, msg = await WorkflowService.test_adapter_connection("7", {"bucket_name": "orbit-test"})
    assert ok is True
    assert "orbit-test" in msg

    # Test Database connection probe with sqlite in-memory
    ok_db, msg_db = await WorkflowService.test_adapter_connection(
        "sql_database", {"connection_uri": "sqlite:///:memory:"}
    )
    assert ok_db is True
    assert "verified" in msg_db

    # Test Email connection probe with invalid recipient
    ok_email_inv, msg_email_inv = await WorkflowService.test_adapter_connection(
        "email_alert", {"recipient_email": "invalid-address"}
    )
    assert ok_email_inv is False
    assert "valid recipient email" in msg_email_inv

    # Test Email custom mode without host
    ok_smtp_fail, msg_smtp_fail = await WorkflowService.test_adapter_connection(
        "10", {"mode": "custom", "recipient_email": "admin@company.com", "smtp_host": ""}
    )
    assert ok_smtp_fail is False
    assert "SMTP Host is required" in msg_smtp_fail

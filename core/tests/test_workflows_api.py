from fastapi.testclient import TestClient
from core.app import app

client = TestClient(app)


def test_get_workflow_topology():
    response = client.get("/api/v1/workflows/topology")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 7

    # Verify modes are serialized properly
    modes = [node.get("mode") for node in data]
    assert "managed" in modes
    assert "both" in modes
    assert "custom" in modes


def test_deploy_workflow():
    payload = {
        "nodes": [
            {"id": "1", "label": "Schedule Trigger", "config": {}},
            {"id": "2", "label": "Amazon S3 Storage", "config": {"bucket_name": "my-bucket"}},
        ]
    }
    response = client.post("/api/v1/workflows/deploy", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert res["status"] == "deployed"
    assert "2 active adapter stages" in res["message"]


def test_test_adapter_connection_api():
    payload = {
        "adapter_id": "7",
        "config": {"bucket_name": "orbit-production"}
    }
    response = client.post("/api/v1/workflows/test-connection", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "orbit-production" in data["message"]

    # Test Database probe via API
    db_payload = {
        "adapter_id": "sql_database",
        "config": {"connection_uri": "sqlite:///:memory:"}
    }
    db_resp = client.post("/api/v1/workflows/test-connection", json=db_payload)
    assert db_resp.status_code == 200
    db_data = db_resp.json()
    assert db_data["success"] is True
    assert "verified" in db_data["message"]

    # Test Email probe via API with invalid recipient
    email_payload = {
        "adapter_id": "email_alert",
        "config": {"recipient_email": "bad_email_format"}
    }
    email_resp = client.post("/api/v1/workflows/test-connection", json=email_payload)
    assert email_resp.status_code == 200
    email_data = email_resp.json()
    assert email_data["success"] is False

    # Test Email probe via API with valid recipient and mock
    from unittest.mock import AsyncMock, patch
    with patch("core.adapters.communication.email.EmailNotificationAdapter.send_email", new_callable=AsyncMock) as mock_send:
        mock_send.return_value = True
        valid_payload = {
            "adapter_id": "email_alert",
            "config": {"recipient_email": "user@example.com", "api_key": "test-key"}
        }
        res_valid = client.post("/api/v1/workflows/test-connection", json=valid_payload)
        assert res_valid.status_code == 200
        assert res_valid.json()["success"] is True
        assert "user@example.com" in res_valid.json()["message"]

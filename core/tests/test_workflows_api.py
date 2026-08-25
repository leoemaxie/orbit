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

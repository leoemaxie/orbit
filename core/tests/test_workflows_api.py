from fastapi.testclient import TestClient
from core.app import app

client = TestClient(app)


def test_get_workflow_topology():
    response = client.get("/api/v1/workflows/topology")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 7
    categories = [node["category"] for node in data]
    assert "trigger" in categories
    assert "parsing" in categories
    assert "storage" in categories
    assert "notify" in categories


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

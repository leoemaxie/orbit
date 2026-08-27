import pytest
from fastapi.testclient import TestClient

from core.app import create_app
from core.db.orm import Automation, Run
from core.db.session import Base, SessionLocal, engine
from core.models.enums import RunStatus


@pytest.fixture(scope="module")
def app_client():
    Base.metadata.create_all(bind=engine)
    app = create_app()
    with TestClient(app) as client:
        yield client


def test_stream_run_404_for_unknown_run(app_client):
    response = app_client.get("/api/v1/runs/non-existent-run-id/stream")
    assert response.status_code == 404
    assert "Run not found" in response.json()["detail"]


def test_stream_run_completed_snapshot_and_complete(app_client):
    with SessionLocal() as db:
        auto = Automation(raw_goal="Test SSE goal", plan={"objective": "Test"})
        db.add(auto)
        db.commit()
        db.refresh(auto)

        run = Run(
            automation_id=auto.id,
            status=RunStatus.verified,
            extracted_count=10,
            validated_count=10,
        )
        db.add(run)
        db.commit()
        db.refresh(run)
        run_id = run.id

    response = app_client.get(f"/api/v1/runs/{run_id}/stream")
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]
    content = response.text
    assert "event: snapshot" in content
    assert "event: complete" in content
    assert run_id in content

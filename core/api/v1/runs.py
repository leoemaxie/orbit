import asyncio
import logging
import os
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from core.agent.orchestrator import AgentOrchestrator
from core.api.dependencies import get_db
from core.api.serializers import run_to_out
from core.db.orm import Automation, Run
from core.db.session import SessionLocal
from core.events.bus import event_bus
from core.events.types import OrbitEvent
from core.models.enums import RunStatus
from core.models.schemas import RunOut

logger = logging.getLogger("core.api.v1.runs")

router = APIRouter(tags=["Runs"])
orchestrator = AgentOrchestrator()


@router.get("/runs/{run_id}", response_model=RunOut)
def get_run(run_id: str, db: Annotated[Session, Depends(get_db)]):
    """Retrieves detailed execution audit trail and results for a specific run."""
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run_to_out(run)


@router.get("/runs/{run_id}/stream")
async def stream_run_telemetry(run_id: str, request: Request, db: Annotated[Session, Depends(get_db)]):
    """
    Streams live run telemetry, stage transitions, reasoning logs, and status updates via Server-Sent Events (SSE).
    """
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    initial_payload = run_to_out(run)

    async def event_generator():
        # 1. Send initial snapshot immediately
        yield f"event: snapshot\ndata: {initial_payload.model_dump_json()}\n\n"

        # If already completed or failed, close the stream cleanly
        if initial_payload.status in (RunStatus.verified, RunStatus.failed):
            yield f"event: complete\ndata: {initial_payload.model_dump_json()}\n\n"
            return

        queue: asyncio.Queue[OrbitEvent | None] = asyncio.Queue()

        async def _on_event(evt: OrbitEvent):
            if evt.run_id == run_id:
                await queue.put(evt)

        event_bus.subscribe(_on_event)

        try:
            while True:
                if await request.is_disconnected():
                    break

                try:
                    evt = await asyncio.wait_for(queue.get(), timeout=1.0)
                    if evt is None:
                        break

                    with SessionLocal() as poll_db:
                        current_run = poll_db.query(Run).filter(Run.id == run_id).first()
                        if current_run:
                            out = run_to_out(current_run)
                            event_name = "complete" if out.status in (RunStatus.verified, RunStatus.failed) else "update"
                            yield f"event: {event_name}\ndata: {out.model_dump_json()}\n\n"

                            if out.status in (RunStatus.verified, RunStatus.failed):
                                break
                except asyncio.TimeoutError:
                    with SessionLocal() as poll_db:
                        current_run = poll_db.query(Run).filter(Run.id == run_id).first()
                        if current_run:
                            out = run_to_out(current_run)
                            if out.status in (RunStatus.verified, RunStatus.failed):
                                yield f"event: complete\ndata: {out.model_dump_json()}\n\n"
                                break
                    yield ": ping\n\n"
        finally:
            event_bus.unsubscribe(_on_event)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/runs/{run_id}/dossier")
def get_run_dossier(run_id: str, db: Annotated[Session, Depends(get_db)]):
    """Streams the generated and redacted PDF/HTML report dossier for interactive inspection."""
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    pdf_path = os.path.join("exports", run.automation_id, run.id, "dossier.pdf")
    if os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            return Response(content=f.read(), media_type="application/pdf")

    # Generate interactive HTML fallback if PDF file is not on local disk
    html_report = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"><title>Orbit Executive Briefing - Run {run.id[:8]}</title>
    <style>body{{font-family:system-ui;background:#090d16;color:#e2e8f0;padding:2rem;}}
    .badge{{background:#06b6d420;color:#06b6d4;padding:4px 8px;border-radius:4px;font-family:monospace;}}</style>
    </head>
    <body>
    <h2>🛰️ Orbit Report Dossier <span class="badge">Run: {run.id[:8]}</span></h2>
    <p>Extraction Status: <strong>{run.status.value}</strong> | Records: {run.extracted_count}</p>
    <hr style="border:1px solid #1e293b;margin:1.5rem 0;"/>
    <p>PII Entities Masked: <strong>Active (Nutrient Redactor)</strong></p>
    </body></html>
    """
    return Response(content=html_report.encode("utf-8"), media_type="text/html")


@router.post("/runs/{run_id}/retry", response_model=RunOut)
async def retry_run(run_id: str, db: Annotated[Session, Depends(get_db)]):
    """Resumes and retries execution of an existing run from its last checkpoint in background."""
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    automation = db.query(Automation).filter(Automation.id == run.automation_id).first()
    if not automation:
        raise HTTPException(status_code=404, detail="Parent automation not found")

    run.status = RunStatus.retrieving if run.sources_found else RunStatus.discovering
    run.error, run.finished_at = None, None
    db.commit()
    db.refresh(run)

    async def _execute_retry(auto_id: str, r_id: str):
        with SessionLocal() as bg_db:
            bg_auto = bg_db.query(Automation).filter(Automation.id == auto_id).first()
            bg_run = bg_db.query(Run).filter(Run.id == r_id).first()
            if bg_auto and bg_run:
                try:
                    await orchestrator.execute_run(bg_db, bg_auto, run=bg_run, resume=True)
                except Exception as err:
                    logger.exception("Background execution error in run %s: %s", r_id, err)

    asyncio.create_task(_execute_retry(automation.id, run.id))
    return run_to_out(run)


@router.get("/automations/{automation_id}/runs", response_model=list[RunOut])
def list_automation_runs(automation_id: str, db: Annotated[Session, Depends(get_db)]):
    """Lists past execution history for a given automation."""
    runs = db.query(Run).filter(Run.automation_id == automation_id).order_by(Run.started_at.desc()).all()
    return [run_to_out(r) for r in runs]

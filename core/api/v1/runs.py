import asyncio
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.agent.orchestrator import AgentOrchestrator
from core.api.dependencies import get_db
from core.api.serializers import run_to_out
from core.db.orm import Automation, Run
from core.db.session import SessionLocal
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


@router.post("/runs/{run_id}/retry", response_model=RunOut)
async def retry_run(run_id: str, db: Annotated[Session, Depends(get_db)]):
    """Resumes and retries execution of an existing run from its last checkpoint in background."""
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    automation = db.query(Automation).filter(Automation.id == run.automation_id).first()
    if not automation:
        raise HTTPException(status_code=404, detail="Parent automation not found")

    # Determine resume status based on checkpoint state
    if run.sources_found:
        run.status = RunStatus.retrieving
    else:
        run.status = RunStatus.discovering

    run.error = None
    run.finished_at = None
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
                    logger.exception("Background execution error while retrying run %s: %s", r_id, err)

    asyncio.create_task(_execute_retry(automation.id, run.id))
    return run_to_out(run)


@router.get("/automations/{automation_id}/runs", response_model=list[RunOut])
def list_automation_runs(automation_id: str, db: Annotated[Session, Depends(get_db)]):
    """Lists past execution history for a given automation."""
    runs = (
        db.query(Run)
        .filter(Run.automation_id == automation_id)
        .order_by(Run.started_at.desc())
        .all()
    )
    return [run_to_out(r) for r in runs]

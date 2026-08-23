from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.api.dependencies import get_db
from core.api.v1.automations import _run_to_out
from core.db.orm import Run
from core.models.schemas import RunOut

router = APIRouter(tags=["Runs"])


@router.get("/runs/{run_id}", response_model=RunOut)
def get_run(run_id: str, db: Annotated[Session, Depends(get_db)]):
    """Retrieves detailed execution audit trail and results for a specific run."""
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return _run_to_out(run)


@router.get("/automations/{automation_id}/runs", response_model=list[RunOut])
def list_automation_runs(automation_id: str, db: Annotated[Session, Depends(get_db)]):
    """Lists past execution history for a given automation."""
    runs = (
        db.query(Run)
        .filter(Run.automation_id == automation_id)
        .order_by(Run.started_at.desc())
        .all()
    )
    return [_run_to_out(r) for r in runs]

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.orm import Automation, Run
from app.models.schemas import GoalRequest, AutomationOut, RunOut
from app.core.interpreter import interpret_goal
from app.core.engine import execute_automation

router = APIRouter()


@router.post("/automations", response_model=AutomationOut)
async def create_automation(payload: GoalRequest, db: Session = Depends(get_db)):
    """Goal Interpreter: turns a natural-language goal into a stored automation spec."""
    spec = await interpret_goal(payload.goal)

    automation = Automation(raw_goal=payload.goal, spec=spec.model_dump())
    db.add(automation)
    db.commit()
    db.refresh(automation)

    return AutomationOut(
        id=automation.id,
        raw_goal=automation.raw_goal,
        spec=spec,
        next_run_at=None,
    )


@router.get("/automations", response_model=list[AutomationOut])
def list_automations(db: Session = Depends(get_db)):
    automations = db.query(Automation).order_by(Automation.created_at.desc()).all()
    return [
        AutomationOut(
            id=a.id,
            raw_goal=a.raw_goal,
            spec=a.spec,
            next_run_at=a.next_run_at.isoformat() if a.next_run_at else None,
        )
        for a in automations
    ]


@router.post("/automations/{automation_id}/run", response_model=RunOut)
async def run_automation(automation_id: str, db: Session = Depends(get_db)):
    """Executes the Orbit Core pipeline once for this automation ('Run Now')."""
    automation = db.query(Automation).filter(Automation.id == automation_id).first()
    if not automation:
        raise HTTPException(status_code=404, detail="Automation not found")

    run = await execute_automation(db, automation)
    return _run_to_out(run)


@router.get("/automations/{automation_id}/runs", response_model=list[RunOut])
def list_runs(automation_id: str, db: Session = Depends(get_db)):
    runs = (
        db.query(Run)
        .filter(Run.automation_id == automation_id)
        .order_by(Run.started_at.desc())
        .all()
    )
    return [_run_to_out(r) for r in runs]


@router.get("/runs/{run_id}", response_model=RunOut)
def get_run(run_id: str, db: Session = Depends(get_db)):
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return _run_to_out(run)


def _run_to_out(run: Run) -> RunOut:
    return RunOut(
        id=run.id,
        status=run.status.value if hasattr(run.status, "value") else run.status,
        started_at=run.started_at.isoformat(),
        finished_at=run.finished_at.isoformat() if run.finished_at else None,
        sources_found=run.sources_found,
        pages_retrieved=run.pages_retrieved,
        error=run.error,
        results=[
            {
                "product": r.product,
                "price": float(r.price) if r.price is not None else None,
                "currency": r.currency,
                "availability": r.availability,
                "seller": r.seller,
                "url": r.url,
                "valid": r.valid,
                "validation_errors": r.validation_errors,
            }
            for r in run.results
        ],
    )

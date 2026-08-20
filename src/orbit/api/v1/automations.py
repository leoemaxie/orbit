from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from orbit.agent.interpreter import GoalInterpreter
from orbit.agent.orchestrator import AgentOrchestrator
from orbit.api.dependencies import get_db
from orbit.db.orm import Automation, Run
from orbit.models.execution_plan import ExecutionPlan
from orbit.models.schemas import AutomationListOut, AutomationOut, GoalRequest, ResultOut, RunOut

router = APIRouter(prefix="/automations", tags=["Automations"])

interpreter = GoalInterpreter()
orchestrator = AgentOrchestrator()


def _automation_to_out(a: Automation) -> AutomationOut:
    return AutomationOut(
        id=a.id,
        raw_goal=a.raw_goal,
        plan=ExecutionPlan(**a.plan),
        active=a.active,
        created_at=a.created_at.isoformat(),
        next_run_at=a.next_run_at.isoformat() if a.next_run_at else None,
    )


def _run_to_out(r: Run) -> RunOut:
    return RunOut(
        id=r.id,
        automation_id=r.automation_id,
        status=r.status.value if hasattr(r.status, "value") else str(r.status),
        started_at=r.started_at.isoformat(),
        finished_at=r.finished_at.isoformat() if r.finished_at else None,
        sources_found=r.sources_found,
        pages_retrieved=r.pages_retrieved,
        extracted_count=r.extracted_count,
        validated_count=r.validated_count,
        condition_matched=r.condition_matched,
        condition_message=r.condition_message,
        reasoning_log=r.reasoning_log,
        error=r.error,
        results=[
            ResultOut(
                id=res.id,
                url=res.url,
                data=res.data or {},
                valid=res.valid,
                validation_errors=res.validation_errors,
                created_at=res.created_at.isoformat(),
            )
            for res in r.results
        ],
    )


@router.post("", response_model=AutomationOut)
async def create_automation(payload: GoalRequest, db: Session = Depends(get_db)):
    """Interprets a natural-language goal into a dynamic execution plan and creates an automation."""
    plan = await interpreter.interpret(payload.goal)

    automation = Automation(
        raw_goal=payload.goal,
        plan=plan.model_dump(),
        active=True,
    )
    db.add(automation)
    db.commit()
    db.refresh(automation)

    return _automation_to_out(automation)


@router.get("", response_model=AutomationListOut)
def list_automations(db: Session = Depends(get_db)):
    """Retrieves all registered automations."""
    records = db.query(Automation).order_by(Automation.created_at.desc()).all()
    items = [_automation_to_out(a) for a in records]
    return AutomationListOut(items=items, total=len(items))


@router.get("/{automation_id}", response_model=AutomationOut)
def get_automation(automation_id: str, db: Session = Depends(get_db)):
    """Retrieves a single automation by its ID."""
    automation = db.query(Automation).filter(Automation.id == automation_id).first()
    if not automation:
        raise HTTPException(status_code=404, detail="Automation not found")
    return _automation_to_out(automation)


@router.post("/{automation_id}/run", response_model=RunOut)
async def run_automation(automation_id: str, db: Session = Depends(get_db)):
    """Triggers an on-demand autonomous run for the specified automation."""
    automation = db.query(Automation).filter(Automation.id == automation_id).first()
    if not automation:
        raise HTTPException(status_code=404, detail="Automation not found")

    run = await orchestrator.execute_run(db, automation)
    return _run_to_out(run)


@router.delete("/{automation_id}")
def delete_automation(automation_id: str, db: Session = Depends(get_db)):
    """Deletes an automation and all its associated runs and results."""
    automation = db.query(Automation).filter(Automation.id == automation_id).first()
    if not automation:
        raise HTTPException(status_code=404, detail="Automation not found")

    db.delete(automation)
    db.commit()
    return {"message": "Automation deleted successfully"}

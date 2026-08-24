import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.agent.interpreter import GoalInterpreter
from core.agent.orchestrator import AgentOrchestrator
from core.api.dependencies import get_db
from core.api.serializers import automation_to_out, run_to_out
from core.db.orm import Automation
from core.models.schemas import AutomationListOut, AutomationOut, GoalRequest, RunOut

logger = logging.getLogger("core.api.v1.automations")

router = APIRouter(prefix="/automations", tags=["Automations"])

interpreter = GoalInterpreter()
orchestrator = AgentOrchestrator()


@router.post("", response_model=AutomationOut)
async def create_automation(payload: GoalRequest, db: Annotated[Session, Depends(get_db)]):
    """Interprets a natural-language goal into a dynamic execution plan and creates an automation."""
    try:
        plan = await interpreter.interpret(payload.goal)
    except ValueError as e:
        logger.warning("Goal interpretation validation failed: %s", e)
        raise HTTPException(
            status_code=400,
            detail="The provided goal could not be processed into an execution plan. Please provide a more descriptive objective.",
        ) from e
    except Exception as e:
        logger.exception("Unexpected error during goal interpretation")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while synthesizing the execution plan. Please try again.",
        ) from e

    automation = Automation(
        raw_goal=payload.goal,
        plan=plan.model_dump(),
        active=True,
    )
    db.add(automation)
    db.commit()
    db.refresh(automation)

    return automation_to_out(automation)


@router.get("", response_model=AutomationListOut)
def list_automations(db: Annotated[Session, Depends(get_db)]):
    """Retrieves all registered automations."""
    records = db.query(Automation).order_by(Automation.created_at.desc()).all()
    items = [automation_to_out(a) for a in records]
    return AutomationListOut(items=items, total=len(items))


@router.get("/{automation_id}", response_model=AutomationOut)
def get_automation(automation_id: str, db: Annotated[Session, Depends(get_db)]):
    """Retrieves a single automation by its ID."""
    automation = db.query(Automation).filter(Automation.id == automation_id).first()
    if not automation:
        raise HTTPException(status_code=404, detail="Automation not found")
    return automation_to_out(automation)


@router.post("/{automation_id}/run", response_model=RunOut)
async def run_automation(automation_id: str, db: Annotated[Session, Depends(get_db)]):
    """Triggers an on-demand autonomous run for the specified automation."""
    automation = db.query(Automation).filter(Automation.id == automation_id).first()
    if not automation:
        raise HTTPException(status_code=404, detail="Automation not found")

    try:
        run = await orchestrator.execute_run(db, automation)
        return run_to_out(run)
    except Exception as e:
        logger.exception("Orchestrator failed during execution of automation %s", automation_id)
        raise HTTPException(
            status_code=500,
            detail="The automation run could not be completed. Please try again shortly.",
        ) from e


@router.delete("/{automation_id}")
def delete_automation(automation_id: str, db: Annotated[Session, Depends(get_db)]):
    """Deletes an automation and all its associated runs and results."""
    automation = db.query(Automation).filter(Automation.id == automation_id).first()
    if not automation:
        raise HTTPException(status_code=404, detail="Automation not found")

    db.delete(automation)
    db.commit()
    return {"message": "Automation deleted successfully"}

import asyncio
import logging
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from core.agent.orchestrator import AgentOrchestrator
from core.api.dependencies import get_db
from core.config.settings import get_settings
from core.db.orm import Automation
from core.db.session import SessionLocal

logger = logging.getLogger("core.api.v1.scheduler")

router = APIRouter(prefix="/scheduler", tags=["Scheduler"])

orchestrator = AgentOrchestrator()


def verify_scheduler_auth(
    x_scheduler_secret: str | None = Header(None, alias="X-Scheduler-Secret"),
    authorization: str | None = Header(None, alias="Authorization"),
):
    """Provider-agnostic authentication verifying Cloud Schedulers (GCP, AWS, Render, GitHub, etc.)."""
    settings = get_settings()
    configured_secret = settings.scheduler_secret

    # If no secret is configured on the server, open access is allowed
    if not configured_secret:
        return True

    # Check X-Scheduler-Secret header
    if x_scheduler_secret and x_scheduler_secret == configured_secret:
        return True

    # Check Bearer token in Authorization header
    if authorization:
        token = authorization.replace("Bearer ", "").strip()
        if token == configured_secret:
            return True

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized: invalid or missing scheduler secret header.",
    )


@router.post("/trigger-due", summary="Trigger all due automations (Cloud Scheduler Hook)")
@router.post("/tick", summary="Alias for /trigger-due")
async def trigger_due_automations(
    db: Annotated[Session, Depends(get_db)],
    _: bool = Depends(verify_scheduler_auth),
):
    """
    Provider-agnostic cloud-native scheduler webhook.
    Works seamlessly with:
    - Google Cloud Scheduler
    - AWS EventBridge / Lambda
    - Render Cron Jobs
    - Fly.io / Railway / Heroku
    - GitHub Actions / Custom Crons
    """
    now_utc = datetime.now(timezone.utc)
    due_automations = (
        db.query(Automation)
        .filter(
            Automation.active.is_(True),
            Automation.next_run_at.isnot(None),
            Automation.next_run_at <= now_utc,
        )
        .all()
    )

    triggered_ids = []
    for auto in due_automations:
        try:
            # Atomic update: temporarily clear next_run_at to prevent double triggering on overlapping ticks
            auto.next_run_at = None
            db.commit()

            async def _execute_due_task(auto_id: str):
                with SessionLocal() as bg_db:
                    bg_auto = bg_db.query(Automation).filter(Automation.id == auto_id).first()
                    if bg_auto:
                        try:
                            await orchestrator.execute_run(bg_db, bg_auto)
                        except Exception as err:
                            logger.exception("Scheduled execution error for automation %s: %s", auto_id, err)

            asyncio.create_task(_execute_due_task(auto.id))
            triggered_ids.append(auto.id)
            logger.info("Cloud scheduler triggered execution for automation %s", auto.id)
        except Exception as e:
            logger.error("Failed to trigger scheduled execution for automation %s: %s", auto.id, e)

    return {
        "status": "success",
        "due_count": len(due_automations),
        "triggered_automation_ids": triggered_ids,
        "server_time_utc": now_utc.isoformat(),
    }


@router.get("/status", summary="Inspect upcoming scheduled automations")
def get_scheduler_status(
    db: Annotated[Session, Depends(get_db)],
    _: bool = Depends(verify_scheduler_auth),
):
    """Lists all active automations with their next scheduled execution time."""
    now_utc = datetime.now(timezone.utc)
    active_schedules = (
        db.query(Automation)
        .filter(Automation.active.is_(True), Automation.next_run_at.isnot(None))
        .order_by(Automation.next_run_at.asc())
        .all()
    )

    items = []
    for auto in active_schedules:
        plan = auto.plan or {}
        items.append({
            "automation_id": auto.id,
            "objective": plan.get("objective") or auto.raw_goal,
            "frequency": plan.get("frequency"),
            "schedule_time": plan.get("schedule_time"),
            "timezone": plan.get("timezone", "UTC"),
            "next_run_at": auto.next_run_at.isoformat() if auto.next_run_at else None,
            "is_due": auto.next_run_at <= now_utc if auto.next_run_at else False,
        })

    return {
        "server_time_utc": now_utc.isoformat(),
        "active_schedule_count": len(items),
        "schedules": items,
    }

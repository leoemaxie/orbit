import asyncio
from datetime import datetime, timezone
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from core.agent.orchestrator import AgentOrchestrator
from core.db.orm import Automation
from core.db.session import SessionLocal

logger = logging.getLogger("core.scheduler")


class SchedulerService:
    """Background scheduler that automatically queries and executes recurring automations."""

    scheduler: AsyncIOScheduler
    orchestrator: AgentOrchestrator
    _is_running: bool

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.orchestrator = AgentOrchestrator()
        self._is_running = False

    def start(self, check_interval_seconds: int = 60):
        if self._is_running:
            return

        self.scheduler.add_job(
            self._check_and_run_due_automations,
            trigger=IntervalTrigger(seconds=check_interval_seconds),
            id="orbit_due_automations_check",
            replace_existing=True,
        )
        self.scheduler.start()
        self._is_running = True
        logger.info(f"⏰ Orbit Scheduler started. Polling interval: {check_interval_seconds}s")

    def shutdown(self):
        if self._is_running:
            self.scheduler.shutdown(wait=False)
            self._is_running = False
            logger.info("Orbit Scheduler stopped.")

    async def _check_and_run_due_automations(self):
        now = datetime.now(timezone.utc)
        db = SessionLocal()
        try:
            due_automations = (
                db.query(Automation)
                .filter(
                    Automation.active.is_(True),
                    Automation.next_run_at.is_not(None),
                    Automation.next_run_at <= now,
                )
                .all()
            )

            if due_automations:
                logger.info(f"Found {len(due_automations)} due automation(s) to execute.")

            for auto in due_automations:
                try:
                    logger.info(f"Triggering scheduled execution for automation {auto.id}...")
                    # Execute asynchronously
                    asyncio.create_task(self._run_single_automation(auto.id))
                except Exception as e:
                    logger.error(f"Failed to launch task for automation {auto.id}: {e}")

        except Exception as e:
            logger.error(f"Error querying due automations: {e}")
        finally:
            db.close()

    async def _run_single_automation(self, automation_id: str):
        db = SessionLocal()
        try:
            auto = db.query(Automation).filter(Automation.id == automation_id).first()
            if auto:
                await self.orchestrator.execute_run(db, auto)
        except Exception as e:
            logger.error(f"Execution error for scheduled automation {automation_id}: {e}")
        finally:
            db.close()


scheduler_service = SchedulerService()

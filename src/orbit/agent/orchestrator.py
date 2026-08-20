from datetime import datetime, timedelta, timezone
import logging
from typing import Any
from sqlalchemy.orm import Session

from orbit.agent.condition import ConditionEvaluator
from orbit.agent.reasoner import AgentReasoner
from orbit.db.orm import Automation, Result, Run
from orbit.events.bus import event_bus
from orbit.events.types import OrbitEvent
from orbit.models.enums import Frequency, RunStatus
from orbit.models.execution_plan import ExecutionPlan
from orbit.notifications.service import NotificationService
from orbit.pipeline.discovery.serpapi import SerpApiDiscovery
from orbit.pipeline.extraction.llm_extractor import LLMExtractor
from orbit.pipeline.retrieval.brightdata import BrightDataRetrieval
from orbit.pipeline.validation.schema_validator import SchemaValidator

logger = logging.getLogger("orbit.agent.orchestrator")

FREQUENCY_DELTAS = {
    Frequency.hourly: timedelta(hours=1),
    Frequency.daily: timedelta(days=1),
    Frequency.weekly: timedelta(weeks=1),
    Frequency.monthly: timedelta(days=30),
    Frequency.once: None,
}


class AgentOrchestrator:
    """The central agentic execution engine that executes goal-driven web data operations."""

    def __init__(
        self,
        discovery=None,
        retrieval=None,
        extractor=None,
        validator=None,
        evaluator=None,
        notifier=None,
        reasoner=None,
    ):
        self.discovery = discovery or SerpApiDiscovery()
        self.retrieval = retrieval or BrightDataRetrieval()
        self.extractor = extractor or LLMExtractor()
        self.validator = validator or SchemaValidator()
        self.evaluator = evaluator or ConditionEvaluator()
        self.notifier = notifier or NotificationService()
        self.reasoner = reasoner or AgentReasoner()

    async def execute_run(self, db: Session, automation: Automation) -> Run:
        """Executes a full agent run with self-correction, validation, alerting, and verification."""
        plan_dict = automation.plan
        plan = ExecutionPlan(**plan_dict)

        run = Run(
            automation_id=automation.id,
            status=RunStatus.discovering,
            reasoning_log=[],
        )
        db.add(run)
        db.commit()
        db.refresh(run)

        await event_bus.publish(
            OrbitEvent(
                event_type="run.started",
                run_id=run.id,
                automation_id=automation.id,
                message=f"Starting autonomous run for goal: {automation.raw_goal}",
            )
        )

        reasoning_trail: list[dict[str, Any]] = []

        try:
            # ────────────────────────────────────────────────
            # 1. DISCOVERY STAGE
            # ────────────────────────────────────────────────
            urls = await self.discovery.discover(plan, max_results=8)

            # Self-correction check: if no URLs discovered, ask reasoner to rephrase query
            if not urls:
                logger.info("0 sources found, invoking Agent Reasoner for recovery...")
                diagnosis = await self.reasoner.diagnose_and_recover(
                    stage="discovery",
                    error="No search results returned for query",
                    plan=plan,
                )
                reasoning_trail.append({"stage": "discovery", "decision": diagnosis})

                if diagnosis.get("can_recover") and diagnosis.get("new_search_query"):
                    adjusted_plan = plan.model_copy(
                        update={"search_query": diagnosis["new_search_query"]}
                    )
                    urls = await self.discovery.discover(adjusted_plan, max_results=8)

            run.sources_found = urls
            run.reasoning_log = reasoning_trail
            db.commit()

            if not urls:
                run.status = RunStatus.failed
                run.error = "Discovery failed: No relevant web sources could be found."
                run.finished_at = datetime.now(timezone.utc)
                db.commit()
                return run

            # ────────────────────────────────────────────────
            # 2. RETRIEVAL STAGE
            # ────────────────────────────────────────────────
            run.status = RunStatus.retrieving
            db.commit()

            pages = await self.retrieval.retrieve_many(
                urls, country_code=plan.country_code
            )

            # Retry once for any failed URLs
            failed_urls = [u for u, content in pages.items() if not content]
            if failed_urls:
                logger.info(f"Retrying {len(failed_urls)} failed page retrievals...")
                retry_pages = await self.retrieval.retrieve_many(
                    failed_urls, country_code=plan.country_code
                )
                pages.update(retry_pages)

            retrieved_urls = [u for u, content in pages.items() if content]
            run.pages_retrieved = retrieved_urls
            db.commit()

            if not retrieved_urls:
                run.status = RunStatus.failed
                run.error = "Retrieval failed: Unable to fetch content from discovered URLs."
                run.finished_at = datetime.now(timezone.utc)
                db.commit()
                return run

            # ────────────────────────────────────────────────
            # 3. EXTRACTION STAGE
            # ────────────────────────────────────────────────
            run.status = RunStatus.extracting
            db.commit()

            extracted_records: list[dict[str, Any]] = []
            for url in retrieved_urls:
                content = pages.get(url, "")
                record = await self.extractor.extract(url, content, plan)
                extracted_records.append(record)

            run.extracted_count = len(extracted_records)
            db.commit()

            # ────────────────────────────────────────────────
            # 4. VALIDATION & STORAGE STAGE
            # ────────────────────────────────────────────────
            run.status = RunStatus.validating
            db.commit()

            valid_count = 0
            valid_records = []

            for rec in extracted_records:
                is_valid, errors = self.validator.validate(rec, plan)
                if is_valid:
                    valid_count += 1
                    valid_records.append(rec)

                result_row = Result(
                    run_id=run.id,
                    url=rec.get("url"),
                    data=rec.get("data", {}),
                    valid=is_valid,
                    validation_errors=errors if errors else None,
                )
                db.add(result_row)

            run.validated_count = valid_count
            run.status = RunStatus.storing
            db.commit()

            # ────────────────────────────────────────────────
            # 5. CONDITION EVALUATION & ALERTING
            # ────────────────────────────────────────────────
            if plan.condition and valid_records:
                run.status = RunStatus.evaluating
                db.commit()

                matched, cond_msg = self.evaluator.evaluate(plan.condition, valid_records)
                run.condition_matched = matched
                run.condition_message = cond_msg
                db.commit()

                if matched:
                    run.status = RunStatus.alerting
                    db.commit()
                    await self.notifier.notify(
                        title=f"Orbit Alert: {plan.objective}",
                        message=cond_msg,
                        payload={"automation_id": automation.id, "run_id": run.id},
                    )

            # ────────────────────────────────────────────────
            # 6. VERIFICATION STAGE
            # ────────────────────────────────────────────────
            if valid_count == 0:
                run.status = RunStatus.failed
                run.error = "Verification failed: 0 records passed schema validation."
            else:
                run.status = RunStatus.verified

            run.finished_at = datetime.now(timezone.utc)
            db.commit()

            # ────────────────────────────────────────────────
            # 7. SCHEDULE NEXT RUN
            # ────────────────────────────────────────────────
            delta = FREQUENCY_DELTAS.get(plan.frequency)
            if delta and automation.active:
                automation.next_run_at = datetime.now(timezone.utc) + delta
                db.commit()

            await event_bus.publish(
                OrbitEvent(
                    event_type="run.completed",
                    run_id=run.id,
                    automation_id=automation.id,
                    message=f"Run finished with status {run.status.value}",
                    payload={"valid_count": valid_count, "extracted_count": len(extracted_records)},
                )
            )

            return run

        except Exception as e:
            logger.exception(f"Unexpected error in orchestrator: {e}")
            run.status = RunStatus.failed
            run.error = str(e)
            run.finished_at = datetime.now(timezone.utc)
            db.commit()
            return run

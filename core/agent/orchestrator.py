import logging
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from core.adapters.storage.local_export import LocalFileExportSink
from core.agent.condition import ConditionEvaluator
from core.agent.reasoner import AgentReasoner
from core.db.orm import Automation, Result, Run
from core.events.bus import event_bus
from core.events.types import OrbitEvent
from core.models.enums import Frequency, RunStatus
from core.models.execution_plan import ExecutionPlan
from core.notifications.service import NotificationService
from core.pipeline.discovery.composite import CompositeDiscovery
from core.pipeline.extraction.llm_extractor import LLMExtractor
from core.pipeline.retrieval.brightdata import BrightDataRetrieval
from core.pipeline.retrieval.link_extractor import LinkExtractor
from core.pipeline.validation.anomaly_detector import AnomalyDetector
from core.pipeline.validation.schema_validator import SchemaValidator
from core.scheduler.cron import calculate_next_run

logger = logging.getLogger("core.agent.orchestrator")


class AgentOrchestrator:
    """The central agentic execution engine that executes goal-driven web data operations."""

    discovery: CompositeDiscovery
    retrieval: BrightDataRetrieval
    extractor: LLMExtractor
    validator: SchemaValidator
    evaluator: ConditionEvaluator
    notifier: NotificationService
    reasoner: AgentReasoner
    link_extractor: LinkExtractor
    anomaly_detector: AnomalyDetector
    export_sink: LocalFileExportSink

    def __init__(
        self,
        discovery: CompositeDiscovery | None = None,
        retrieval: BrightDataRetrieval | None = None,
        extractor: LLMExtractor | None = None,
        validator: SchemaValidator | None = None,
        evaluator: ConditionEvaluator | None = None,
        notifier: NotificationService | None = None,
        reasoner: AgentReasoner | None = None,
        link_extractor: LinkExtractor | None = None,
        anomaly_detector: AnomalyDetector | None = None,
        export_sink: LocalFileExportSink | None = None,
    ):
        # Default to CompositeDiscovery so Orbit functions with or without SerpApi
        self.discovery = discovery or CompositeDiscovery()
        self.retrieval = retrieval or BrightDataRetrieval()
        self.extractor = extractor or LLMExtractor()
        self.validator = validator or SchemaValidator()
        self.evaluator = evaluator or ConditionEvaluator()
        self.notifier = notifier or NotificationService()
        self.reasoner = reasoner or AgentReasoner()
        self.link_extractor = link_extractor or LinkExtractor()
        self.anomaly_detector = anomaly_detector or AnomalyDetector()
        self.export_sink = export_sink or LocalFileExportSink()

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
            # 1. DISCOVERY STAGE (Decoupled & Multi-Engine)
            # ────────────────────────────────────────────────
            urls = await self.discovery.discover(plan, max_results=8)

            # Self-correction check: if no URLs discovered, ask reasoner to rephrase query
            if not urls:
                logger.info("0 sources found, invoking Agent Reasoner for recovery...")
                diagnosis = await self.reasoner.diagnose_and_recover(
                    stage="discovery",
                    error="No search results returned for query across available engines",
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
            # 2. RETRIEVAL STAGE (with 2-Hop Detail Link Discovery)
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

            # 2-Hop Navigation: Check if retrieved pages are listing pages and discover detail links
            extra_detail_urls = []
            for u, content in pages.items():
                if content:
                    child_links = self.link_extractor.extract_child_links(u, content, max_links=2)
                    for child in child_links:
                        if child not in pages and child not in extra_detail_urls:
                            extra_detail_urls.append(child)

            if extra_detail_urls:
                logger.info(f"Discovered {len(extra_detail_urls)} child detail links for 2-hop crawl.")
                child_pages = await self.retrieval.retrieve_many(
                    extra_detail_urls, country_code=plan.country_code
                )
                pages.update(child_pages)

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
                content = pages.get(url) or ""
                record = await self.extractor.extract(url, content, plan)
                extracted_records.append(record)

            run.extracted_count = len(extracted_records)
            db.commit()

            # ────────────────────────────────────────────────
            # 4. VALIDATION & ANOMALY DETECTION
            # ────────────────────────────────────────────────
            run.status = RunStatus.validating
            db.commit()

            # Statistical anomaly check across records
            annotated_records = self.anomaly_detector.filter_and_annotate_outliers(extracted_records)

            valid_count = 0
            valid_records = []

            for rec in annotated_records:
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

            # Export sink (local file / external storage)
            if valid_records:
                await self.export_sink.export_results(automation.id, run.id, valid_records)

            # ────────────────────────────────────────────────
            # 5. CONDITION EVALUATION & HISTORICAL COMPARISON
            # ────────────────────────────────────────────────
            if plan.condition and valid_records:
                run.status = RunStatus.evaluating
                db.commit()

                # Fetch previous run records for historical delta calculations
                previous_records = self._get_previous_run_records(db, automation.id, run.id)

                matched, cond_msg = self.evaluator.evaluate(
                    plan.condition, valid_records, previous_records=previous_records
                )
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
            # 7. TIMEZONE-AWARE WALL-CLOCK SCHEDULING
            # ────────────────────────────────────────────────
            if automation.active and plan.frequency != Frequency.once:
                next_run = calculate_next_run(
                    frequency=plan.frequency,
                    schedule_time=plan.schedule_time,
                    tz_name=plan.timezone,
                )
                if next_run:
                    automation.next_run_at = next_run
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
            logger.exception("Unexpected error in orchestrator")
            run.status = RunStatus.failed
            run.error = str(e)
            run.finished_at = datetime.now(timezone.utc)
            db.commit()
            return run

    def _get_previous_run_records(
        self, db: Session, automation_id: str, current_run_id: str
    ) -> list[dict[str, Any]]:
        """Retrieves valid records from the most recent previous run of this automation."""
        last_run = (
            db.query(Run)
            .filter(
                Run.automation_id == automation_id,
                Run.id != current_run_id,
                Run.status.in_([RunStatus.verified, RunStatus.alerting]),
            )
            .order_by(Run.started_at.desc())
            .first()
        )
        if not last_run or not last_run.results:
            return []

        return [{"url": r.url, "data": r.data or {}} for r in last_run.results if r.valid]

import logging
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from core.adapters.storage.local_export import LocalFileExportSink
from core.agent.brain import AgentBrain
from core.agent.condition import ConditionEvaluator
from core.db.orm import Automation, Result, Run
from core.events.bus import event_bus
from core.events.types import OrbitEvent
from core.models.enums import Frequency, RunStatus
from core.models.execution_plan import ExecutionPlan
from core.notifications.service import NotificationService
from core.pipeline.discovery.composite import CompositeDiscovery
from core.pipeline.extraction.llm_extractor import LLMExtractor
from core.pipeline.retrieval.link_extractor import LinkExtractor
from core.pipeline.retrieval.proxy import ProxyRetrieval
from core.pipeline.validation.anomaly_detector import AnomalyDetector
from core.pipeline.validation.schema_validator import SchemaValidator
from core.pipeline.verification.engine import VerificationEngine
from core.scheduler.cron import calculate_next_run

logger = logging.getLogger("core.agent.orchestrator")


class AgentOrchestrator:
    """The central agentic execution engine that executes goal-driven web data operations."""

    discovery: CompositeDiscovery
    retrieval: ProxyRetrieval
    extractor: LLMExtractor
    validator: SchemaValidator
    evaluator: ConditionEvaluator
    notifier: NotificationService
    brain: AgentBrain
    link_extractor: LinkExtractor
    anomaly_detector: AnomalyDetector
    verification: VerificationEngine
    export_sink: LocalFileExportSink

    def __init__(
        self,
        discovery: CompositeDiscovery | None = None,
        retrieval: ProxyRetrieval | None = None,
        extractor: LLMExtractor | None = None,
        validator: SchemaValidator | None = None,
        evaluator: ConditionEvaluator | None = None,
        notifier: NotificationService | None = None,
        brain: AgentBrain | None = None,
        link_extractor: LinkExtractor | None = None,
        anomaly_detector: AnomalyDetector | None = None,
        verification: VerificationEngine | None = None,
        export_sink: LocalFileExportSink | None = None,
    ):
        # Default to CompositeDiscovery so Orbit functions across multi-source discovery backends
        self.discovery = discovery or CompositeDiscovery()
        self.retrieval = retrieval or ProxyRetrieval()
        self.extractor = extractor or LLMExtractor()
        self.validator = validator or SchemaValidator()
        self.evaluator = evaluator or ConditionEvaluator()
        self.notifier = notifier or NotificationService()
        self.brain = brain or AgentBrain()
        self.link_extractor = link_extractor or LinkExtractor()
        self.anomaly_detector = anomaly_detector or AnomalyDetector()
        self.verification = verification or VerificationEngine()
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

            # Self-correction check: if no URLs discovered, ask brain to rephrase query
            if not urls:
                logger.info("0 sources found, invoking Agent Brain for recovery...")
                diagnosis = await self.brain.diagnose_and_recover(
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
                run.error = "Discovery failed: no relevant web sources could be identified."
                run.finished_at = datetime.now(timezone.utc)
                db.commit()
                return run

            # ────────────────────────────────────────────────
            # 2. RETRIEVAL STAGE (Resilient Proxy & 2-Hop Detail Links)
            # ────────────────────────────────────────────────
            run.status = RunStatus.retrieving
            db.commit()

            pages = await self.retrieval.retrieve_many(
                urls, country_code=plan.country_code, concurrency=4
            )

            # Self-correction / Autonomous 2-hop navigation
            target_detail_urls: list[str] = []
            for url, content in pages.items():
                if content:
                    child_links = self.link_extractor.extract_child_links(url, content, max_links=3)
                    if child_links:
                        logger.info(f"2-hop navigation: found {len(child_links)} child detail URL(s) from {url}")
                        target_detail_urls.extend(child_links)
                    else:
                        target_detail_urls.append(url)
                else:
                    target_detail_urls.append(url)

            # Deduplicate target detail URLs
            seen_targets = set()
            deduped_targets = []
            for t in target_detail_urls:
                if t not in seen_targets:
                    seen_targets.add(t)
                    deduped_targets.append(t)

            if len(deduped_targets) > len(urls):
                logger.info(f"Retrieving {len(deduped_targets)} detail pages following 2-hop expansion...")
                pages = await self.retrieval.retrieve_many(
                    deduped_targets, country_code=plan.country_code, concurrency=4
                )

            run.pages_retrieved = len([p for p in pages.values() if p])
            db.commit()

            # ────────────────────────────────────────────────
            # 3. EXTRACTION STAGE (Schema-Driven)
            # ────────────────────────────────────────────────
            run.status = RunStatus.extracting
            db.commit()

            extracted_records: list[dict[str, Any]] = []

            for url, content in pages.items():
                if not content:
                    continue

                record = await self.extractor.extract(url, content, plan)

                # Self-correction check: if extraction completely failed, ask brain for fallback strategy
                if not record.get("extracted", True):
                    diagnosis = await self.brain.diagnose_and_recover(
                        stage="extraction",
                        error=f"Empty extraction payload from {url}",
                        plan=plan,
                        sources=[url],
                    )
                    reasoning_trail.append({"stage": "extraction", "url": url, "decision": diagnosis})

                extracted_records.append(record)

            run.extracted_count = len(extracted_records)
            db.commit()

            # ────────────────────────────────────────────────
            # 4. VALIDATION & ANOMALY DETECTION
            # ────────────────────────────────────────────────
            run.status = RunStatus.validating
            db.commit()

            # Statistical anomaly check across all numeric fields in plan schema
            annotated_records = self.anomaly_detector.filter_and_annotate_outliers(
                extracted_records, plan=plan
            )

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
            has_persisted = True
            if valid_records:
                try:
                    await self.export_sink.export_results(automation.id, run.id, valid_records)
                except Exception as e:  # noqa: BLE001
                    logger.warning(f"Export sink notification error: {e}")
                    has_persisted = False

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
            # 6. TIMEZONE-AWARE WALL-CLOCK SCHEDULING
            # ────────────────────────────────────────────────
            next_run = None
            if automation.active and plan.frequency != Frequency.once:
                next_run = calculate_next_run(
                    frequency=plan.frequency,
                    schedule_time=plan.schedule_time,
                    tz_name=plan.timezone,
                )
                if next_run:
                    automation.next_run_at = next_run
                    db.commit()

            # ────────────────────────────────────────────────
            # 7. VERIFICATION STAGE (Concept Note Section 6.10)
            # ────────────────────────────────────────────────
            verification_report = self.verification.verify_run(
                plan=plan,
                sources=urls,
                pages=pages,
                extracted_records=extracted_records,
                validated_records=valid_records,
                results_persisted=has_persisted,
                next_run_at=automation.next_run_at,
            )

            reasoning_trail.append({"stage": "verification", "report": verification_report.to_dict()})
            run.reasoning_log = reasoning_trail

            if verification_report.verified:
                run.status = RunStatus.verified
            else:
                if valid_count == 0:
                    run.status = RunStatus.failed
                    run.error = f"Verification failed: 0 records passed validation. ({verification_report.summary})"
                else:
                    run.status = RunStatus.verified

            run.finished_at = datetime.now(timezone.utc)
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
                Run.validated_count > 0,
            )
            .order_by(Run.started_at.desc())
            .first()
        )
        if not last_run:
            return []

        return [
            {"url": r.url, "data": r.data, "valid": r.valid}
            for r in last_run.results
            if r.valid
        ]

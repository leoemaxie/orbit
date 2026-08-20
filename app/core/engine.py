from datetime import datetime, timezone, timedelta

from sqlalchemy.orm import Session

from app.models.orm import Automation, Run, Result, RunStatus
from app.core.discovery import discover_sources
from app.core.retrieval import retrieve_pages
from app.core.extraction import extract_fields
from app.core.validation import validate_record


FREQUENCY_DELTAS = {
    "hourly": timedelta(hours=1),
    "daily": timedelta(days=1),
    "weekly": timedelta(weeks=1),
    "once": None,
}


async def execute_automation(db: Session, automation: Automation) -> Run:
    """
    Runs the full Orbit Core pipeline once for a given automation:
    discover -> retrieve -> extract -> validate -> store -> verify -> schedule next.

    One retry is attempted per URL on retrieval failure (simple recovery, not a
    full diagnosis engine — appropriate for Phase 1 scope).
    """
    spec = automation.spec  # dict, matches AutomationSpec shape

    run = Run(automation_id=automation.id, status=RunStatus.discovering)
    db.add(run)
    db.commit()
    db.refresh(run)

    try:
        # 1. Discover
        urls = await discover_sources(
            product_query=spec["product_query"],
            geography=spec.get("geography", "Nigeria"),
        )
        run.sources_found = urls
        run.status = RunStatus.retrieving
        db.commit()

        if not urls:
            run.status = RunStatus.failed
            run.error = "No sources discovered for this product/geography combination."
            run.finished_at = datetime.now(timezone.utc)
            db.commit()
            return run

        # 2. Retrieve (with one retry pass for failures — simple recovery)
        pages = await retrieve_pages(urls)
        failed_urls = [u for u, content in pages.items() if content is None]
        if failed_urls:
            retry_pages = await retrieve_pages(failed_urls)
            pages.update(retry_pages)

        retrieved_urls = [u for u, content in pages.items() if content is not None]
        run.pages_retrieved = retrieved_urls
        run.status = RunStatus.extracting
        db.commit()

        # 3. Extract
        extracted_records = []
        for url, markdown in pages.items():
            record = await extract_fields(url, markdown)
            extracted_records.append(record)
        run.extracted_count = str(len(extracted_records))
        run.status = RunStatus.validating
        db.commit()

        # 4. Validate + 5. Store
        valid_count = 0
        for record in extracted_records:
            is_valid, errors = validate_record(record)
            if is_valid:
                valid_count += 1
            result = Result(
                run_id=run.id,
                product=record.get("product"),
                price=record.get("price"),
                currency=record.get("currency"),
                availability=record.get("availability"),
                seller=record.get("seller"),
                url=record.get("url"),
                valid=is_valid,
                validation_errors=errors or None,
            )
            db.add(result)

        run.validated_count = str(valid_count)
        run.status = RunStatus.storing
        db.commit()

        # 6. Verify
        if valid_count == 0:
            run.status = RunStatus.failed
            run.error = "No records passed validation."
        else:
            run.status = RunStatus.verified

        run.finished_at = datetime.now(timezone.utc)
        db.commit()

        # 7. Schedule next execution
        delta = FREQUENCY_DELTAS.get(spec.get("frequency", "daily"))
        if delta:
            automation.next_run_at = datetime.now(timezone.utc) + delta
            db.commit()

        return run

    except Exception as e:
        run.status = RunStatus.failed
        run.error = str(e)
        run.finished_at = datetime.now(timezone.utc)
        db.commit()
        return run

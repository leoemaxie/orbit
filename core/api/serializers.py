from core.db.orm import Automation, Run
from core.models.execution_plan import ExecutionPlan
from core.models.schemas import AutomationOut, ResultOut, RunOut


def sanitize_error_message(error: str | None) -> str | None:
    """Sanitizes internal driver/database exceptions to avoid leaking SQL or internal parameters."""
    if not error:
        return None
    err_str = str(error)
    if "OperationalError" in err_str or "server closed the connection" in err_str or "connection refused" in err_str:
        return "Database connectivity error: the connection was closed or timed out. Please retry the run."
    if "SQLAlchemyError" in err_str or "[SQL:" in err_str or "psycopg2" in err_str:
        return "A database transaction error occurred during pipeline execution."
    if "IntegrityError" in err_str:
        return "Data integrity constraint violated during record storage."
    return err_str


def automation_to_out(a: Automation) -> AutomationOut:
    return AutomationOut(
        id=a.id,
        raw_goal=a.raw_goal,
        plan=ExecutionPlan.model_validate(a.plan),
        active=a.active,
        created_at=a.created_at.isoformat(),
        next_run_at=a.next_run_at.isoformat() if a.next_run_at else None,
    )


def run_to_out(r: Run) -> RunOut:
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
        error=sanitize_error_message(r.error),
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

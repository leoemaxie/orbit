from core.db.orm import Automation, Run
from core.models.execution_plan import ExecutionPlan
from core.models.schemas import AutomationOut, ResultOut, RunOut


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

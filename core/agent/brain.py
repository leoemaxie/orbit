import logging
from typing import Any

from core.llm.client import DefaultLLMClient
from core.llm.prompts import FAILURE_BRAIN_PROMPT
from core.models.execution_plan import ExecutionPlan

logger = logging.getLogger("core.agent.brain")


class AgentBrain:
    """The agentic cognition and reasoning engine that diagnoses bottlenecks and drives self-correction."""

    llm: DefaultLLMClient

    def __init__(self, llm_client: DefaultLLMClient | None = None):
        self.llm = llm_client or DefaultLLMClient()

    async def diagnose_and_recover(
        self,
        stage: str,
        error: str,
        plan: ExecutionPlan,
        sources: list[str] | None = None,
    ) -> dict[str, Any]:
        prompt = FAILURE_BRAIN_PROMPT.format(
            objective=plan.objective,
            stage=stage,
            error=error,
            sources=str(sources or []),
        )

        try:
            decision = await self.llm.call_json(
                system_prompt="You are Orbit's autonomous brain. Respond in JSON.",
                user_prompt=prompt,
                temperature=0.1,
            )
            logger.info(f"Agent Brain decision for stage '{stage}': {decision}")
            return decision
        except Exception as e:  # noqa: BLE001
            logger.warning(f"Brain call failed: {e}")
            return {
                "diagnosis": f"Failure during {stage}: {error}",
                "can_recover": False,
                "action": "abort",
                "explanation": "Brain unavailable",
            }

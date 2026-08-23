import logging
from typing import Any

from core.llm.openrouter import OpenRouterLLMClient
from core.llm.prompts import FAILURE_REASONER_PROMPT
from core.models.execution_plan import ExecutionPlan

logger = logging.getLogger("core.agent.reasoner")


class AgentReasoner:
    """Diagnoses execution bottlenecks/failures and reasons about autonomous recovery."""

    llm: OpenRouterLLMClient

    def __init__(self, llm_client: OpenRouterLLMClient | None = None):
        self.llm = llm_client or OpenRouterLLMClient()

    async def diagnose_and_recover(
        self,
        stage: str,
        error: str,
        plan: ExecutionPlan,
        sources: list[str] | None = None,
    ) -> dict[str, Any]:
        prompt = FAILURE_REASONER_PROMPT.format(
            objective=plan.objective,
            stage=stage,
            error=error,
            sources=str(sources or []),
        )

        try:
            decision = await self.llm.call_json(
                system_prompt="You are Orbit's autonomous reasoner. Respond in JSON.",
                user_prompt=prompt,
                temperature=0.1,
            )
            logger.info(f"Agent Reasoner decision for stage '{stage}': {decision}")
            return decision
        except Exception as e:  # noqa: BLE001
            logger.warning(f"Reasoner call failed: {e}")
            return {
                "diagnosis": f"Failure during {stage}: {error}",
                "can_recover": False,
                "action": "abort",
                "explanation": "Reasoner unavailable",
            }

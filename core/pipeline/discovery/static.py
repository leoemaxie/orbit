from core.models.execution_plan import ExecutionPlan


class StaticDiscovery:
    """Discovery strategy for explicit target URLs provided directly in plan."""

    async def discover(self, plan: ExecutionPlan, max_results: int = 10) -> list[str]:
        direct_urls = [h for h in plan.source_hints if h.startswith("http://") or h.startswith("https://")]
        return direct_urls[:max_results]

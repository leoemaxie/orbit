import logging

from core.config.settings import get_settings
from core.models.execution_plan import ExecutionPlan
from core.pipeline.discovery.open_search import OpenWebSearchDiscovery
from core.pipeline.discovery.proxy_search import ProxySearchDiscovery
from core.pipeline.discovery.search_engine import SearchEngineDiscovery
from core.pipeline.discovery.static import StaticDiscovery

logger = logging.getLogger("core.pipeline.discovery.composite")


class CompositeDiscovery:
    """
    Decoupled discovery orchestrator that attempts multiple discovery backends in priority order.
    Functions seamlessly across direct URLs, search APIs, open web search, and proxy search.
    """

    def __init__(self):
        self.settings = get_settings()
        self.static_discovery = StaticDiscovery()
        self.open_search = OpenWebSearchDiscovery()
        self.search_engine = SearchEngineDiscovery()
        self.proxy_search = ProxySearchDiscovery()

    async def discover(self, plan: ExecutionPlan, max_results: int = 10) -> list[str]:
        # 1. Direct URLs in source hints
        direct = await self.static_discovery.discover(plan, max_results=max_results)
        if direct:
            logger.info(f"Using {len(direct)} direct URL(s) from plan.")
            return direct

        # 2. Search Engine API (if API key is present)
        if self.settings.serpapi_api_key:
            try:
                urls = await self.search_engine.discover(plan, max_results=max_results)
                if urls:
                    logger.info(f"Search engine discovery returned {len(urls)} URLs.")
                    return urls
            except Exception as e:  # noqa: BLE001
                logger.warning(f"Search engine discovery failed, falling back: {e}")

        # 3. Open web search discovery (zero API key required)
        try:
            urls = await self.open_search.discover(plan, max_results=max_results)
            if urls:
                logger.info(f"Open web search discovery returned {len(urls)} URLs.")
                return urls
        except Exception as e:  # noqa: BLE001
            logger.warning(f"Open web search discovery failed: {e}")

        # 4. Proxy-routed search (if configured)
        if self.settings.brightdata_api_key and self.settings.brightdata_zone:
            try:
                urls = await self.proxy_search.discover(plan, max_results=max_results)
                if urls:
                    logger.info(f"Proxy search discovery returned {len(urls)} URLs.")
                    return urls
            except Exception as e:  # noqa: BLE001
                logger.warning(f"Proxy search discovery failed: {e}")

        return []

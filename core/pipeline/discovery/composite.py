import logging

from core.config.settings import get_settings
from core.models.execution_plan import ExecutionPlan
from core.pipeline.discovery.brightdata_serp import BrightDataSerpDiscovery
from core.pipeline.discovery.duckduckgo import DuckDuckGoDiscovery
from core.pipeline.discovery.serpapi import SerpApiDiscovery
from core.pipeline.discovery.static import StaticDiscovery

logger = logging.getLogger("core.pipeline.discovery.composite")


class CompositeDiscovery:
    """
    Decoupled discovery orchestrator that attempts multiple discovery backends in priority order.
    Functions seamlessly with or without SerpApi.
    """

    def __init__(self):
        self.settings = get_settings()
        self.static_discovery = StaticDiscovery()
        self.duckduckgo = DuckDuckGoDiscovery()
        self.serpapi = SerpApiDiscovery()
        self.brightdata_serp = BrightDataSerpDiscovery()

    async def discover(self, plan: ExecutionPlan, max_results: int = 10) -> list[str]:
        # 1. Direct URLs in source hints
        direct = await self.static_discovery.discover(plan, max_results=max_results)
        if direct:
            logger.info(f"Using {len(direct)} direct URL(s) from plan.")
            return direct

        # 2. SerpApi (if API key is present)
        if self.settings.serpapi_api_key:
            try:
                urls = await self.serpapi.discover(plan, max_results=max_results)
                if urls:
                    logger.info(f"SerpApi discovery returned {len(urls)} URLs.")
                    return urls
            except Exception as e:  # noqa: BLE001
                logger.warning(f"SerpApi discovery failed, falling back: {e}")

        # 3. DuckDuckGo open web discovery (zero API key required)
        try:
            urls = await self.duckduckgo.discover(plan, max_results=max_results)
            if urls:
                logger.info(f"DuckDuckGo zero-key discovery returned {len(urls)} URLs.")
                return urls
        except Exception as e:  # noqa: BLE001
            logger.warning(f"DuckDuckGo discovery failed: {e}")

        # 4. Bright Data SERP (if configured)
        if self.settings.brightdata_api_key and self.settings.brightdata_zone:
            try:
                urls = await self.brightdata_serp.discover(plan, max_results=max_results)
                if urls:
                    logger.info(f"Bright Data SERP discovery returned {len(urls)} URLs.")
                    return urls
            except Exception as e:  # noqa: BLE001
                logger.warning(f"Bright Data SERP discovery failed: {e}")

        return []

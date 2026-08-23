from core.pipeline.discovery.composite import CompositeDiscovery
from core.pipeline.discovery.open_search import OpenWebSearchDiscovery
from core.pipeline.discovery.proxy_search import ProxySearchDiscovery
from core.pipeline.discovery.search_engine import SearchEngineDiscovery
from core.pipeline.discovery.static import StaticDiscovery

__all__ = [
    "CompositeDiscovery",
    "OpenWebSearchDiscovery",
    "ProxySearchDiscovery",
    "SearchEngineDiscovery",
    "StaticDiscovery",
]

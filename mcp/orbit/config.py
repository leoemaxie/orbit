from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class MCPSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    orbit_api_url: str = "http://localhost:8000"
    request_timeout: float = 120.0
    debug: bool = False


@lru_cache
def get_mcp_settings() -> MCPSettings:
    return MCPSettings()

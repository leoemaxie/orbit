from functools import lru_cache
from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class MCPSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    orbit_api_url: str = Field(
        default="http://localhost:8000",
        validation_alias="ORBIT_API_URL",
    )
    request_timeout: float = Field(
        default=120.0,
        validation_alias=AliasChoices("REQUEST_TIMEOUT", "MCP_TIMEOUT"),
    )
    debug: bool = Field(
        default=False,
        validation_alias=AliasChoices("DEBUG", "MCP_DEBUG"),
    )
    mcp_transport: str = Field(
        default="stdio",
        validation_alias=AliasChoices("MCP_TRANSPORT", "TRANSPORT"),
    )
    mcp_host: str = Field(
        default="0.0.0.0",
        validation_alias=AliasChoices("MCP_HOST", "HOST"),
    )
    mcp_port: int = Field(
        default=8001,
        validation_alias=AliasChoices("MCP_PORT", "PORT"),
    )


@lru_cache
def get_mcp_settings() -> MCPSettings:
    return MCPSettings()


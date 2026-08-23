from functools import lru_cache

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Domain-agnostic application and pipeline settings with multi-provider alias support."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Application
    app_env: str = "development"
    app_port: int = 8000
    log_level: str = "INFO"

    # LLM (OpenAI-compatible endpoints e.g. OpenRouter, OpenAI, Local Ollama/vLLM)
    llm_api_key: str = Field(
        "",
        validation_alias=AliasChoices("LLM_API_KEY", "OPENROUTER_API_KEY", "OPENAI_API_KEY"),
        description="API key for LLM inference provider",
    )
    llm_model: str = Field(
        "anthropic/claude-3.5-sonnet",
        validation_alias=AliasChoices("LLM_MODEL", "OPENROUTER_MODEL"),
        description="Target model identifier",
    )
    llm_base_url: str = Field(
        "https://openrouter.ai/api/v1",
        validation_alias=AliasChoices("LLM_BASE_URL", "OPENROUTER_BASE_URL"),
        description="Base URL for OpenAI-compatible LLM endpoint",
    )

    # Web Data Retrieval & Resilient Proxy
    retrieval_api_key: str = Field(
        "",
        validation_alias=AliasChoices("RETRIEVAL_API_KEY", "PROXY_API_KEY", "BRIGHTDATA_API_KEY"),
        description="API key or credentials for proxy/unblocker service",
    )
    retrieval_zone: str = Field(
        "",
        validation_alias=AliasChoices("RETRIEVAL_ZONE", "PROXY_ZONE", "BRIGHTDATA_ZONE"),
        description="Zone or gateway identifier for proxy routing",
    )
    retrieval_base_url: str = Field(
        "https://api.brightdata.com",
        validation_alias=AliasChoices("RETRIEVAL_BASE_URL", "PROXY_BASE_URL", "BRIGHTDATA_BASE_URL"),
        description="Base endpoint URL for web data retrieval proxy",
    )

    # Web Discovery & Search Engine API
    search_engine_api_key: str = Field(
        "",
        validation_alias=AliasChoices("SEARCH_ENGINE_API_KEY", "DISCOVERY_API_KEY", "SERPAPI_API_KEY"),
        description="API key for structured search engine discovery",
    )
    search_engine_base_url: str = Field(
        "https://serpapi.com/search.json",
        validation_alias=AliasChoices("SEARCH_ENGINE_BASE_URL", "DISCOVERY_BASE_URL"),
        description="Endpoint URL for search engine API queries",
    )

    # Database
    database_url: str = "postgresql+psycopg2://orbit:orbit@localhost:5432/orbit"

    # Scheduler
    enable_scheduler: bool = True

    # Notification & Webhooks
    default_webhook_url: str | None = None

    # Backward compatibility accessors
    @property
    def openrouter_api_key(self) -> str:
        return self.llm_api_key

    @property
    def openrouter_model(self) -> str:
        return self.llm_model

    @property
    def openrouter_base_url(self) -> str:
        return self.llm_base_url

    @property
    def brightdata_api_key(self) -> str:
        return self.retrieval_api_key

    @property
    def brightdata_zone(self) -> str:
        return self.retrieval_zone

    @property
    def brightdata_base_url(self) -> str:
        return self.retrieval_base_url

    @property
    def serpapi_api_key(self) -> str:
        return self.search_engine_api_key


@lru_cache
def get_settings() -> Settings:
    return Settings()

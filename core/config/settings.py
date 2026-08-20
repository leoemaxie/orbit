from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Application
    app_env: str = "development"
    app_port: int = 8000
    log_level: str = "INFO"

    # LLM (via OpenRouter or standard OpenAI-compatible endpoints)
    openrouter_api_key: str = ""
    openrouter_model: str = "anthropic/claude-3.5-sonnet"
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    # Web Data Retrieval
    brightdata_api_key: str = ""
    brightdata_zone: str = ""
    brightdata_base_url: str = "https://api.brightdata.com"

    # Web Discovery
    serpapi_api_key: str = ""

    # Database
    database_url: str = "postgresql+psycopg2://orbit:orbit@localhost:5432/orbit"

    # Scheduler
    enable_scheduler: bool = True

    # Notification & Webhooks
    default_webhook_url: Optional[str] = None


@lru_cache
def get_settings() -> Settings:
    return Settings()

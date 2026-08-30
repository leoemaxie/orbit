from functools import lru_cache

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Domain-agnostic application and pipeline settings with multi-provider alias support."""

    model_config = SettingsConfigDict(env_file=(".env", "core/.env"), extra="ignore")

    app_env: str = "development"
    app_port: int = 8000
    log_level: str = "INFO"

    # LLM
    llm_provider: str = Field(default="gemini", validation_alias=AliasChoices("LLM_PROVIDER", "AI_PROVIDER"))
    llm_api_key: str = Field(default="", validation_alias=AliasChoices("LLM_API_KEY"))
    llm_model: str = Field(default="gemini-2.5-flash", validation_alias=AliasChoices("LLM_MODEL"))
    llm_base_url: str = Field(default="https://openrouter.ai/api/v1", validation_alias=AliasChoices("LLM_BASE_URL"))

    # Web Data Retrieval & Discovery
    retrieval_api_key: str = Field(default="", validation_alias=AliasChoices("RETRIEVAL_API_KEY", "PROXY_API_KEY", "BRIGHTDATA_API_KEY"))
    retrieval_zone: str = Field(default="", validation_alias=AliasChoices("RETRIEVAL_ZONE", "PROXY_ZONE", "BRIGHTDATA_ZONE"))
    retrieval_base_url: str = Field(default="https://api.brightdata.com", validation_alias=AliasChoices("RETRIEVAL_BASE_URL", "PROXY_BASE_URL"))
    search_engine_api_key: str = Field(default="", validation_alias=AliasChoices("SEARCH_ENGINE_API_KEY", "DISCOVERY_API_KEY", "SERPAPI_API_KEY"))
    search_engine_base_url: str = Field(default="https://serpapi.com/search.json", validation_alias=AliasChoices("SEARCH_ENGINE_BASE_URL", "DISCOVERY_BASE_URL"))

    # Database & Scheduler
    database_url: str = Field(default="postgresql+psycopg2://orbit:orbit@localhost:5432/orbit", validation_alias=AliasChoices("DATABASE_URL", "DB_URL"))
    enable_scheduler: bool = True
    scheduler_secret: str = Field(default="", validation_alias=AliasChoices("SCHEDULER_SECRET", "SCHEDULER_API_KEY", "CRON_SECRET"))

    # Document Processing (Provider-Agnostic)
    document_converter_api_key: str = Field(default="", validation_alias=AliasChoices("DOCUMENT_CONVERTER_API_KEY", "FOXIT_API_KEY"))
    document_converter_base_url: str = "https://api.foxit.com/v1"
    document_generator_api_key: str = Field(default="", validation_alias=AliasChoices("DOCUMENT_GENERATOR_API_KEY", "NUTRIENT_API_KEY"))
    document_generator_base_url: str = "https://api.nutrient.io"
    document_redactor_api_key: str = Field(default="", validation_alias=AliasChoices("DOCUMENT_REDACTOR_API_KEY", "NUTRIENT_API_KEY"))
    document_redactor_base_url: str = "https://api.nutrient.io"

    # Email Notifications (Provider-Agnostic Managed Outbound Gateway)
    email_api_key: str = Field(default="", validation_alias=AliasChoices("EMAIL_API_KEY", "MAIL_API_KEY", "SMTP_API_KEY"))
    email_sender_address: str = Field(default="Orbit Alerts <alerts@orbit.dev>", validation_alias=AliasChoices("EMAIL_SENDER_ADDRESS", "EMAIL_FROM", "MAIL_FROM"))
    email_base_url: str = Field(default="https://api.orbit.dev/v1/emails", validation_alias=AliasChoices("EMAIL_BASE_URL", "MAIL_BASE_URL"))

    # Message Broker & Distributed Lock (Provider-Agnostic with orb: key prefix)
    event_broker_backend: str = Field(default="memory", validation_alias=AliasChoices("EVENT_BROKER_BACKEND", "BROKER_BACKEND", "EVENT_BROKER"))
    broker_url: str = Field(default="redis://localhost:6379/0", validation_alias=AliasChoices("BROKER_URL", "REDIS_URL", "MESSAGE_BROKER_URL"))
    broker_project_id: str = Field(default="", validation_alias=AliasChoices("BROKER_PROJECT_ID", "GCP_PROJECT_ID", "CLOUD_PROJECT_ID"))
    broker_key_prefix: str = Field(default="orb", validation_alias=AliasChoices("BROKER_KEY_PREFIX", "REDIS_KEY_PREFIX", "KEY_PREFIX"))

    # Unified Caching (Provider-Agnostic with Memory/Redis backends)
    cache_backend: str = Field(default="memory", validation_alias=AliasChoices("CACHE_BACKEND", "CACHE_TYPE"))
    cache_url: str = Field(default="redis://localhost:6379/1", validation_alias=AliasChoices("CACHE_URL", "REDIS_CACHE_URL"))
    cache_enabled: bool = Field(default=True, validation_alias=AliasChoices("CACHE_ENABLED", "ENABLE_CACHE"))
    cache_default_ttl: int = Field(default=300, validation_alias=AliasChoices("CACHE_DEFAULT_TTL", "CACHE_TTL"))



    @property
    def brightdata_api_key(self) -> str: return self.retrieval_api_key
    @property
    def brightdata_zone(self) -> str: return self.retrieval_zone
    @property
    def brightdata_base_url(self) -> str: return self.retrieval_base_url
    @property
    def serpapi_api_key(self) -> str: return self.search_engine_api_key


@lru_cache
def get_settings() -> Settings:
    return Settings()

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
    llm_api_key: str = Field("", validation_alias=AliasChoices("LLM_API_KEY", "OPENROUTER_API_KEY", "OPENAI_API_KEY"))
    llm_model: str = Field("anthropic/claude-3.5-sonnet", validation_alias=AliasChoices("LLM_MODEL", "OPENROUTER_MODEL"))
    llm_base_url: str = Field("https://openrouter.ai/api/v1", validation_alias=AliasChoices("LLM_BASE_URL", "OPENROUTER_BASE_URL"))

    # Web Data Retrieval & Discovery
    retrieval_api_key: str = Field("", validation_alias=AliasChoices("RETRIEVAL_API_KEY", "PROXY_API_KEY", "BRIGHTDATA_API_KEY"))
    retrieval_zone: str = Field("", validation_alias=AliasChoices("RETRIEVAL_ZONE", "PROXY_ZONE", "BRIGHTDATA_ZONE"))
    retrieval_base_url: str = Field("https://api.brightdata.com", validation_alias=AliasChoices("RETRIEVAL_BASE_URL", "PROXY_BASE_URL"))
    search_engine_api_key: str = Field("", validation_alias=AliasChoices("SEARCH_ENGINE_API_KEY", "DISCOVERY_API_KEY", "SERPAPI_API_KEY"))
    search_engine_base_url: str = Field("https://serpapi.com/search.json", validation_alias=AliasChoices("SEARCH_ENGINE_BASE_URL", "DISCOVERY_BASE_URL"))

    # Database & Scheduler
    database_url: str = "postgresql+psycopg2://orbit:orbit@localhost:5432/orbit"
    enable_scheduler: bool = True
    scheduler_secret: str = Field("", validation_alias=AliasChoices("SCHEDULER_SECRET", "SCHEDULER_API_KEY", "CRON_SECRET"))
    default_webhook_url: str | None = None
    webhook_signing_secret: str = Field("orbit-webhook-secret-key", validation_alias=AliasChoices("WEBHOOK_SIGNING_SECRET", "WEBHOOK_SECRET"))

    # Document Processing (Provider-Agnostic)
    document_converter_api_key: str = Field("", validation_alias=AliasChoices("DOCUMENT_CONVERTER_API_KEY", "FOXIT_API_KEY"))
    document_converter_base_url: str = "https://api.foxit.com/v1"
    document_generator_api_key: str = Field("", validation_alias=AliasChoices("DOCUMENT_GENERATOR_API_KEY", "NUTRIENT_API_KEY"))
    document_generator_base_url: str = "https://api.nutrient.io/v1"
    document_redactor_api_key: str = Field("", validation_alias=AliasChoices("DOCUMENT_REDACTOR_API_KEY", "NUTRIENT_API_KEY"))
    document_redactor_base_url: str = "https://api.nutrient.io/v1"

    # Cloud Storage Sinks (S3 / MinIO)
    s3_bucket_name: str = "orbit-exports"
    s3_endpoint_url: str | None = None
    s3_access_key: str = Field("", validation_alias=AliasChoices("S3_ACCESS_KEY", "AWS_ACCESS_KEY_ID"))
    s3_secret_key: str = Field("", validation_alias=AliasChoices("S3_SECRET_KEY", "AWS_SECRET_ACCESS_KEY"))
    s3_region: str = "us-east-1"

    # Backward compatibility accessors
    @property
    def openrouter_api_key(self) -> str: return self.llm_api_key
    @property
    def openrouter_model(self) -> str: return self.llm_model
    @property
    def openrouter_base_url(self) -> str: return self.llm_base_url
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

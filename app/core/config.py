from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # LLM
    openrouter_api_key: str
    openrouter_model: str = "nvidia/nemotron-3-ultra:free"
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    # Web data
    brightdata_api_key: str
    brightdata_zone: str
    brightdata_base_url: str = "https://api.brightdata.com"
    serpapi_api_key: str

    database_url: str = "postgresql+psycopg2://orbit:orbit@localhost:5432/orbit"
    orbit_allowed_retailers: str = "jumia.com.ng,konga.com,slot.ng,pointekonline.com"

    @property
    def allowed_retailer_list(self) -> list[str]:
        return [d.strip() for d in self.orbit_allowed_retailers.split(",") if d.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()

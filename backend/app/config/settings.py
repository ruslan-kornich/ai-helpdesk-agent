from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite+aiosqlite:///:memory:"

    openai_api_key: str = ""
    openai_model: str = "gpt-4o"

    telegram_bot_token: str = ""

    zendesk_subdomain: str = ""
    zendesk_email: str = ""
    zendesk_api_token: str = ""

    working_hours_start: int = 9
    working_hours_end: int = 18
    timezone: str = "Europe/Kyiv"

    support_lead_channel: str = ""

    session_window_minutes: int = 30
    confidence_threshold: float = 0.55


@lru_cache
def get_settings() -> Settings:
    return Settings()

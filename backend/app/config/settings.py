from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "postgresql+asyncpg://gatum:gatum@db:5432/gatum"

    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"

    TELEGRAM_BOT_TOKEN: str = ""

    ZENDESK_SUBDOMAIN: str = ""
    ZENDESK_EMAIL: str = ""
    ZENDESK_API_TOKEN: str = ""

    WORKING_HOURS_START: int = 9
    WORKING_HOURS_END: int = 18
    TIMEZONE: str = "Europe/Kyiv"

    SUPPORT_LEAD_CHANNEL: str = ""

    SESSION_WINDOW_MINUTES: int = 30
    CONFIDENCE_THRESHOLD: float = 0.55


@lru_cache
def get_settings() -> Settings:
    return Settings()

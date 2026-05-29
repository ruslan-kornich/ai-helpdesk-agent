from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "postgresql+asyncpg://gatum:gatum@db:5432/gatum"

    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4.1"

    TELEGRAM_BOT_TOKEN: str = ""

    LOG_LEVEL: str = "INFO"

    ZENDESK_SUBDOMAIN: str = ""
    ZENDESK_EMAIL: str = ""
    ZENDESK_API_TOKEN: str = ""
    ZENDESK_POLL_INTERVAL_SECONDS: int = 15

    WORKING_HOURS_START: int = 9
    WORKING_HOURS_END: int = 18
    TIMEZONE: str = "Europe/Kyiv"

    SUPPORT_LEAD_CHANNEL: str = ""

    SESSION_WINDOW_MINUTES: int = 30
    CONFIDENCE_THRESHOLD: float = 0.55

    JWT_SECRET: str = "CHANGE_ME"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7


@lru_cache
def get_settings() -> Settings:
    return Settings()

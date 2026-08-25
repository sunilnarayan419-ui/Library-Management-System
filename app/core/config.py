"""Application configuration loaded from environment variables."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central application settings. All values are overridable via env vars."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    app_debug: bool = False
    app_name: str = "Library Management System"
    app_version: str = "5.0.0"

    database_url: str = "sqlite:///./data/library.db"

    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    ai_provider: str = "mock"
    ai_api_key: str = ""
    ai_model: str = "claude-sonnet-4-6"

    default_loan_period_days: int = 14
    max_renewals: int = 2
    fine_per_day: float = 5.0

    rate_limit_per_minute: int = 120

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()

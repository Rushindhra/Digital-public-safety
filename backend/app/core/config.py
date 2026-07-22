"""
Central application configuration.

All configuration is environment-driven (12-factor). Nothing here is a
hardcoded secret — defaults are safe only for local dev and are expected
to be overridden via .env / real secrets manager in staging/prod.
"""
from functools import lru_cache
from typing import List

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- App ---
    APP_NAME: str = "Digital Public Safety Intelligence Platform"
    APP_ENV: str = "development"  # development | staging | production
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # --- Security ---
    SECRET_KEY: str = "dev-secret-change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # --- CORS ---
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # --- Database (MongoDB) ---
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "digital_public_safety"
    MONGODB_SERVER_SELECTION_TIMEOUT_MS: int = 5_000

    # --- Redis ---
    REDIS_URL: str = "redis://localhost:6379/0"

    # --- Vector DB ---
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_COLLECTION: str = "citizen_safety_kb"

    # --- Rate limiting ---
    RATE_LIMIT_DEFAULT: str = "100/minute"

    # --- File storage ---
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_MB: int = 15

    # --- Bootstrap administrator (change in production) ---
    ADMIN_EMAIL: str = "admin@suraksha.gov.in"
    ADMIN_PASSWORD: str = "Admin@12345"
    ADMIN_FULL_NAME: str = "Platform Administrator"

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug(cls, value):
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"1", "true", "yes", "on", "debug"}: return True
            if normalized in {"0", "false", "no", "off", "release", "production"}: return False
        return value

    @model_validator(mode="after")
    def validate_production_secrets(self):
        if self.APP_ENV == "production":
            if len(self.SECRET_KEY) < 32 or self.SECRET_KEY.startswith("dev-") or "change-this" in self.SECRET_KEY:
                raise ValueError("Production SECRET_KEY must be a unique value of at least 32 characters")
            if self.ADMIN_PASSWORD == "Admin@12345":
                raise ValueError("Production ADMIN_PASSWORD must be changed")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

"""Application settings — loaded from environment variables."""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "AI Crypto Fraud Intelligence Platform"
    app_version: str = "1.0.0"
    environment: str = "development"  # development | production
    debug: bool = False

    host: str = "0.0.0.0"
    port: int = 8000

    mongo_uri: str = "mongodb://localhost:27017"
    mongo_db: str = "crypto_fraud_intel"

    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    rate_limit: str = "60/minute"
    ws_alert_interval: float = 10.0

    @property
    def cors_origin_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()

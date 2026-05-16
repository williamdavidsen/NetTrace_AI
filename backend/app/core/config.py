import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    service_name: str = os.getenv("SERVICE_NAME", "nettrace-backend")
    app_env: str = os.getenv("APP_ENV", "development")
    api_v1_prefix: str = os.getenv("API_V1_PREFIX", "/api/v1")
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://nettrace:nettrace@localhost:5432/nettrace",
    )
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    redis_stream_name: str = os.getenv("REDIS_STREAM_NAME", "network_events")


settings = Settings()

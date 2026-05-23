import os
from dataclasses import dataclass


def _csv(value: str) -> tuple[str, ...]:
    return tuple(item.strip() for item in value.split(",") if item.strip())


@dataclass(frozen=True)
class Settings:
    service_name: str = os.getenv("SERVICE_NAME", "nettrace-backend")
    app_env: str = os.getenv("APP_ENV", "development")
    log_level: str = os.getenv("LOG_LEVEL", "info")
    api_v1_prefix: str = os.getenv("API_V1_PREFIX", "/api/v1")
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://nettrace:nettrace@localhost:5432/nettrace",
    )
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    redis_stream_name: str = os.getenv("REDIS_STREAM_NAME", "network_events")
    cors_origins: tuple[str, ...] = _csv(
        os.getenv("BACKEND_CORS_ORIGINS", "http://localhost:3000")
    )
    rate_limit_enabled: bool = os.getenv("BACKEND_RATE_LIMIT_ENABLED", "true").lower() == "true"
    rate_limit_requests: int = int(os.getenv("BACKEND_RATE_LIMIT_REQUESTS", "120"))
    rate_limit_window_seconds: int = int(os.getenv("BACKEND_RATE_LIMIT_WINDOW_SECONDS", "60"))


settings = Settings()

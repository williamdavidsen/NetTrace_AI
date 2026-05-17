from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from app.api.v1.router import router as api_v1_router
from app.core.config import settings
from app.db.session import get_session
from app.schemas import MetricsResponse
from app.services import get_metrics


def create_app() -> FastAPI:
    app = FastAPI(
        title="NetTrace AI Backend",
        version="0.1.0",
        description="Backend API for NetTrace AI.",
    )

    @app.get("/health")
    def health_check() -> dict[str, str]:
        return {
            "status": "ok",
            "service": settings.service_name,
        }

    @app.get("/metrics", response_model=MetricsResponse)
    def metrics(session: Session = Depends(get_session)) -> MetricsResponse:
        return get_metrics(session=session)

    app.include_router(api_v1_router, prefix=settings.api_v1_prefix)
    return app


app = create_app()

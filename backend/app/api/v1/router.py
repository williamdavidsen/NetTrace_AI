from fastapi import APIRouter

from app.core.config import settings

router = APIRouter()


@router.get("/status")
def get_status() -> dict[str, str]:
    return {
        "status": "ok",
        "service": settings.service_name,
        "environment": settings.app_env,
    }

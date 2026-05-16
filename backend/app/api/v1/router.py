from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_session
from app.schemas import AlertResponse, PacketEventCreate, PacketEventResponse
from app.services import create_packet_event, list_alerts

router = APIRouter()


@router.get("/status")
def get_status() -> dict[str, str]:
    return {
        "status": "ok",
        "service": settings.service_name,
        "environment": settings.app_env,
    }


@router.post(
    "/events",
    response_model=PacketEventResponse,
    status_code=status.HTTP_201_CREATED,
)
def ingest_event(
    payload: PacketEventCreate,
    session: Session = Depends(get_session),
) -> PacketEventResponse:
    return create_packet_event(session=session, payload=payload)


@router.get("/alerts", response_model=list[AlertResponse])
def get_alerts(
    scan_id: UUID | None = None,
    session: Session = Depends(get_session),
) -> list[AlertResponse]:
    return list_alerts(session=session, scan_id=scan_id)

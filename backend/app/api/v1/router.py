from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends, Query, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_session
from app.schemas import (
    AlertExplanationResponse,
    AlertResponse,
    PacketEventCreate,
    PacketEventResponse,
    ScanCreate,
    ScanResponse,
)
from app.services import (
    complete_scan,
    create_packet_event,
    create_scan,
    explain_alert,
    get_alert_or_404,
    get_scan_or_404,
    list_alerts,
    list_alerts_for_scan,
    list_packet_events_for_scan,
    list_scans,
)
from app.streams import RedisEventStream, get_event_stream

router = APIRouter()


@router.get("/status")
def get_status() -> dict[str, str]:
    return {
        "status": "ok",
        "service": settings.service_name,
        "environment": settings.app_env,
    }


@router.post(
    "/scans",
    response_model=ScanResponse,
    status_code=status.HTTP_201_CREATED,
)
def start_scan(
    payload: ScanCreate,
    session: Session = Depends(get_session),
) -> ScanResponse:
    return create_scan(session=session, payload=payload)


@router.get("/scans", response_model=list[ScanResponse])
def get_scans(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    session: Session = Depends(get_session),
) -> list[ScanResponse]:
    return list_scans(session=session, limit=limit, offset=offset)


@router.get("/scans/{scan_id}", response_model=ScanResponse)
def get_scan(
    scan_id: UUID,
    session: Session = Depends(get_session),
) -> ScanResponse:
    return get_scan_or_404(session=session, scan_id=scan_id)


@router.patch("/scans/{scan_id}/complete", response_model=ScanResponse)
def mark_scan_complete(
    scan_id: UUID,
    session: Session = Depends(get_session),
) -> ScanResponse:
    return complete_scan(session=session, scan_id=scan_id)


@router.get("/scans/{scan_id}/events", response_model=list[PacketEventResponse])
def get_scan_events(
    scan_id: UUID,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    session: Session = Depends(get_session),
) -> list[PacketEventResponse]:
    return list_packet_events_for_scan(session=session, scan_id=scan_id, limit=limit, offset=offset)


@router.get("/scans/{scan_id}/alerts", response_model=list[AlertResponse])
def get_scan_alerts(
    scan_id: UUID,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    session: Session = Depends(get_session),
) -> list[AlertResponse]:
    return list_alerts_for_scan(session=session, scan_id=scan_id, limit=limit, offset=offset)


@router.post(
    "/events",
    response_model=PacketEventResponse,
    status_code=status.HTTP_201_CREATED,
)
def ingest_event(
    payload: PacketEventCreate,
    session: Session = Depends(get_session),
    event_stream: RedisEventStream = Depends(get_event_stream),
) -> PacketEventResponse:
    return create_packet_event(session=session, payload=payload, event_stream=event_stream)


@router.get("/alerts", response_model=list[AlertResponse])
def get_alerts(
    scan_id: UUID | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    session: Session = Depends(get_session),
) -> list[AlertResponse]:
    return list_alerts(session=session, scan_id=scan_id, limit=limit, offset=offset)


@router.get("/alerts/{alert_id}", response_model=AlertResponse)
def get_alert(
    alert_id: UUID,
    session: Session = Depends(get_session),
) -> AlertResponse:
    return get_alert_or_404(session=session, alert_id=alert_id)


@router.get("/alerts/{alert_id}/explanation", response_model=AlertExplanationResponse)
def get_alert_explanation(
    alert_id: UUID,
    session: Session = Depends(get_session),
) -> AlertExplanationResponse:
    alert = get_alert_or_404(session=session, alert_id=alert_id)
    return explain_alert(alert)

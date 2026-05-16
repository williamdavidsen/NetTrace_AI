from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import PacketEvent, Scan
from app.schemas import PacketEventCreate
from app.services.detection import detect_alerts_for_event
from app.streams import EventStreamPublishError, RedisEventStream


def create_packet_event(
    session: Session,
    payload: PacketEventCreate,
    event_stream: RedisEventStream,
) -> PacketEvent:
    scan = session.get(Scan, str(payload.scan_id))
    if scan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found for event payload.",
        )

    event = PacketEvent(
        scan_id=str(payload.scan_id),
        timestamp=payload.timestamp,
        source_ip=payload.source_ip,
        destination_ip=payload.destination_ip,
        protocol=payload.protocol,
        source_port=payload.source_port,
        destination_port=payload.destination_port,
        packet_size=payload.packet_size,
    )
    session.add(event)
    session.flush()

    alerts = detect_alerts_for_event(session=session, event=event)
    session.add_all(alerts)

    try:
        event_stream.publish_packet_event(event)
    except EventStreamPublishError as exc:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Event stream unavailable.",
        ) from exc

    session.commit()
    session.refresh(event)
    return event

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import PacketEvent
from app.services.scans import get_scan_or_404


def list_packet_events_for_scan(
    *,
    session: Session,
    scan_id: UUID,
    limit: int,
    offset: int,
) -> list[PacketEvent]:
    get_scan_or_404(session=session, scan_id=scan_id)
    statement = (
        select(PacketEvent)
        .where(PacketEvent.scan_id == str(scan_id))
        .order_by(PacketEvent.timestamp.desc(), PacketEvent.id.desc())
        .offset(offset)
        .limit(limit)
    )
    return list(session.scalars(statement).all())

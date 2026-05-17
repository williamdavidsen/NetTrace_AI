from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Alert
from app.services.scans import get_scan_or_404


def list_alerts(
    session: Session,
    scan_id: UUID | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[Alert]:
    statement = select(Alert).order_by(Alert.created_at.desc(), Alert.id.desc()).offset(offset).limit(limit)
    if scan_id is not None:
        statement = statement.where(Alert.scan_id == str(scan_id))
    return list(session.scalars(statement).all())


def list_alerts_for_scan(
    *,
    session: Session,
    scan_id: UUID,
    limit: int,
    offset: int,
) -> list[Alert]:
    get_scan_or_404(session=session, scan_id=scan_id)
    return list_alerts(session=session, scan_id=scan_id, limit=limit, offset=offset)


def get_alert_or_404(session: Session, alert_id: UUID) -> Alert:
    alert = session.get(Alert, str(alert_id))
    if alert is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found.",
        )
    return alert

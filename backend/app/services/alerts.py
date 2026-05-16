from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Alert


def list_alerts(session: Session, scan_id: UUID | None = None) -> list[Alert]:
    statement = select(Alert).order_by(Alert.created_at.desc(), Alert.id.desc())
    if scan_id is not None:
        statement = statement.where(Alert.scan_id == str(scan_id))
    return list(session.scalars(statement).all())

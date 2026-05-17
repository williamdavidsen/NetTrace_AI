from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Scan
from app.schemas import ScanCreate


def create_scan(session: Session, payload: ScanCreate) -> Scan:
    scan = Scan(target_name=payload.target_name.strip(), status="running")
    session.add(scan)
    session.commit()
    session.refresh(scan)
    return scan


def list_scans(session: Session, limit: int, offset: int) -> list[Scan]:
    statement = (
        select(Scan)
        .order_by(Scan.created_at.desc(), Scan.id.desc())
        .offset(offset)
        .limit(limit)
    )
    return list(session.scalars(statement).all())


def get_scan_or_404(session: Session, scan_id: UUID) -> Scan:
    scan = session.get(Scan, str(scan_id))
    if scan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found.",
        )
    return scan


def complete_scan(session: Session, scan_id: UUID) -> Scan:
    scan = get_scan_or_404(session=session, scan_id=scan_id)
    scan.status = "completed"
    scan.finished_at = datetime.now(timezone.utc)
    session.commit()
    session.refresh(scan)
    return scan

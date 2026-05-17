from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Alert, PacketEvent, Scan


def get_metrics(session: Session) -> dict[str, int]:
    processed_events_total = session.scalar(select(func.count(PacketEvent.id))) or 0
    generated_alerts_total = session.scalar(select(func.count(Alert.id))) or 0
    active_scans_total = session.scalar(select(func.count(Scan.id)).where(Scan.status == "running")) or 0

    return {
        "processed_events_total": int(processed_events_total),
        "generated_alerts_total": int(generated_alerts_total),
        "active_scans_total": int(active_scans_total),
    }

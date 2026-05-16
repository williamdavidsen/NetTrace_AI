from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Alert, PacketEvent, Scan
from app.services.detection import detect_alerts_for_event


def test_detection_flags_sensitive_destination_port(db_session: Session) -> None:
    scan = Scan(target_name="sensitive-port", status="running")
    event = _event(scan=scan, destination_port=3389)
    db_session.add(event)
    db_session.commit()

    alerts = detect_alerts_for_event(db_session, event)

    assert len(alerts) == 1
    assert alerts[0].severity == "medium"
    assert alerts[0].rule_name == "sensitive_port"
    assert "RDP" in alerts[0].title


def test_detection_flags_port_scan_once_threshold_is_reached(db_session: Session) -> None:
    scan = Scan(target_name="port-scan", status="running")
    db_session.add(scan)
    db_session.flush()

    latest_event = None
    for port in [80, 81, 82, 83, 84]:
        latest_event = _event(scan=scan, source_ip="10.0.0.50", destination_port=port)
        db_session.add(latest_event)
    db_session.commit()

    assert latest_event is not None
    alerts = detect_alerts_for_event(db_session, latest_event)

    assert len(alerts) == 1
    assert alerts[0].severity == "high"
    assert alerts[0].rule_name == "port_scan"


def test_detection_does_not_duplicate_port_scan_alerts(db_session: Session) -> None:
    scan = Scan(target_name="existing-alert", status="running")
    db_session.add(scan)
    db_session.flush()

    events = [_event(scan=scan, source_ip="10.0.0.60", destination_port=port) for port in [80, 81, 82, 83, 84]]
    db_session.add_all(events)
    db_session.add(
        Alert(
            scan=scan,
            severity="high",
            title="Possible port scan detected",
            description="Already detected.",
            rule_name="port_scan",
            source_ip="10.0.0.60",
        )
    )
    db_session.commit()

    alerts = detect_alerts_for_event(db_session, events[-1])

    assert alerts == []
    saved_alerts = db_session.scalars(select(Alert).where(Alert.rule_name == "port_scan")).all()
    assert len(saved_alerts) == 1


def _event(
    *,
    scan: Scan,
    source_ip: str = "192.168.1.10",
    destination_port: int = 443,
) -> PacketEvent:
    return PacketEvent(
        scan=scan,
        timestamp=datetime.now(timezone.utc),
        source_ip=source_ip,
        destination_ip="10.0.0.1",
        protocol="TCP",
        source_port=49152,
        destination_port=destination_port,
        packet_size=512,
    )

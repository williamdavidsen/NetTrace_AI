from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Alert, PacketEvent, Scan
from app.services.detection import detect_alerts_for_event


def test_detection_flags_suspicious_destination_port(db_session: Session) -> None:
    scan = Scan(target_name="suspicious-port", status="running")
    event = _event(scan=scan, destination_port=3389)
    db_session.add(event)
    db_session.commit()

    alerts = detect_alerts_for_event(db_session, event)

    assert len(alerts) == 1
    assert alerts[0].severity == "medium"
    assert alerts[0].rule_name == "suspicious_port"
    assert "RDP" in alerts[0].title


def test_detection_marks_repeated_suspicious_port_as_high(db_session: Session) -> None:
    scan = Scan(target_name="repeated-suspicious-port", status="running")
    db_session.add(scan)
    db_session.flush()

    events = [_event(scan=scan, source_ip="10.0.0.70", destination_port=22) for _ in range(5)]
    db_session.add_all(events)
    db_session.commit()

    alerts = detect_alerts_for_event(db_session, events[-1])

    assert len(alerts) == 1
    assert alerts[0].severity == "high"
    assert alerts[0].rule_name == "suspicious_port"


def test_detection_flags_port_scan_once_threshold_is_reached(db_session: Session) -> None:
    scan = Scan(target_name="port-scan", status="running")
    db_session.add(scan)
    db_session.flush()

    latest_event = None
    for port in range(80, 100):
        latest_event = _event(scan=scan, source_ip="10.0.0.50", destination_port=port)
        db_session.add(latest_event)
    db_session.commit()

    assert latest_event is not None
    alerts = detect_alerts_for_event(db_session, latest_event)

    assert len(alerts) == 1
    assert alerts[0].severity == "high"
    assert alerts[0].rule_name == "port_scan"


def test_detection_ignores_old_ports_for_port_scan_window(db_session: Session) -> None:
    scan = Scan(target_name="old-port-scan", status="running")
    db_session.add(scan)
    db_session.flush()

    old_timestamp = datetime.now(timezone.utc) - timedelta(minutes=5)
    for port in range(80, 99):
        db_session.add(_event(scan=scan, source_ip="10.0.0.55", destination_port=port, timestamp=old_timestamp))
    latest_event = _event(scan=scan, source_ip="10.0.0.55", destination_port=99)
    db_session.add(latest_event)
    db_session.commit()

    alerts = detect_alerts_for_event(db_session, latest_event)

    assert alerts == []


def test_detection_does_not_duplicate_port_scan_alerts(db_session: Session) -> None:
    scan = Scan(target_name="existing-alert", status="running")
    db_session.add(scan)
    db_session.flush()

    events = [_event(scan=scan, source_ip="10.0.0.60", destination_port=port) for port in range(80, 100)]
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


def test_detection_flags_dns_spike_at_threshold(db_session: Session) -> None:
    scan = Scan(target_name="dns-spike", status="running")
    db_session.add(scan)
    db_session.flush()

    events = [_event(scan=scan, source_ip="10.0.0.80", protocol="UDP", destination_port=53) for _ in range(50)]
    db_session.add_all(events)
    db_session.commit()

    alerts = detect_alerts_for_event(db_session, events[-1])

    assert len(alerts) == 1
    assert alerts[0].severity == "medium"
    assert alerts[0].rule_name == "dns_spike"


def test_detection_does_not_duplicate_dns_spike_alerts(db_session: Session) -> None:
    scan = Scan(target_name="existing-dns-alert", status="running")
    db_session.add(scan)
    db_session.flush()

    events = [_event(scan=scan, source_ip="10.0.0.81", protocol="UDP", destination_port=53) for _ in range(50)]
    db_session.add_all(events)
    db_session.add(
        Alert(
            scan=scan,
            severity="medium",
            title="DNS traffic spike detected",
            description="Already detected.",
            rule_name="dns_spike",
            source_ip="10.0.0.81",
        )
    )
    db_session.commit()

    alerts = detect_alerts_for_event(db_session, events[-1])

    assert alerts == []


def test_detection_flags_large_packet(db_session: Session) -> None:
    scan = Scan(target_name="large-packet", status="running")
    event = _event(scan=scan, packet_size=9001)
    db_session.add(event)
    db_session.commit()

    alerts = detect_alerts_for_event(db_session, event)

    assert len(alerts) == 1
    assert alerts[0].severity == "medium"
    assert alerts[0].rule_name == "large_packet"


def test_detection_flags_unknown_protocol(db_session: Session) -> None:
    scan = Scan(target_name="unknown-protocol", status="running")
    event = _event(scan=scan, protocol="GRE")
    db_session.add(event)
    db_session.commit()

    alerts = detect_alerts_for_event(db_session, event)

    assert len(alerts) == 1
    assert alerts[0].severity == "low"
    assert alerts[0].rule_name == "unknown_protocol"


def test_detection_does_not_alert_for_normal_traffic(db_session: Session) -> None:
    scan = Scan(target_name="normal-traffic", status="running")
    event = _event(scan=scan, destination_port=443, packet_size=512, protocol="TCP")
    db_session.add(event)
    db_session.commit()

    alerts = detect_alerts_for_event(db_session, event)

    assert alerts == []


def _event(
    *,
    scan: Scan,
    source_ip: str = "192.168.1.10",
    destination_port: int = 443,
    protocol: str = "TCP",
    packet_size: int = 512,
    timestamp: datetime | None = None,
) -> PacketEvent:
    return PacketEvent(
        scan=scan,
        timestamp=timestamp or datetime.now(timezone.utc),
        source_ip=source_ip,
        destination_ip="10.0.0.1",
        protocol=protocol,
        source_port=49152,
        destination_port=destination_port,
        packet_size=packet_size,
    )

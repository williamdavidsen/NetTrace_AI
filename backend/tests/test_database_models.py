from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Alert, PacketEvent, Scan


def test_scan_can_be_created(db_session: Session) -> None:
    scan = Scan(target_name="local-lab", status="running")

    db_session.add(scan)
    db_session.commit()

    saved_scan = db_session.scalar(select(Scan).where(Scan.id == scan.id))
    assert saved_scan is not None
    assert saved_scan.target_name == "local-lab"
    assert saved_scan.status == "running"


def test_packet_event_can_be_saved_for_a_scan(db_session: Session) -> None:
    scan = Scan(target_name="office-network", status="running")
    event = PacketEvent(
        scan=scan,
        timestamp=datetime.now(timezone.utc),
        source_ip="192.168.1.10",
        destination_ip="8.8.8.8",
        protocol="UDP",
        source_port=51522,
        destination_port=53,
        packet_size=128,
    )

    db_session.add(event)
    db_session.commit()

    saved_event = db_session.scalar(select(PacketEvent).where(PacketEvent.id == event.id))
    assert saved_event is not None
    assert saved_event.scan_id == scan.id
    assert saved_event.source_ip == "192.168.1.10"
    assert saved_event.destination_port == 53


def test_alert_can_be_saved_for_a_scan(db_session: Session) -> None:
    scan = Scan(target_name="lab-target", status="running")
    alert = Alert(
        scan=scan,
        severity="high",
        title="Possible port scan detected",
        description="A source IP contacted many different ports in a short window.",
        rule_name="port_scan",
        source_ip="192.168.1.10",
    )

    db_session.add(alert)
    db_session.commit()

    saved_alert = db_session.scalar(select(Alert).where(Alert.id == alert.id))
    assert saved_alert is not None
    assert saved_alert.scan_id == scan.id
    assert saved_alert.severity == "high"
    assert saved_alert.rule_name == "port_scan"


def test_scan_relationships_include_events_and_alerts(db_session: Session) -> None:
    scan = Scan(target_name="relationship-check", status="running")
    scan.packet_events.append(
        PacketEvent(
            timestamp=datetime.now(timezone.utc),
            source_ip="10.0.0.10",
            destination_ip="10.0.0.20",
            protocol="TCP",
            source_port=44120,
            destination_port=443,
            packet_size=512,
        )
    )
    scan.alerts.append(
        Alert(
            severity="medium",
            title="Suspicious port activity",
            description="Traffic touched a sensitive service port.",
            rule_name="suspicious_port",
            source_ip="10.0.0.10",
        )
    )

    db_session.add(scan)
    db_session.commit()
    db_session.refresh(scan)

    assert len(scan.packet_events) == 1
    assert len(scan.alerts) == 1

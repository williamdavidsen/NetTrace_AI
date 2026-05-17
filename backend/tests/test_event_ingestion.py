from collections.abc import Generator
from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.main import create_app
from app.models import Alert, PacketEvent, Scan
from app.streams import get_event_stream


def test_event_ingestion_saves_valid_payload(db_session: Session) -> None:
    scan = Scan(target_name="event-ingestion", status="running")
    db_session.add(scan)
    db_session.commit()

    client = _client_with_session(db_session)
    payload = _valid_event_payload(scan.id)

    response = client.post("/api/v1/events", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["id"]
    assert body["scan_id"] == scan.id
    assert body["protocol"] == "TCP"
    assert body["destination_port"] == 443

    saved_event = db_session.scalar(select(PacketEvent).where(PacketEvent.id == body["id"]))
    assert saved_event is not None
    assert saved_event.source_ip == "192.168.1.10"
    assert saved_event.packet_size == 512


def test_event_ingestion_rejects_missing_fields(db_session: Session) -> None:
    client = _client_with_session(db_session)

    response = client.post("/api/v1/events", json={"protocol": "TCP"})

    assert response.status_code == 422


def test_event_ingestion_rejects_invalid_ip(db_session: Session) -> None:
    scan = Scan(target_name="invalid-ip", status="running")
    db_session.add(scan)
    db_session.commit()

    client = _client_with_session(db_session)
    payload = _valid_event_payload(scan.id)
    payload["source_ip"] = "999.999.999.999"

    response = client.post("/api/v1/events", json=payload)

    assert response.status_code == 422


def test_event_ingestion_rejects_invalid_port(db_session: Session) -> None:
    scan = Scan(target_name="invalid-port", status="running")
    db_session.add(scan)
    db_session.commit()

    client = _client_with_session(db_session)
    payload = _valid_event_payload(scan.id)
    payload["destination_port"] = 70000

    response = client.post("/api/v1/events", json=payload)

    assert response.status_code == 422


def test_event_ingestion_rejects_blank_protocol(db_session: Session) -> None:
    scan = Scan(target_name="blank-protocol", status="running")
    db_session.add(scan)
    db_session.commit()

    client = _client_with_session(db_session)
    payload = _valid_event_payload(scan.id)
    payload["protocol"] = "   "

    response = client.post("/api/v1/events", json=payload)

    assert response.status_code == 422


def test_event_ingestion_rejects_unknown_scan(db_session: Session) -> None:
    client = _client_with_session(db_session)
    payload = _valid_event_payload("11111111-1111-1111-1111-111111111111")

    response = client.post("/api/v1/events", json=payload)

    assert response.status_code == 404


def test_event_ingestion_creates_alert_for_suspicious_port(db_session: Session) -> None:
    scan = Scan(target_name="suspicious-port-ingestion", status="running")
    db_session.add(scan)
    db_session.commit()

    client = _client_with_session(db_session)
    payload = _valid_event_payload(scan.id)
    payload["destination_port"] = 22

    response = client.post("/api/v1/events", json=payload)

    assert response.status_code == 201
    saved_alert = db_session.scalar(select(Alert).where(Alert.scan_id == scan.id))
    assert saved_alert is not None
    assert saved_alert.rule_name == "suspicious_port"
    assert saved_alert.source_ip == "192.168.1.10"


def test_event_ingestion_creates_port_scan_alert_at_threshold(db_session: Session) -> None:
    scan = Scan(target_name="port-scan-ingestion", status="running")
    db_session.add(scan)
    db_session.commit()

    client = _client_with_session(db_session)
    for port in range(80, 100):
        payload = _valid_event_payload(scan.id)
        payload["source_ip"] = "10.0.0.90"
        payload["destination_port"] = port
        response = client.post("/api/v1/events", json=payload)
        assert response.status_code == 201

    saved_alerts = db_session.scalars(select(Alert).where(Alert.scan_id == scan.id)).all()
    assert len(saved_alerts) == 1
    assert saved_alerts[0].rule_name == "port_scan"


def test_event_ingestion_creates_dns_spike_alert_at_threshold(db_session: Session) -> None:
    scan = Scan(target_name="dns-spike-ingestion", status="running")
    db_session.add(scan)
    db_session.commit()

    client = _client_with_session(db_session)
    for _ in range(50):
        payload = _valid_event_payload(scan.id)
        payload["source_ip"] = "10.0.0.91"
        payload["protocol"] = "UDP"
        payload["destination_port"] = 53
        response = client.post("/api/v1/events", json=payload)
        assert response.status_code == 201

    saved_alerts = db_session.scalars(select(Alert).where(Alert.scan_id == scan.id)).all()
    assert len(saved_alerts) == 1
    assert saved_alerts[0].rule_name == "dns_spike"


def test_event_ingestion_creates_large_packet_alert(db_session: Session) -> None:
    scan = Scan(target_name="large-packet-ingestion", status="running")
    db_session.add(scan)
    db_session.commit()

    client = _client_with_session(db_session)
    payload = _valid_event_payload(scan.id)
    payload["packet_size"] = 9001

    response = client.post("/api/v1/events", json=payload)

    assert response.status_code == 201
    saved_alert = db_session.scalar(select(Alert).where(Alert.scan_id == scan.id))
    assert saved_alert is not None
    assert saved_alert.rule_name == "large_packet"


def test_event_ingestion_creates_unknown_protocol_alert(db_session: Session) -> None:
    scan = Scan(target_name="unknown-protocol-ingestion", status="running")
    db_session.add(scan)
    db_session.commit()

    client = _client_with_session(db_session)
    payload = _valid_event_payload(scan.id)
    payload["protocol"] = "gre"

    response = client.post("/api/v1/events", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["protocol"] == "GRE"
    saved_alert = db_session.scalar(select(Alert).where(Alert.scan_id == scan.id))
    assert saved_alert is not None
    assert saved_alert.rule_name == "unknown_protocol"


def _client_with_session(db_session: Session) -> TestClient:
    app = create_app()

    def override_get_session() -> Generator[Session, None, None]:
        yield db_session

    def override_get_event_stream() -> Generator["_RecordingEventStream", None, None]:
        yield _RecordingEventStream()

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_event_stream] = override_get_event_stream
    return TestClient(app)


def _valid_event_payload(scan_id: str) -> dict[str, str | int]:
    return {
        "scan_id": scan_id,
        "timestamp": datetime(2026, 1, 1, tzinfo=timezone.utc).isoformat(),
        "source_ip": "192.168.1.10",
        "destination_ip": "8.8.8.8",
        "protocol": "TCP",
        "source_port": 49152,
        "destination_port": 443,
        "packet_size": 512,
    }


class _RecordingEventStream:
    def publish_packet_event(self, event: PacketEvent) -> str:
        return f"{event.id}-0"

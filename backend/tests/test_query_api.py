from collections.abc import Generator
from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.main import create_app
from app.models import Alert, PacketEvent, Scan


def test_scans_endpoint_creates_scan(db_session: Session) -> None:
    client = _client_with_session(db_session)

    response = client.post("/api/v1/scans", json={"target_name": "office-lab"})

    assert response.status_code == 201
    body = response.json()
    assert body["id"]
    assert body["target_name"] == "office-lab"
    assert body["status"] == "running"
    assert body["finished_at"] is None


def test_scans_endpoint_rejects_blank_target_name(db_session: Session) -> None:
    client = _client_with_session(db_session)

    response = client.post("/api/v1/scans", json={"target_name": "   "})

    assert response.status_code == 422


def test_scans_endpoint_lists_scans_newest_first_with_limit(db_session: Session) -> None:
    first_scan = Scan(
        target_name="first",
        status="running",
        created_at=datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc),
    )
    second_scan = Scan(
        target_name="second",
        status="running",
        created_at=datetime(2026, 1, 1, 12, 1, tzinfo=timezone.utc),
    )
    db_session.add_all([first_scan, second_scan])
    db_session.commit()

    client = _client_with_session(db_session)
    response = client.get("/api/v1/scans?limit=1")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["id"] == second_scan.id


def test_scan_detail_returns_scan(db_session: Session) -> None:
    scan = Scan(target_name="detail", status="running")
    db_session.add(scan)
    db_session.commit()

    client = _client_with_session(db_session)
    response = client.get(f"/api/v1/scans/{scan.id}")

    assert response.status_code == 200
    assert response.json()["target_name"] == "detail"


def test_scan_detail_returns_404_for_missing_scan(db_session: Session) -> None:
    client = _client_with_session(db_session)

    response = client.get("/api/v1/scans/11111111-1111-1111-1111-111111111111")

    assert response.status_code == 404


def test_scan_complete_updates_status_and_finished_at(db_session: Session) -> None:
    scan = Scan(target_name="complete", status="running")
    db_session.add(scan)
    db_session.commit()

    client = _client_with_session(db_session)
    response = client.patch(f"/api/v1/scans/{scan.id}/complete")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "completed"
    assert body["finished_at"] is not None


def test_scan_events_endpoint_lists_events_for_scan(db_session: Session) -> None:
    matching_scan = Scan(target_name="matching", status="running")
    other_scan = Scan(target_name="other", status="running")
    db_session.add_all([matching_scan, other_scan])
    db_session.flush()
    first_event = _event(
        scan=matching_scan,
        source_ip="10.0.0.1",
        timestamp=datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc),
    )
    second_event = _event(
        scan=matching_scan,
        source_ip="10.0.0.2",
        timestamp=datetime(2026, 1, 1, 12, 1, tzinfo=timezone.utc),
    )
    db_session.add_all([first_event, second_event, _event(scan=other_scan, source_ip="10.0.0.3")])
    db_session.commit()

    client = _client_with_session(db_session)
    response = client.get(f"/api/v1/scans/{matching_scan.id}/events?limit=1")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["id"] == second_event.id
    assert body[0]["scan_id"] == matching_scan.id


def test_scan_events_endpoint_returns_404_for_missing_scan(db_session: Session) -> None:
    client = _client_with_session(db_session)

    response = client.get("/api/v1/scans/11111111-1111-1111-1111-111111111111/events")

    assert response.status_code == 404


def test_scan_alerts_endpoint_lists_alerts_for_scan(db_session: Session) -> None:
    matching_scan = Scan(target_name="matching-alerts", status="running")
    other_scan = Scan(target_name="other-alerts", status="running")
    db_session.add_all([matching_scan, other_scan])
    db_session.flush()
    first_alert = _alert(
        scan=matching_scan,
        source_ip="10.0.0.1",
        created_at=datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc),
    )
    second_alert = _alert(
        scan=matching_scan,
        source_ip="10.0.0.2",
        created_at=datetime(2026, 1, 1, 12, 1, tzinfo=timezone.utc),
    )
    db_session.add_all([first_alert, second_alert, _alert(scan=other_scan, source_ip="10.0.0.3")])
    db_session.commit()

    client = _client_with_session(db_session)
    response = client.get(f"/api/v1/scans/{matching_scan.id}/alerts?limit=1")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["id"] == second_alert.id
    assert body[0]["scan_id"] == matching_scan.id


def test_alert_detail_endpoint_returns_alert(db_session: Session) -> None:
    scan = Scan(target_name="alert-detail", status="running")
    db_session.add(scan)
    db_session.flush()
    alert = _alert(scan=scan, source_ip="10.0.0.1")
    db_session.add(alert)
    db_session.commit()

    client = _client_with_session(db_session)
    response = client.get(f"/api/v1/alerts/{alert.id}")

    assert response.status_code == 200
    assert response.json()["id"] == alert.id


def test_alert_detail_endpoint_returns_404_for_missing_alert(db_session: Session) -> None:
    client = _client_with_session(db_session)

    response = client.get("/api/v1/alerts/11111111-1111-1111-1111-111111111111")

    assert response.status_code == 404


def test_alert_explanation_endpoint_returns_rule_based_explanation(db_session: Session) -> None:
    scan = Scan(target_name="alert-explanation", status="running")
    db_session.add(scan)
    db_session.flush()
    alert = _alert(scan=scan, source_ip="10.0.0.1")
    db_session.add(alert)
    db_session.commit()

    client = _client_with_session(db_session)
    response = client.get(f"/api/v1/alerts/{alert.id}/explanation")

    assert response.status_code == 200
    body = response.json()
    assert body["alert_id"] == alert.id
    assert body["rule_name"] == "port_scan"
    assert body["summary"]
    assert body["pattern"]
    assert body["recommended_action"]


def test_alert_explanation_endpoint_returns_404_for_missing_alert(db_session: Session) -> None:
    client = _client_with_session(db_session)

    response = client.get("/api/v1/alerts/11111111-1111-1111-1111-111111111111/explanation")

    assert response.status_code == 404


def test_metrics_endpoint_returns_basic_counts(db_session: Session) -> None:
    running_scan = Scan(target_name="running", status="running")
    completed_scan = Scan(target_name="completed", status="completed")
    db_session.add_all([running_scan, completed_scan])
    db_session.flush()
    db_session.add_all(
        [
            _event(scan=running_scan, source_ip="10.0.0.1"),
            _event(scan=running_scan, source_ip="10.0.0.2"),
            _alert(scan=running_scan, source_ip="10.0.0.1"),
        ]
    )
    db_session.commit()

    client = _client_with_session(db_session)
    response = client.get("/metrics")

    assert response.status_code == 200
    assert response.json() == {
        "processed_events_total": 2,
        "generated_alerts_total": 1,
        "active_scans_total": 1,
    }


def test_query_limit_validation(db_session: Session) -> None:
    client = _client_with_session(db_session)

    response = client.get("/api/v1/scans?limit=0")

    assert response.status_code == 422


def _client_with_session(db_session: Session) -> TestClient:
    app = create_app()

    def override_get_session() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_session] = override_get_session
    return TestClient(app)


def _event(
    *,
    scan: Scan,
    source_ip: str,
    timestamp: datetime | None = None,
) -> PacketEvent:
    return PacketEvent(
        scan=scan,
        timestamp=timestamp or datetime(2026, 1, 1, tzinfo=timezone.utc),
        source_ip=source_ip,
        destination_ip="8.8.8.8",
        protocol="TCP",
        source_port=49152,
        destination_port=443,
        packet_size=512,
    )


def _alert(
    *,
    scan: Scan,
    source_ip: str,
    created_at: datetime | None = None,
) -> Alert:
    return Alert(
        scan=scan,
        severity="high",
        title="Possible port scan detected",
        description="A source IP contacted many ports.",
        rule_name="port_scan",
        source_ip=source_ip,
        created_at=created_at or datetime(2026, 1, 1, tzinfo=timezone.utc),
    )

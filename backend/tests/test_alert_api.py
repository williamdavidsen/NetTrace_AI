from collections.abc import Generator
from datetime import datetime, timezone
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.main import create_app
from app.models import Alert, Scan


def test_alerts_endpoint_lists_alerts_newest_first(db_session: Session) -> None:
    first_scan = Scan(target_name="first", status="running")
    second_scan = Scan(target_name="second", status="running")
    db_session.add_all([first_scan, second_scan])
    db_session.flush()
    first_alert = _alert(
        scan=first_scan,
        source_ip="10.0.0.1",
        created_at=datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc),
    )
    second_alert = _alert(
        scan=second_scan,
        source_ip="10.0.0.2",
        created_at=datetime(2026, 1, 1, 12, 1, tzinfo=timezone.utc),
    )
    db_session.add_all([first_alert, second_alert])
    db_session.commit()

    client = _client_with_session(db_session)
    response = client.get("/api/v1/alerts")

    assert response.status_code == 200
    body = response.json()
    assert [alert["id"] for alert in body] == [second_alert.id, first_alert.id]
    assert body[0]["rule_name"] == "suspicious_port"


def test_alerts_endpoint_filters_by_scan_id(db_session: Session) -> None:
    matching_scan = Scan(target_name="matching", status="running")
    other_scan = Scan(target_name="other", status="running")
    db_session.add_all([matching_scan, other_scan])
    db_session.flush()
    db_session.add_all(
        [
            _alert(scan=matching_scan, source_ip="10.0.0.1"),
            _alert(scan=other_scan, source_ip="10.0.0.2"),
        ]
    )
    db_session.commit()

    client = _client_with_session(db_session)
    response = client.get(f"/api/v1/alerts?scan_id={matching_scan.id}")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["scan_id"] == matching_scan.id


def test_alerts_endpoint_rejects_invalid_scan_filter(db_session: Session) -> None:
    client = _client_with_session(db_session)

    response = client.get("/api/v1/alerts?scan_id=not-a-uuid")

    assert response.status_code == 422


def test_alert_explanation_endpoint_returns_explanation(db_session: Session) -> None:
    scan = Scan(target_name="scan-with-alert", status="running")
    db_session.add(scan)
    db_session.flush()
    alert = _alert(scan=scan, source_ip="10.0.0.10")
    db_session.add(alert)
    db_session.commit()

    client = _client_with_session(db_session)
    response = client.get(f"/api/v1/alerts/{alert.id}/explanation")

    assert response.status_code == 200
    body = response.json()
    assert body["alert_id"] == alert.id
    assert body["rule_name"] == "suspicious_port"
    assert body["summary"]
    assert body["pattern"]
    assert body["recommended_action"]


def test_alert_explanation_endpoint_returns_404_for_missing_alert(db_session: Session) -> None:
    client = _client_with_session(db_session)

    response = client.get(f"/api/v1/alerts/{uuid4()}/explanation")

    assert response.status_code == 404
    assert response.json()["detail"] == "Alert not found."


def _client_with_session(db_session: Session) -> TestClient:
    app = create_app()

    def override_get_session() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_session] = override_get_session
    return TestClient(app)


def _alert(*, scan: Scan, source_ip: str, created_at: datetime | None = None) -> Alert:
    return Alert(
        scan=scan,
        severity="medium",
        title="Sensitive service contacted: SSH",
        description="A source IP contacted SSH.",
        rule_name="suspicious_port",
        source_ip=source_ip,
        created_at=created_at or datetime(2026, 1, 1, tzinfo=timezone.utc),
    )

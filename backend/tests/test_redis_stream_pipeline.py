from collections.abc import Generator
from datetime import datetime, timezone

from fastapi.testclient import TestClient
from redis.exceptions import ConnectionError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.main import create_app
from app.models import PacketEvent, Scan
from app.streams import EventStreamPublishError, RedisEventStream, get_event_stream


def test_redis_event_stream_publishes_packet_event_to_network_events() -> None:
    redis_client = _FakeRedisClient()
    event_stream = RedisEventStream(client=redis_client, stream_name="network_events")
    event = _packet_event(scan_id="11111111-1111-1111-1111-111111111111")

    stream_id = event_stream.publish_packet_event(event)

    assert stream_id == "1-0"
    assert redis_client.stream_name == "network_events"
    assert redis_client.payload["event_id"] == event.id
    assert redis_client.payload["scan_id"] == event.scan_id
    assert redis_client.payload["source_ip"] == "192.168.1.10"
    assert redis_client.payload["destination_port"] == "443"
    assert redis_client.payload["packet_size"] == "512"


def test_redis_event_stream_wraps_connection_errors() -> None:
    redis_client = _FailingRedisClient()
    event_stream = RedisEventStream(client=redis_client, stream_name="network_events")
    event = _packet_event(scan_id="11111111-1111-1111-1111-111111111111")

    try:
        event_stream.publish_packet_event(event)
    except EventStreamPublishError as exc:
        assert "Redis stream" in str(exc)
    else:
        raise AssertionError("Expected EventStreamPublishError")


def test_event_ingestion_writes_valid_event_to_postgresql_and_redis(db_session: Session) -> None:
    scan = Scan(target_name="stream-success", status="running")
    db_session.add(scan)
    db_session.commit()
    event_stream = _RecordingEventStream()
    client = _client_with_dependencies(db_session=db_session, event_stream=event_stream)

    response = client.post("/api/v1/events", json=_valid_event_payload(scan.id))

    assert response.status_code == 201
    body = response.json()
    saved_event = db_session.scalar(select(PacketEvent).where(PacketEvent.id == body["id"]))
    assert saved_event is not None
    assert event_stream.published_event_ids == [body["id"]]


def test_event_ingestion_rolls_back_when_redis_publish_fails(db_session: Session) -> None:
    scan = Scan(target_name="stream-failure", status="running")
    db_session.add(scan)
    db_session.commit()
    client = _client_with_dependencies(db_session=db_session, event_stream=_FailingEventStream())

    response = client.post("/api/v1/events", json=_valid_event_payload(scan.id))

    assert response.status_code == 503
    assert response.json()["error"]["message"] == "Event stream unavailable."
    saved_events = db_session.scalars(select(PacketEvent).where(PacketEvent.scan_id == scan.id)).all()
    assert saved_events == []


def _client_with_dependencies(db_session: Session, event_stream: object) -> TestClient:
    app = create_app()

    def override_get_session() -> Generator[Session, None, None]:
        yield db_session

    def override_get_event_stream() -> Generator[object, None, None]:
        yield event_stream

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


def _packet_event(scan_id: str) -> PacketEvent:
    return PacketEvent(
        id="event-1",
        scan_id=scan_id,
        timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc),
        source_ip="192.168.1.10",
        destination_ip="8.8.8.8",
        protocol="TCP",
        source_port=49152,
        destination_port=443,
        packet_size=512,
    )


class _FakeRedisClient:
    def __init__(self) -> None:
        self.stream_name = ""
        self.payload: dict[str, str] = {}

    def xadd(self, stream_name: str, payload: dict[str, str]) -> str:
        self.stream_name = stream_name
        self.payload = payload
        return "1-0"


class _FailingRedisClient:
    def xadd(self, stream_name: str, payload: dict[str, str]) -> str:
        raise ConnectionError("redis unavailable")


class _RecordingEventStream:
    def __init__(self) -> None:
        self.published_event_ids: list[str] = []

    def publish_packet_event(self, event: PacketEvent) -> str:
        self.published_event_ids.append(event.id)
        return "1-0"


class _FailingEventStream:
    def publish_packet_event(self, event: PacketEvent) -> str:
        raise EventStreamPublishError("Could not publish packet event to Redis stream.")

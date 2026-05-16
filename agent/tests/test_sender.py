import json
from io import BytesIO

import sender
from events import PacketEventPayload
from sender import EventSender


class FakeResponse:
    status = 201

    def __init__(self, payload: dict[str, object]) -> None:
        self._body = json.dumps(payload).encode("utf-8")

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def read(self) -> bytes:
        return BytesIO(self._body).read()


def test_sender_posts_event_json(monkeypatch) -> None:
    captured = {}

    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        captured["timeout"] = timeout
        captured["content_type"] = request.headers["Content-type"]
        captured["body"] = json.loads(request.data.decode("utf-8"))
        return FakeResponse({"id": "event-1", "accepted": True})

    monkeypatch.setattr(sender, "urlopen", fake_urlopen)
    event = PacketEventPayload(
        scan_id="11111111-1111-1111-1111-111111111111",
        timestamp="2026-01-01T00:00:00+00:00",
        source_ip="192.168.1.10",
        destination_ip="8.8.8.8",
        protocol="UDP",
        source_port=53000,
        destination_port=53,
        packet_size=128,
    )

    response = EventSender("http://localhost:8000/api/v1/events", timeout_seconds=2).send(event)

    assert response == {"id": "event-1", "accepted": True}
    assert captured["url"] == "http://localhost:8000/api/v1/events"
    assert captured["timeout"] == 2
    assert captured["content_type"] == "application/json"
    assert captured["body"]["destination_port"] == 53

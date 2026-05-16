import pytest

from events import PacketEventPayload, SampleEventGenerator


SCAN_ID = "11111111-1111-1111-1111-111111111111"


def test_generator_produces_valid_backend_compatible_event() -> None:
    event = SampleEventGenerator(scan_id=SCAN_ID, seed=42).generate_one()

    payload = event.to_dict()

    assert payload.keys() == {
        "scan_id",
        "timestamp",
        "source_ip",
        "destination_ip",
        "protocol",
        "source_port",
        "destination_port",
        "packet_size",
    }
    assert payload["scan_id"] == SCAN_ID
    assert payload["protocol"] in {"TCP", "UDP", "ICMP"}
    assert 1 <= payload["packet_size"] <= 65535


def test_generator_is_deterministic_for_same_seed() -> None:
    first = SampleEventGenerator(scan_id=SCAN_ID, seed=99).generate(5)
    second = SampleEventGenerator(scan_id=SCAN_ID, seed=99).generate(5)

    assert [event.to_dict() for event in first] == [event.to_dict() for event in second]


def test_generator_rejects_empty_count() -> None:
    generator = SampleEventGenerator(scan_id=SCAN_ID)

    with pytest.raises(ValueError, match="count must be at least 1"):
        generator.generate(0)


def test_event_validation_rejects_invalid_protocol() -> None:
    event = PacketEventPayload(
        scan_id=SCAN_ID,
        timestamp="2026-01-01T00:00:00+00:00",
        source_ip="192.168.1.10",
        destination_ip="8.8.8.8",
        protocol="FTP",
        source_port=12000,
        destination_port=21,
        packet_size=128,
    )

    with pytest.raises(ValueError, match="Unsupported protocol"):
        event.validate()

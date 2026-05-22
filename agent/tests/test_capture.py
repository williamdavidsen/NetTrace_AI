from datetime import datetime, timezone
from types import ModuleType
import sys

import pytest

from capture import (
    PacketCaptureConfig,
    PacketCapturePermissionError,
    capture_packet_metadata,
    parse_packets,
)


SCAN_ID = "11111111-1111-1111-1111-111111111111"


class IP:
    def __init__(self, src: str = "192.168.1.10", dst: str = "8.8.8.8") -> None:
        self.src = src
        self.dst = dst


class TCP:
    def __init__(self, sport: int = 53000, dport: int = 443) -> None:
        self.sport = sport
        self.dport = dport


class UDP:
    def __init__(self, sport: int = 53001, dport: int = 53) -> None:
        self.sport = sport
        self.dport = dport


class ICMP:
    pass


class FakePacket:
    def __init__(self, *layers: object, size: int = 128, payload: bytes = b"secret") -> None:
        self._layers = {layer.__class__.__name__: layer for layer in layers}
        self._size = size
        self.payload = payload

    def haslayer(self, name: str) -> bool:
        return name in self._layers

    def getlayer(self, name: str) -> object:
        return self._layers[name]

    def __len__(self) -> int:
        return self._size


def fixed_clock() -> datetime:
    return datetime(2026, 5, 22, 12, 0, tzinfo=timezone.utc)


def test_parser_extracts_tcp_metadata_without_payload() -> None:
    packet = FakePacket(IP(), TCP(), size=512, payload=b"do-not-store")

    events = parse_packets([packet], scan_id=SCAN_ID, clock=fixed_clock)

    assert len(events) == 1
    payload = events[0].to_dict()
    assert payload == {
        "scan_id": SCAN_ID,
        "timestamp": "2026-05-22T12:00:00+00:00",
        "source_ip": "192.168.1.10",
        "destination_ip": "8.8.8.8",
        "protocol": "TCP",
        "source_port": 53000,
        "destination_port": 443,
        "packet_size": 512,
    }
    assert "payload" not in payload


def test_parser_extracts_udp_metadata() -> None:
    packet = FakePacket(IP(dst="1.1.1.1"), UDP(), size=96)

    event = parse_packets([packet], scan_id=SCAN_ID, clock=fixed_clock)[0]

    assert event.protocol == "UDP"
    assert event.destination_ip == "1.1.1.1"
    assert event.source_port == 53001
    assert event.destination_port == 53


def test_parser_extracts_icmp_without_ports() -> None:
    packet = FakePacket(IP(), ICMP(), size=84)

    event = parse_packets([packet], scan_id=SCAN_ID, clock=fixed_clock)[0]

    assert event.protocol == "ICMP"
    assert event.source_port is None
    assert event.destination_port is None


def test_parser_skips_packets_without_supported_network_metadata() -> None:
    packet = FakePacket(TCP(), size=128)

    assert parse_packets([packet], scan_id=SCAN_ID, clock=fixed_clock) == []


def test_capture_uses_scapy_without_storing_packets(monkeypatch) -> None:
    captured = {}
    scapy_module = ModuleType("scapy")
    scapy_all_module = ModuleType("scapy.all")

    def sniff(**kwargs):
        captured.update(kwargs)
        kwargs["prn"](FakePacket(IP(), TCP(), size=128))

    scapy_all_module.sniff = sniff
    monkeypatch.setitem(sys.modules, "scapy", scapy_module)
    monkeypatch.setitem(sys.modules, "scapy.all", scapy_all_module)

    events = capture_packet_metadata(
        PacketCaptureConfig(scan_id=SCAN_ID, interface="eth0", count=1)
    )

    assert len(events) == 1
    assert captured["iface"] == "eth0"
    assert captured["filter"] == "ip or ip6"
    assert captured["store"] is False


def test_capture_permission_error_is_user_readable(monkeypatch) -> None:
    scapy_module = ModuleType("scapy")
    scapy_all_module = ModuleType("scapy.all")

    def sniff(**kwargs):
        raise PermissionError("access is denied")

    scapy_all_module.sniff = sniff
    monkeypatch.setitem(sys.modules, "scapy", scapy_module)
    monkeypatch.setitem(sys.modules, "scapy.all", scapy_all_module)

    with pytest.raises(PacketCapturePermissionError, match="administrator/root"):
        capture_packet_metadata(PacketCaptureConfig(scan_id=SCAN_ID, interface="eth0"))

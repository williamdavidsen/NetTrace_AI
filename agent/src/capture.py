from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import datetime, timezone

from events import PacketEventPayload


@dataclass(frozen=True)
class PacketCaptureConfig:
    scan_id: str
    interface: str | None = None
    packet_filter: str = "ip or ip6"
    count: int = 10
    timeout_seconds: int | None = None


class PacketCaptureError(RuntimeError):
    pass


class PacketCapturePermissionError(PacketCaptureError):
    pass


class PacketCaptureDependencyError(PacketCaptureError):
    pass


class PacketMetadataParser:
    def __init__(
        self,
        scan_id: str,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self.scan_id = scan_id
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def parse(self, packet: object) -> PacketEventPayload | None:
        ip_layer = _first_layer(packet, ("IP", "IPv6"))
        if ip_layer is None:
            return None

        transport_layer = _first_layer(packet, ("TCP", "UDP", "ICMP", "ICMPv6EchoRequest"))
        if transport_layer is None:
            return None

        protocol = _protocol_name(transport_layer)
        source_port = _layer_int(transport_layer, "sport")
        destination_port = _layer_int(transport_layer, "dport")
        if protocol == "ICMP":
            source_port = None
            destination_port = None

        event = PacketEventPayload(
            scan_id=self.scan_id,
            timestamp=self._clock().astimezone(timezone.utc).isoformat(),
            source_ip=str(getattr(ip_layer, "src")),
            destination_ip=str(getattr(ip_layer, "dst")),
            protocol=protocol,
            source_port=source_port,
            destination_port=destination_port,
            packet_size=len(packet),  # size only; payload bytes are never persisted.
        )
        event.validate()
        return event


def capture_packet_metadata(config: PacketCaptureConfig) -> list[PacketEventPayload]:
    if config.count < 1:
        raise ValueError("count must be at least 1")

    try:
        from scapy.all import sniff
    except ImportError as exc:
        raise PacketCaptureDependencyError(
            "Packet capture requires scapy. Install agent requirements before capture mode."
        ) from exc

    parser = PacketMetadataParser(scan_id=config.scan_id)
    events: list[PacketEventPayload] = []

    def on_packet(packet: object) -> None:
        event = parser.parse(packet)
        if event is not None:
            events.append(event)

    try:
        sniff(
            iface=config.interface,
            filter=config.packet_filter,
            prn=on_packet,
            count=config.count,
            timeout=config.timeout_seconds,
            store=False,
        )
    except PermissionError as exc:
        raise PacketCapturePermissionError(_permission_message(config.interface)) from exc
    except OSError as exc:
        if _looks_like_permission_error(exc):
            raise PacketCapturePermissionError(_permission_message(config.interface)) from exc
        raise PacketCaptureError(f"Packet capture failed: {exc}") from exc

    return events[: config.count]


def parse_packets(
    packets: Iterable[object],
    scan_id: str,
    clock: Callable[[], datetime] | None = None,
) -> list[PacketEventPayload]:
    parser = PacketMetadataParser(scan_id=scan_id, clock=clock)
    return [event for packet in packets if (event := parser.parse(packet)) is not None]


def _first_layer(packet: object, names: tuple[str, ...]) -> object | None:
    for name in names:
        if _has_layer(packet, name):
            return _get_layer(packet, name)
    return None


def _has_layer(packet: object, name: str) -> bool:
    haslayer = getattr(packet, "haslayer", None)
    if callable(haslayer):
        return bool(haslayer(name))
    return hasattr(packet, name)


def _get_layer(packet: object, name: str) -> object:
    getlayer = getattr(packet, "getlayer", None)
    if callable(getlayer):
        return getlayer(name)
    return getattr(packet, name)


def _protocol_name(layer: object) -> str:
    name = layer.__class__.__name__.upper()
    if "TCP" in name:
        return "TCP"
    if "UDP" in name:
        return "UDP"
    if "ICMP" in name:
        return "ICMP"
    return name


def _layer_int(layer: object, attribute: str) -> int | None:
    value = getattr(layer, attribute, None)
    if value is None:
        return None
    return int(value)


def _permission_message(interface: str | None) -> str:
    target = f" on interface '{interface}'" if interface else ""
    return (
        f"Packet capture permission denied{target}. Run the agent with administrator/root "
        "privileges or grant packet capture permissions to the capture driver."
    )


def _looks_like_permission_error(exc: OSError) -> bool:
    message = str(exc).lower()
    return "permission" in message or "operation not permitted" in message or "access is denied" in message

from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
import ipaddress
import random
import uuid


ALLOWED_PROTOCOLS = {"TCP", "UDP", "ICMP"}
MIN_PORT = 1
MAX_PORT = 65535
MIN_PACKET_SIZE = 1
MAX_PACKET_SIZE = 65535


@dataclass(frozen=True)
class PacketEventPayload:
    scan_id: str
    timestamp: str
    source_ip: str
    destination_ip: str
    protocol: str
    source_port: int | None
    destination_port: int | None
    packet_size: int

    def validate(self) -> None:
        uuid.UUID(self.scan_id)
        datetime.fromisoformat(self.timestamp.replace("Z", "+00:00"))
        ipaddress.ip_address(self.source_ip)
        ipaddress.ip_address(self.destination_ip)

        if self.protocol not in ALLOWED_PROTOCOLS:
            raise ValueError(f"Unsupported protocol: {self.protocol}")

        for port_name, port in (
            ("source_port", self.source_port),
            ("destination_port", self.destination_port),
        ):
            if port is not None and not MIN_PORT <= port <= MAX_PORT:
                raise ValueError(f"{port_name} must be between {MIN_PORT} and {MAX_PORT}")

        if not MIN_PACKET_SIZE <= self.packet_size <= MAX_PACKET_SIZE:
            raise ValueError(
                f"packet_size must be between {MIN_PACKET_SIZE} and {MAX_PACKET_SIZE}"
            )

    def to_dict(self) -> dict[str, str | int | None]:
        self.validate()
        return asdict(self)


class SampleEventGenerator:
    def __init__(
        self,
        scan_id: str,
        seed: int = 42,
        start_time: datetime | None = None,
    ) -> None:
        self.scan_id = scan_id
        self._random = random.Random(seed)
        self._start_time = start_time or datetime(2026, 1, 1, tzinfo=timezone.utc)

    def generate(self, count: int) -> list[PacketEventPayload]:
        if count < 1:
            raise ValueError("count must be at least 1")

        return [self.generate_one(index) for index in range(count)]

    def generate_one(self, index: int = 0) -> PacketEventPayload:
        protocol = self._random.choice(sorted(ALLOWED_PROTOCOLS))
        source_port = None if protocol == "ICMP" else self._random.randint(1024, MAX_PORT)
        destination_port = None if protocol == "ICMP" else self._pick_destination_port()

        event = PacketEventPayload(
            scan_id=self.scan_id,
            timestamp=(self._start_time + timedelta(seconds=index)).isoformat(),
            source_ip=f"192.168.1.{self._random.randint(2, 254)}",
            destination_ip=self._random.choice(["1.1.1.1", "8.8.8.8", "10.0.0.20"]),
            protocol=protocol,
            source_port=source_port,
            destination_port=destination_port,
            packet_size=self._random.randint(64, 1500),
        )
        event.validate()
        return event

    def _pick_destination_port(self) -> int:
        common_ports = [22, 53, 80, 443, 445, 3389]
        if self._random.random() < 0.7:
            return self._random.choice(common_ports)
        return self._random.randint(1024, MAX_PORT)

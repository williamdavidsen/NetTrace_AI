from datetime import timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Alert, PacketEvent

EXPECTED_PROTOCOLS = {"TCP", "UDP", "ICMP"}
SUSPICIOUS_PORTS = {
    22: "SSH",
    23: "Telnet",
    445: "SMB",
    3389: "RDP",
}
PORT_SCAN_THRESHOLD = 20
DNS_SPIKE_THRESHOLD = 50
DETECTION_WINDOW = timedelta(seconds=60)
LARGE_PACKET_THRESHOLD = 9000


def detect_alerts_for_event(session: Session, event: PacketEvent) -> list[Alert]:
    alerts: list[Alert] = []

    for alert in (
        _detect_suspicious_port(session, event),
        _detect_port_scan(session, event),
        _detect_dns_spike(session, event),
        _detect_large_packet(event),
        _detect_unknown_protocol(event),
    ):
        if alert is not None:
            alerts.append(alert)

    return alerts


def _detect_suspicious_port(session: Session, event: PacketEvent) -> Alert | None:
    if event.destination_port not in SUSPICIOUS_PORTS:
        return None

    service_name = SUSPICIOUS_PORTS[event.destination_port]
    repeated_attempts = _count_recent_events(
        session=session,
        event=event,
        destination_port=event.destination_port,
    )
    severity = "high" if repeated_attempts >= 5 else "medium"

    return Alert(
        scan_id=event.scan_id,
        severity=severity,
        title=f"Sensitive service contacted: {service_name}",
        description=(
            f"{event.source_ip} contacted {event.destination_ip} on "
            f"{service_name} port {event.destination_port}. "
            f"{repeated_attempts} matching event(s) were observed in the recent window."
        ),
        rule_name="suspicious_port",
        source_ip=event.source_ip,
    )


def _detect_port_scan(session: Session, event: PacketEvent) -> Alert | None:
    if event.destination_port is None:
        return None

    window_start = event.timestamp - DETECTION_WINDOW
    distinct_ports = session.scalar(
        select(func.count(func.distinct(PacketEvent.destination_port))).where(
            PacketEvent.scan_id == event.scan_id,
            PacketEvent.source_ip == event.source_ip,
            PacketEvent.destination_port.is_not(None),
            PacketEvent.timestamp >= window_start,
            PacketEvent.timestamp <= event.timestamp,
        )
    )
    if distinct_ports is None or distinct_ports < PORT_SCAN_THRESHOLD:
        return None

    if _alert_exists(session=session, event=event, rule_name="port_scan"):
        return None

    return Alert(
        scan_id=event.scan_id,
        severity="high",
        title="Possible port scan detected",
        description=(
            f"{event.source_ip} contacted {distinct_ports} distinct destination "
            f"ports during scan {event.scan_id}."
        ),
        rule_name="port_scan",
        source_ip=event.source_ip,
    )


def _detect_dns_spike(session: Session, event: PacketEvent) -> Alert | None:
    if event.destination_port != 53:
        return None

    dns_events = _count_recent_events(
        session=session,
        event=event,
        destination_port=53,
    )
    if dns_events < DNS_SPIKE_THRESHOLD:
        return None

    if _alert_exists(session=session, event=event, rule_name="dns_spike"):
        return None

    return Alert(
        scan_id=event.scan_id,
        severity="medium",
        title="DNS traffic spike detected",
        description=(
            f"{event.source_ip} generated {dns_events} DNS event(s) within "
            f"{int(DETECTION_WINDOW.total_seconds())} seconds."
        ),
        rule_name="dns_spike",
        source_ip=event.source_ip,
    )


def _detect_large_packet(event: PacketEvent) -> Alert | None:
    if event.packet_size <= LARGE_PACKET_THRESHOLD:
        return None

    return Alert(
        scan_id=event.scan_id,
        severity="medium",
        title="Large packet observed",
        description=(
            f"Packet metadata from {event.source_ip} reported size "
            f"{event.packet_size}, exceeding threshold {LARGE_PACKET_THRESHOLD}."
        ),
        rule_name="large_packet",
        source_ip=event.source_ip,
    )


def _detect_unknown_protocol(event: PacketEvent) -> Alert | None:
    if event.protocol in EXPECTED_PROTOCOLS:
        return None

    return Alert(
        scan_id=event.scan_id,
        severity="low",
        title="Unknown protocol observed",
        description=(
            f"Protocol {event.protocol} is outside expected values: "
            f"{', '.join(sorted(EXPECTED_PROTOCOLS))}."
        ),
        rule_name="unknown_protocol",
        source_ip=event.source_ip,
    )


def _count_recent_events(
    *,
    session: Session,
    event: PacketEvent,
    destination_port: int,
) -> int:
    window_start = event.timestamp - DETECTION_WINDOW
    count = session.scalar(
        select(func.count(PacketEvent.id)).where(
            PacketEvent.scan_id == event.scan_id,
            PacketEvent.source_ip == event.source_ip,
            PacketEvent.destination_port == destination_port,
            PacketEvent.timestamp >= window_start,
            PacketEvent.timestamp <= event.timestamp,
        )
    )
    return int(count or 0)


def _alert_exists(*, session: Session, event: PacketEvent, rule_name: str) -> bool:
    existing_alert = session.scalar(
        select(Alert).where(
            Alert.scan_id == event.scan_id,
            Alert.source_ip == event.source_ip,
            Alert.rule_name == rule_name,
        )
    )
    return existing_alert is not None

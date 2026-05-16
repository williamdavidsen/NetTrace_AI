from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Alert, PacketEvent

SENSITIVE_PORTS = {
    22: "SSH",
    23: "Telnet",
    3389: "RDP",
}
PORT_SCAN_THRESHOLD = 5


def detect_alerts_for_event(session: Session, event: PacketEvent) -> list[Alert]:
    alerts: list[Alert] = []

    sensitive_alert = _detect_sensitive_port(event)
    if sensitive_alert is not None:
        alerts.append(sensitive_alert)

    port_scan_alert = _detect_port_scan(session, event)
    if port_scan_alert is not None:
        alerts.append(port_scan_alert)

    return alerts


def _detect_sensitive_port(event: PacketEvent) -> Alert | None:
    if event.destination_port not in SENSITIVE_PORTS:
        return None

    service_name = SENSITIVE_PORTS[event.destination_port]
    return Alert(
        scan_id=event.scan_id,
        severity="medium",
        title=f"Sensitive service contacted: {service_name}",
        description=(
            f"{event.source_ip} contacted {event.destination_ip} on "
            f"{service_name} port {event.destination_port}."
        ),
        rule_name="sensitive_port",
        source_ip=event.source_ip,
    )


def _detect_port_scan(session: Session, event: PacketEvent) -> Alert | None:
    if event.destination_port is None:
        return None

    distinct_ports = session.scalar(
        select(func.count(func.distinct(PacketEvent.destination_port))).where(
            PacketEvent.scan_id == event.scan_id,
            PacketEvent.source_ip == event.source_ip,
            PacketEvent.destination_port.is_not(None),
        )
    )
    if distinct_ports is None or distinct_ports < PORT_SCAN_THRESHOLD:
        return None

    existing_alert = session.scalar(
        select(Alert).where(
            Alert.scan_id == event.scan_id,
            Alert.source_ip == event.source_ip,
            Alert.rule_name == "port_scan",
        )
    )
    if existing_alert is not None:
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

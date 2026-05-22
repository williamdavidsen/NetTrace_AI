from datetime import datetime, timezone

from support import get_json, post_json, wait_for_alert_rule


def test_alert_creation_and_explanation_endpoint() -> None:
    scan = post_json("/api/v1/scans", {"target_name": "large-packet-e2e"})
    event = {
        "scan_id": scan["id"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source_ip": "192.168.50.10",
        "destination_ip": "8.8.8.8",
        "protocol": "UDP",
        "source_port": 53000,
        "destination_port": 53,
        "packet_size": 9001,
    }

    post_json("/api/v1/events", event)
    alerts = wait_for_alert_rule("large_packet")
    explanation = get_json(f"/api/v1/alerts/{alerts[0]['id']}/explanation")

    assert alerts[0]["title"] == "Large packet observed"
    assert explanation["rule_name"] == "large_packet"
    assert explanation["recommended_action"]

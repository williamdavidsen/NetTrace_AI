from support import get_json, run_compose, wait_for_dashboard_text, wait_for_metrics


def test_agent_happy_path_reaches_dashboard() -> None:
    run_compose(
        "run",
        "--rm",
        "agent",
        "python",
        "src/main.py",
        "--create-scan",
        "--scan-target",
        "e2e-agent-flow",
        "--count",
        "10",
        "--send",
    )

    metrics = wait_for_metrics(min_events=10, min_alerts=1)
    alerts = get_json("/api/v1/alerts?limit=100&offset=0")
    html = wait_for_dashboard_text("Sensitive service contacted")

    assert metrics["processed_events_total"] >= 10
    assert any(alert["rule_name"] == "suspicious_port" for alert in alerts)
    assert "Total events" in html

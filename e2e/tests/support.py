import json
import subprocess
import time
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[2]
PROJECT_NAME = "nettrace_e2e"
BACKEND_URL = "http://localhost:18000"
FRONTEND_URL = "http://localhost:13000"
COMPOSE = [
    "docker",
    "compose",
    "-p",
    PROJECT_NAME,
    "-f",
    str(ROOT / "docker-compose.yml"),
    "-f",
    str(ROOT / "e2e" / "docker-compose.e2e.yml"),
]


def run_compose(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [*COMPOSE, *args],
        cwd=ROOT,
        check=check,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )


def wait_for_json(path: str, timeout_seconds: int = 90) -> dict[str, Any]:
    deadline = time.monotonic() + timeout_seconds
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            response = get_json(path)
            if isinstance(response, dict):
                return response
            raise AssertionError(f"Expected JSON object from {path}.")
        except Exception as exc:  # startup can race while containers become healthy
            last_error = exc
            time.sleep(2)
    raise AssertionError(f"Timed out waiting for {path}: {last_error}")


def wait_for_frontend(timeout_seconds: int = 120) -> str:
    deadline = time.monotonic() + timeout_seconds
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            return frontend_text("/dashboard")
        except Exception as exc:  # startup can race while Next.js begins serving
            last_error = exc
            time.sleep(2)
    raise AssertionError(f"Timed out waiting for frontend: {last_error}")


def wait_for_metrics(min_events: int, min_alerts: int, timeout_seconds: int = 60) -> dict[str, Any]:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        metrics = wait_for_json("/metrics", timeout_seconds=5)
        if (
            metrics["processed_events_total"] >= min_events
            and metrics["generated_alerts_total"] >= min_alerts
        ):
            return metrics
        time.sleep(1)
    raise AssertionError("Timed out waiting for expected metrics.")


def wait_for_alert_rule(rule_name: str, timeout_seconds: int = 30) -> list[dict[str, Any]]:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        alerts = get_json("/api/v1/alerts?limit=100&offset=0")
        if isinstance(alerts, list):
            matching = [alert for alert in alerts if alert["rule_name"] == rule_name]
            if matching:
                return matching
        time.sleep(1)
    raise AssertionError(f"Timed out waiting for alert rule {rule_name}.")


def wait_for_dashboard_text(text: str, timeout_seconds: int = 60) -> str:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        html = frontend_text("/dashboard")
        if text in html:
            return html
        time.sleep(2)
    raise AssertionError(f"Timed out waiting for dashboard text: {text}")


def get_json(path: str) -> dict[str, Any] | list[dict[str, Any]]:
    return json.loads(backend_text(path))


def post_json(path: str, payload: dict[str, Any]) -> dict[str, Any]:
    request = Request(
        f"{BACKEND_URL}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def backend_text(path: str) -> str:
    with urlopen(f"{BACKEND_URL}{path}", timeout=10) as response:
        return response.read().decode("utf-8")


def frontend_text(path: str) -> str:
    with urlopen(f"{FRONTEND_URL}{path}", timeout=10) as response:
        return response.read().decode("utf-8")

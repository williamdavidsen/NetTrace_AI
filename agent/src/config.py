from dataclasses import dataclass
import os


@dataclass(frozen=True)
class AgentConfig:
    backend_url: str
    scan_id: str
    event_endpoint: str = "/api/v1/events"
    scan_endpoint: str = "/api/v1/scans"
    request_timeout_seconds: float = 5.0
    default_event_count: int = 10
    random_seed: int = 42
    capture_mode: str = "sample"
    capture_interface: str | None = None
    capture_filter: str = "ip or ip6"
    capture_timeout_seconds: int | None = None
    scan_target_name: str = "docker-compose-agent"

    @property
    def event_url(self) -> str:
        return f"{self.backend_url.rstrip('/')}{self.event_endpoint}"

    @property
    def scan_url(self) -> str:
        return f"{self.backend_url.rstrip('/')}{self.scan_endpoint}"


def load_config() -> AgentConfig:
    return AgentConfig(
        backend_url=os.getenv(
            "NETTRACE_BACKEND_URL",
            os.getenv("AGENT_BACKEND_URL", "http://localhost:8000"),
        ),
        scan_id=os.getenv(
            "NETTRACE_SCAN_ID",
            os.getenv("AGENT_SCAN_ID", "00000000-0000-0000-0000-000000000001"),
        ),
        event_endpoint=os.getenv("NETTRACE_EVENT_ENDPOINT", "/api/v1/events"),
        scan_endpoint=os.getenv("NETTRACE_SCAN_ENDPOINT", "/api/v1/scans"),
        request_timeout_seconds=float(os.getenv("NETTRACE_AGENT_TIMEOUT_SECONDS", "5")),
        default_event_count=int(
            os.getenv("NETTRACE_AGENT_EVENT_COUNT", os.getenv("AGENT_EVENT_COUNT", "10"))
        ),
        random_seed=int(os.getenv("NETTRACE_AGENT_RANDOM_SEED", "42")),
        capture_mode=os.getenv(
            "NETTRACE_AGENT_CAPTURE_MODE",
            os.getenv("AGENT_CAPTURE_MODE", "sample"),
        ),
        capture_interface=os.getenv("NETTRACE_AGENT_CAPTURE_INTERFACE") or None,
        capture_filter=os.getenv("NETTRACE_AGENT_CAPTURE_FILTER", "ip or ip6"),
        capture_timeout_seconds=_optional_int(
            os.getenv("NETTRACE_AGENT_CAPTURE_TIMEOUT_SECONDS")
        ),
        scan_target_name=os.getenv("NETTRACE_AGENT_SCAN_TARGET_NAME", "docker-compose-agent"),
    )


def _optional_int(value: str | None) -> int | None:
    if value is None or value == "":
        return None
    return int(value)

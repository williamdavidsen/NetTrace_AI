from dataclasses import dataclass
import os


@dataclass(frozen=True)
class AgentConfig:
    backend_url: str
    scan_id: str
    event_endpoint: str = "/api/v1/events"
    request_timeout_seconds: float = 5.0
    default_event_count: int = 10
    random_seed: int = 42

    @property
    def event_url(self) -> str:
        return f"{self.backend_url.rstrip('/')}{self.event_endpoint}"


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
        request_timeout_seconds=float(os.getenv("NETTRACE_AGENT_TIMEOUT_SECONDS", "5")),
        default_event_count=int(
            os.getenv("NETTRACE_AGENT_EVENT_COUNT", os.getenv("AGENT_EVENT_COUNT", "10"))
        ),
        random_seed=int(os.getenv("NETTRACE_AGENT_RANDOM_SEED", "42")),
    )

from config import load_config


def test_load_config_uses_defaults(monkeypatch) -> None:
    monkeypatch.delenv("NETTRACE_BACKEND_URL", raising=False)
    monkeypatch.delenv("NETTRACE_SCAN_ID", raising=False)
    monkeypatch.delenv("NETTRACE_AGENT_CAPTURE_MODE", raising=False)
    monkeypatch.delenv("NETTRACE_AGENT_CAPTURE_INTERFACE", raising=False)
    monkeypatch.delenv("NETTRACE_AGENT_CAPTURE_FILTER", raising=False)
    monkeypatch.delenv("NETTRACE_AGENT_CAPTURE_TIMEOUT_SECONDS", raising=False)

    config = load_config()

    assert config.backend_url == "http://localhost:8000"
    assert config.scan_id == "00000000-0000-0000-0000-000000000001"
    assert config.event_url == "http://localhost:8000/api/v1/events"
    assert config.scan_url == "http://localhost:8000/api/v1/scans"
    assert config.capture_mode == "sample"
    assert config.capture_interface is None
    assert config.capture_filter == "ip or ip6"
    assert config.capture_timeout_seconds is None


def test_load_config_reads_environment(monkeypatch) -> None:
    monkeypatch.setenv("NETTRACE_BACKEND_URL", "http://api.local/")
    monkeypatch.setenv("NETTRACE_SCAN_ID", "11111111-1111-1111-1111-111111111111")
    monkeypatch.setenv("NETTRACE_AGENT_EVENT_COUNT", "3")
    monkeypatch.setenv("NETTRACE_AGENT_RANDOM_SEED", "7")
    monkeypatch.setenv("NETTRACE_AGENT_CAPTURE_MODE", "capture")
    monkeypatch.setenv("NETTRACE_AGENT_CAPTURE_INTERFACE", "eth0")
    monkeypatch.setenv("NETTRACE_AGENT_CAPTURE_FILTER", "tcp")
    monkeypatch.setenv("NETTRACE_AGENT_CAPTURE_TIMEOUT_SECONDS", "2")
    monkeypatch.setenv("NETTRACE_SCAN_ENDPOINT", "/custom/scans")
    monkeypatch.setenv("NETTRACE_AGENT_SCAN_TARGET_NAME", "compose-smoke")

    config = load_config()

    assert config.event_url == "http://api.local/api/v1/events"
    assert config.scan_url == "http://api.local/custom/scans"
    assert config.scan_id == "11111111-1111-1111-1111-111111111111"
    assert config.default_event_count == 3
    assert config.random_seed == 7
    assert config.capture_mode == "capture"
    assert config.capture_interface == "eth0"
    assert config.capture_filter == "tcp"
    assert config.capture_timeout_seconds == 2
    assert config.scan_target_name == "compose-smoke"

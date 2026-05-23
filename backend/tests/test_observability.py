import json
import logging

from fastapi.testclient import TestClient

from app.core.observability import JsonLogFormatter
from app.main import create_app


def test_request_id_is_returned_and_preserved() -> None:
    client = TestClient(create_app())

    response = client.get("/health", headers={"x-request-id": "request-123"})

    assert response.status_code == 200
    assert response.headers["x-request-id"] == "request-123"


def test_structured_log_formatter_outputs_json() -> None:
    record = logging.LogRecord(
        name="nettrace",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="request.completed",
        args=(),
        exc_info=None,
    )
    record.request_id = "request-123"
    record.method = "GET"
    record.path = "/health"
    record.status_code = 200
    record.duration_ms = 1.2

    payload = json.loads(JsonLogFormatter().format(record))

    assert payload["message"] == "request.completed"
    assert payload["request_id"] == "request-123"
    assert payload["status_code"] == 200


def test_failed_requests_are_logged(monkeypatch) -> None:
    from app.core import observability

    logged: list[tuple[str, dict[str, object]]] = []

    def record_exception(message: str, *args, **kwargs) -> None:
        logged.append((message, kwargs["extra"]))

    monkeypatch.setattr(observability.logger, "exception", record_exception)
    app = create_app()

    @app.get("/boom")
    def boom() -> None:
        raise RuntimeError("boom")

    client = TestClient(app, raise_server_exceptions=False)

    response = client.get("/boom", headers={"x-request-id": "failure-123"})

    assert response.status_code == 500
    assert logged == [
        (
            "request.failed",
            {
                "request_id": "failure-123",
                "method": "GET",
                "path": "/boom",
                "status_code": 500,
                "duration_ms": logged[0][1]["duration_ms"],
                "client": "testclient",
                "error_type": "RuntimeError",
            },
        )
    ]

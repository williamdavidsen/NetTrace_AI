from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.main import create_app


def test_cors_allows_configured_frontend_origin() -> None:
    client = TestClient(create_app())

    response = client.options(
        "/api/v1/status",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"


def test_validation_errors_use_safe_response_shape() -> None:
    client = TestClient(create_app())

    response = client.post("/api/v1/scans", json={"target_name": "   "})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"
    assert response.json()["error"]["message"] == "Request validation failed."


def test_http_errors_use_safe_response_shape(db_session: Session) -> None:
    client = _client_with_session(db_session)

    response = client.get("/api/v1/scans/11111111-1111-1111-1111-111111111111")

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "http_error",
            "message": "Scan not found.",
        }
    }


def test_rate_limit_blocks_excessive_requests() -> None:
    from app import main as main_module

    original_requests = main_module.settings.rate_limit_requests
    original_window = main_module.settings.rate_limit_window_seconds
    object.__setattr__(main_module.settings, "rate_limit_requests", 2)
    object.__setattr__(main_module.settings, "rate_limit_window_seconds", 60)
    try:
        client = TestClient(create_app())

        assert client.get("/health").status_code == 200
        assert client.get("/health").status_code == 200
        response = client.get("/health")
    finally:
        object.__setattr__(main_module.settings, "rate_limit_requests", original_requests)
        object.__setattr__(main_module.settings, "rate_limit_window_seconds", original_window)

    assert response.status_code == 429
    assert response.headers["retry-after"] == "60"
    assert response.json()["error"]["code"] == "rate_limit_exceeded"


def _client_with_session(db_session: Session) -> TestClient:
    app = create_app()

    def override_get_session() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_session] = override_get_session
    return TestClient(app)

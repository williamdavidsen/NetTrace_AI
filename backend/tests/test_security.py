from fastapi.testclient import TestClient

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

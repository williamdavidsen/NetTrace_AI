from fastapi.testclient import TestClient

from app.main import create_app


def test_status_endpoint_returns_backend_status() -> None:
    client = TestClient(create_app())

    response = client.get("/api/v1/status")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "nettrace-backend",
        "environment": "development",
    }

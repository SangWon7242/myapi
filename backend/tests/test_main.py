from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_hello_returns_backend_message() -> None:
    response = client.get("/hello")

    assert response.status_code == 200
    assert response.json() == {"message": "hello world"}


def test_cors_allows_local_next_app() -> None:
    response = client.options(
        "/hello",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_read_main() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}


def test_error_handling_verification() -> None:
    """Intentionally failing test to verify CI error handling"""
    assert False, "This test is intentionally failing to verify error handling"

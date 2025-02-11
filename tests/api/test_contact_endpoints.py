import pytest
from fastapi.testclient import TestClient


def test_create_contact_with_minimal_data(client: TestClient):
    """
    Test creating a contact with only required fields (name)
    """
    contact_data = {"name": "John Doe"}

    response = client.post("/api/contacts", json=contact_data)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == contact_data["name"]
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

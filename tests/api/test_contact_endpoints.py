import pytest
from typing import Any, Dict
from fastapi.testclient import TestClient
from http import HTTPStatus
from sqlalchemy.orm import Session
from backend.app.models.contact import Contact


def test_create_contact_with_minimal_data(client: TestClient):
    """
    Test creating a contact with only required fields (name)
    """
    contact_data = {"name": "John Doe"}

    # Create via API
    response = client.post("/api/contacts", json=contact_data)
    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    assert data["name"] == contact_data["name"]
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.parametrize(
    "invalid_data,expected_error",
    [
        ({}, "Field required"),
        ({"name": ""}, "String should have at least 1 character"),
        (
            {"name": "a" * 101},
            "String should have at most 100 characters"
        ),
    ],
)
def test_create_contact_with_invalid_data(
    client: TestClient,
    invalid_data: Dict[str, Any],
    expected_error: str,
):
    """
    Test creating a contact with invalid data returns appropriate error
    messages
    """
    response = client.post("/api/contacts", json=invalid_data)

    assert response.status_code == HTTPStatus.BAD_REQUEST
    data = response.json()
    assert "error" in data
    assert expected_error.lower() in data["error"].lower()


def test_get_nonexistent_contact(client: TestClient):
    """
    Test attempting to get a contact that doesn't exist returns 404
    """
    response = client.get("/api/contacts/00000000-0000-0000-0000-000000000000")

    assert response.status_code == HTTPStatus.NOT_FOUND
    data = response.json()
    assert "error" in data
    assert "not found" in data["error"].lower()


def test_create_contact_with_malformed_json(client: TestClient):
    """
    Test sending malformed JSON returns appropriate error
    """
    malformed_json = "{invalid json"
    response = client.post(
        "/api/contacts",
        headers={"Content-Type": "application/json"},
        content=malformed_json.encode(),
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    data = response.json()
    assert "error" in data
    assert "json decode error" in data["error"].lower()


@pytest.mark.parametrize(
    "field,invalid_value,expected_error",
    [
        (
            "hashtags",
            "not-a-list",
            "Input should be a valid list"
        ),
        (
            "sub_information",
            "not-a-dict",
            "Input should be a valid dictionary"
        ),
    ],
)
def test_create_contact_with_invalid_field_formats(
    client: TestClient,
    field: str,
    invalid_value: Any,
    expected_error: str,
):
    """
    Test creating contacts with invalid field formats returns appropriate
    errors
    """
    contact_data: Dict[str, Any] = {"name": "John Doe", field: invalid_value}

    response = client.post("/api/contacts", json=contact_data)

    assert response.status_code == HTTPStatus.BAD_REQUEST
    data = response.json()
    assert "error" in data
    assert expected_error.lower() in data["error"].lower()


def test_get_contact_successful(client: TestClient, db_session: Session):
    """
    Test successfully retrieving an existing contact
    """
    # Create a contact in the database
    contact = Contact()
    contact.name = "John Doe"
    contact.first_name = "John"
    contact.contact_briefing_text = "Test contact"
    contact.sub_information = {"role": "test"}
    contact.hashtags = ["#test"]
    db_session.add(contact)
    db_session.commit()
    db_session.refresh(contact)

    # Retrieve via API
    response = client.get(f"/api/contacts/{contact.id}")

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data["name"] == contact.name
    assert data["first_name"] == contact.first_name
    assert data["contact_briefing_text"] == contact.contact_briefing_text
    assert data["sub_information"] == contact.sub_information
    assert data["hashtags"] == contact.hashtags
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

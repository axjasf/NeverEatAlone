import pytest
from typing import Any, Dict
from fastapi.testclient import TestClient
from http import HTTPStatus
from sqlalchemy.orm import Session
from backend.app.models.contact import Contact, Hashtag, EntityType


def test_create_contact_with_minimal_data(client: TestClient):
    """Test creating a contact with only required fields.

    This test verifies that:
    1. A contact can be created with only the required name field
    2. The response includes the correct name
    3. System fields (id, created_at, updated_at) are present
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
        ({"name": "a" * 101}, "String should have at most 100 characters"),
    ],
)
def test_create_contact_with_invalid_data(
    client: TestClient,
    invalid_data: Dict[str, Any],
    expected_error: str,
):
    """Test creating a contact with invalid data returns appropriate errors.

    This test verifies that:
    1. Invalid data results in a 400 Bad Request response
    2. The error message matches the expected validation error
    3. The error format follows the standard error response format
    """
    response = client.post("/api/contacts", json=invalid_data)

    assert response.status_code == HTTPStatus.BAD_REQUEST
    data = response.json()
    assert "error" in data
    assert expected_error.lower() in data["error"].lower()


def test_get_nonexistent_contact(client: TestClient):
    """Test attempting to get a non-existent contact.

    This test verifies that:
    1. Request for non-existent UUID returns 404 Not Found
    2. The error message indicates the contact was not found
    3. The error format follows the standard error response format
    """
    response = client.get("/api/contacts/00000000-0000-0000-0000-000000000000")

    assert response.status_code == HTTPStatus.NOT_FOUND
    data = response.json()
    assert "error" in data
    assert "not found" in data["error"].lower()


def test_create_contact_with_malformed_json(client: TestClient):
    """Test sending malformed JSON data.

    This test verifies that:
    1. Malformed JSON results in a 400 Bad Request response
    2. The error message indicates a JSON decode error
    3. The error format follows the standard error response format
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
        ("hashtags", "not-a-list", "Input should be a valid list"),
        ("sub_information", "not-a-dict", "Input should be a valid dictionary"),
    ],
)
def test_create_contact_with_invalid_field_formats(
    client: TestClient,
    field: str,
    invalid_value: Any,
    expected_error: str,
):
    """Test creating contacts with invalid field formats.

    This test verifies that:
    1. Invalid field types result in a 400 Bad Request response
    2. The error message matches the expected type validation error
    3. The error format follows the standard error response format
    """
    contact_data: Dict[str, Any] = {"name": "John Doe", field: invalid_value}

    response = client.post("/api/contacts", json=contact_data)

    assert response.status_code == HTTPStatus.BAD_REQUEST
    data = response.json()
    assert "error" in data
    assert expected_error.lower() in data["error"].lower()


def test_get_contact_successful(client: TestClient, db_session: Session):
    """Test successfully retrieving an existing contact.

    This test verifies that:
    1. Contact can be retrieved using its ID
    2. All fields match the stored contact data
    3. System fields (id, created_at, updated_at) are present
    4. Optional fields (first_name, sub_information, hashtags) are included
    """
    # Create a contact in the database
    contact = Contact()
    contact.name = "John Doe"
    contact.first_name = "John"
    contact.contact_briefing_text = "Test contact"
    contact.sub_information = {"role": "test"}
    db_session.add(contact)
    contact.set_hashtags(["#test"])
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
    assert data["hashtags"] == contact.hashtag_names
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_update_contact_successful(client: TestClient, db_session: Session):
    """
    Test successfully updating an existing contact

    This test verifies that:
    1. We can update all fields of an existing contact
    2. The response contains the updated values
    3. The updated_at timestamp is updated
    4. The ID and other metadata remain unchanged
    """
    # Create a contact in the database
    contact = Contact()
    contact.name = "John Doe"
    contact.first_name = "John"
    contact.contact_briefing_text = "Original text"
    contact.sub_information = {"role": "original"}
    db_session.add(contact)
    contact.set_hashtags(["#original"])
    db_session.commit()
    original_id = contact.id
    original_created_at = contact.created_at

    # Prepare update data with changes to all fields
    update_data = {
        "name": "John Smith",
        "first_name": "Johnny",
        "contact_briefing_text": "Updated contact info",
        "sub_information": {"role": "developer", "team": "backend"},
        "hashtags": ["#updated", "#developer"],
    }

    # Update via API
    response = client.put(f"/api/contacts/{contact.id}", json=update_data)

    # Verify response
    assert response.status_code == HTTPStatus.OK
    data = response.json()

    # Verify all fields are updated
    assert data["name"] == update_data["name"]
    assert data["first_name"] == update_data["first_name"]
    assert data["contact_briefing_text"] == update_data["contact_briefing_text"]
    assert data["sub_information"] == update_data["sub_information"]
    assert data["hashtags"] == update_data["hashtags"]

    # Verify metadata
    assert data["id"] == str(original_id)
    assert data["created_at"] == original_created_at.isoformat()
    assert "updated_at" in data
    assert data["updated_at"] > data["created_at"]

    # Verify persistence by retrieving again
    get_response = client.get(f"/api/contacts/{contact.id}")
    get_data = get_response.json()
    assert get_data == data


def test_update_nonexistent_contact(client: TestClient):
    """
    Test attempting to update a contact that doesn't exist returns 404

    This test verifies that:
    1. Attempting to update a non-existent contact returns 404
    2. The error message indicates the contact was not found
    """
    # Prepare update data
    update_data = {"name": "John Smith"}

    # Use a non-existent UUID
    contact_id = "00000000-0000-0000-0000-000000000000"

    # Attempt update
    response = client.put(f"/api/contacts/{contact_id}", json=update_data)

    # Verify response
    assert response.status_code == HTTPStatus.NOT_FOUND
    data = response.json()
    assert "error" in data
    assert "not found" in data["error"].lower()


@pytest.mark.parametrize(
    "invalid_data,expected_error",
    [
        ({"name": ""}, "String should have at least 1 character"),
        ({"name": "a" * 101}, "String should have at most 100 characters"),
        (
            {"name": "John Doe", "hashtags": ["invalid"]},
            "Each hashtag must be a string starting with #",
        ),
        (
            {"name": "John Doe", "sub_information": "not-a-dict"},
            "Input should be a valid dictionary",
        ),
    ],
)
def test_update_contact_with_invalid_data(
    client: TestClient,
    db_session: Session,
    invalid_data: Dict[str, Any],
    expected_error: str,
):
    """
    Test updating a contact with invalid data returns appropriate errors

    This test verifies that:
    1. Validation rules are enforced during updates
    2. Appropriate error messages are returned
    3. The contact remains unchanged after failed update
    """
    # Create a contact to update
    contact = Contact()
    contact.name = "John Doe"
    contact.first_name = "John"
    contact.contact_briefing_text = "Original text"
    db_session.add(contact)
    contact.set_hashtags(["#original"])
    db_session.commit()

    # Get the ID and original values
    contact_id = contact.id
    original_name = contact.name
    original_first_name = contact.first_name
    original_text = contact.contact_briefing_text

    # Attempt update with invalid data
    response = client.put(f"/api/contacts/{contact_id}", json=invalid_data)

    # Verify error response
    assert response.status_code == HTTPStatus.BAD_REQUEST
    data = response.json()
    assert "error" in data
    assert expected_error.lower() in data["error"].lower()

    # Clear the session and verify contact remains unchanged
    db_session.expunge_all()
    db_contact = db_session.get(Contact, contact_id)
    assert db_contact is not None
    assert db_contact.name == original_name
    assert db_contact.first_name == original_first_name
    assert db_contact.contact_briefing_text == original_text


def test_delete_contact_successful(client: TestClient, db_session: Session):
    """Test successfully deleting an existing contact.

    This test verifies that:
    1. A contact can be deleted using its ID
    2. The response has a 204 No Content status
    3. The contact is actually removed from the database
    4. Subsequent GET requests return 404
    """
    # Create a contact to delete
    contact = Contact()
    contact.name = "To Be Deleted"
    db_session.add(contact)
    db_session.commit()
    contact_id = contact.id

    # Delete via API
    response = client.delete(f"/api/contacts/{contact_id}")
    assert response.status_code == HTTPStatus.NO_CONTENT
    assert response.content == b""  # No content in response body

    # Verify contact is gone from database
    deleted_contact = db_session.get(Contact, contact_id)
    assert deleted_contact is None

    # Verify GET returns 404
    get_response = client.get(f"/api/contacts/{contact_id}")
    assert get_response.status_code == HTTPStatus.NOT_FOUND


def test_delete_nonexistent_contact(client: TestClient):
    """Test attempting to delete a non-existent contact.

    This test verifies that:
    1. Attempting to delete a non-existent contact returns 404
    2. The error message indicates the contact was not found
    3. The error format follows the standard error response format
    """
    response = client.delete("/api/contacts/00000000-0000-0000-0000-000000000000")

    assert response.status_code == HTTPStatus.NOT_FOUND
    data = response.json()
    assert "error" in data
    assert "not found" in data["error"].lower()


def test_delete_contact_invalid_uuid(client: TestClient):
    """Test attempting to delete a contact with invalid UUID format.

    This test verifies that:
    1. Invalid UUID format results in 400 Bad Request
    2. The error message indicates the UUID format issue
    3. The error format follows the standard error response format
    """
    response = client.delete("/api/contacts/not-a-uuid")

    assert response.status_code == HTTPStatus.BAD_REQUEST
    data = response.json()
    assert "error" in data
    assert "uuid" in data["error"].lower()


def test_list_contacts_empty(client: TestClient):
    """Test listing contacts when database is empty.

    This test verifies that:
    1. Response has 200 OK status
    2. Response body contains empty items list
    3. Response includes total_count of 0
    """
    response = client.get("/api/contacts")

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert "items" in data
    assert len(data["items"]) == 0
    assert data["total_count"] == 0


def test_list_contacts_multiple(client: TestClient, db_session: Session):
    """Test listing multiple contacts.

    This test verifies that:
    1. Response has 200 OK status
    2. All contacts are returned in items list
    3. Total count matches number of contacts
    4. Each contact has all expected fields
    """
    # Create test contacts
    contacts = [
        Contact(name="Alice"),
        Contact(name="Bob"),
        Contact(name="Charlie"),
    ]
    for contact in contacts:
        db_session.add(contact)
    db_session.commit()

    # Get list via API
    response = client.get("/api/contacts")

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert "items" in data
    assert len(data["items"]) == len(contacts)
    assert data["total_count"] == len(contacts)

    # Verify each contact has required fields
    for item in data["items"]:
        assert "id" in item
        assert "name" in item
        assert "created_at" in item
        assert "updated_at" in item


@pytest.mark.parametrize(
    "name_filter,expected_count",
    [
        ("Alice", 1),  # Exact match
        ("bob", 1),  # Case insensitive
        ("li", 2),  # Partial match (Alice, Charlie)
        ("David", 0),  # No matches
    ],
)
def test_list_contacts_name_filter(
    client: TestClient,
    db_session: Session,
    name_filter: str,
    expected_count: int,
):
    """Test filtering contacts by name.

    This test verifies that:
    1. Name filter works case-insensitively
    2. Partial name matches are found
    3. Total count reflects filtered results
    4. No results when filter doesn't match
    """
    # Create test contacts
    contacts = [
        Contact(name="Alice"),
        Contact(name="Bob"),
        Contact(name="Charlie"),
    ]
    for contact in contacts:
        db_session.add(contact)
    db_session.commit()

    # Get filtered list
    response = client.get(f"/api/contacts?name={name_filter}")

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert len(data["items"]) == expected_count
    assert data["total_count"] == expected_count

    # Verify matches contain filter string
    for item in data["items"]:
        assert name_filter.lower() in item["name"].lower()


def test_list_contacts_hashtag_filter(client: TestClient, db_session: Session):
    """Test filtering contacts by hashtags.

    This test verifies that:
    1. Contacts can be filtered by a single hashtag
    2. Contacts can be filtered by multiple hashtags (AND logic)
    3. Hashtag filtering is case-insensitive
    4. Non-matching hashtags return empty results
    5. Invalid hashtags (without #) return empty results
    """
    print("\n=== Setting up test data ===")
    # Create test contacts
    contacts = [
        Contact(name="Alice"),
        Contact(name="Bob"),
        Contact(name="Charlie"),
    ]

    # Add contacts to session first
    for contact in contacts:
        db_session.add(contact)
    db_session.flush()
    print("Created contacts:", [c.name for c in contacts])

    # Create hashtags
    test_tag = "#test"
    dev_tag = "#dev"
    prod_tag = "#prod"
    print("Created hashtags:", [test_tag, dev_tag, prod_tag])

    # Associate hashtags with contacts
    print("\n=== Associating hashtags ===")
    # Alice: #test, #dev
    contacts[0].set_hashtags([test_tag, dev_tag])
    print(f"Alice's tags: {contacts[0].hashtag_names}")
    # Bob: #dev
    contacts[1].set_hashtags([dev_tag])
    print(f"Bob's tags: {contacts[1].hashtag_names}")
    # Charlie: #prod
    contacts[2].set_hashtags([prod_tag])
    print(f"Charlie's tags: {contacts[2].hashtag_names}")

    db_session.commit()

    print("\n=== Verifying database state ===")
    # Verify hashtags in database
    all_hashtags = db_session.query(Hashtag).all()
    print("All hashtags in DB:", [h.name for h in all_hashtags])

    # Verify contact associations
    for contact in contacts:
        db_session.refresh(contact)
        print(f"Contact {contact.name} has tags: {contact.hashtag_names}")

    print("\n=== Running test cases ===")
    # Test single hashtag filter
    print("\nTesting single hashtag filter: #test")
    response = client.get("/api/contacts?hashtags=#test")
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    print("Response data:", data)
    assert data["total_count"] == 1  # Only Alice has #test
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "Alice"

    # Test multiple hashtags (AND logic)
    response = client.get("/api/contacts?hashtags=#test,#dev")
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data["total_count"] == 1  # Only Alice has both #test and #dev
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "Alice"

    # Test case insensitivity
    response = client.get("/api/contacts?hashtags=#TEST")
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data["total_count"] == 1  # Only Alice has #test
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "Alice"

    # Test non-matching hashtag
    response = client.get("/api/contacts?hashtags=#nonexistent")
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data["total_count"] == 0
    assert len(data["items"]) == 0

    # Test invalid hashtag format
    response = client.get("/api/contacts?hashtags=invalid")
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data["total_count"] == 0
    assert len(data["items"]) == 0


def test_contact_hashtags_validation(client: TestClient):
    """Test hashtag validation during contact creation.

    This test verifies that:
    1. Hashtags must start with #
    2. Hashtags are stored in lowercase
    3. Invalid hashtag format returns 400
    """
    # Test invalid hashtag format
    contact_data = {"name": "John Doe", "hashtags": ["invalid"]}  # Missing #
    response = client.post("/api/contacts", json=contact_data)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    data = response.json()
    assert "error" in data
    assert "each hashtag must be a string starting with #" in data["error"].lower()

    # Test valid hashtags with mixed case
    contact_data = {"name": "John Doe", "hashtags": ["#TEST", "#Dev"]}
    response = client.post("/api/contacts", json=contact_data)
    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    assert set(data["hashtags"]) == {"#test", "#dev"}  # Should be lowercase


def test_update_contact_hashtags(client: TestClient, db_session: Session):
    """Test updating contact hashtags.

    This test verifies that:
    1. Hashtags can be added to existing contact
    2. Hashtags can be removed from contact
    3. Hashtags can be completely replaced
    4. Case is preserved in response but normalized in storage
    """
    # Create initial contact with hashtags
    contact = Contact(name="John Doe")
    db_session.add(contact)
    contact.set_hashtags(["#initial"])
    db_session.commit()

    # Update with new hashtags
    update_data = {"name": "John Doe", "hashtags": ["#NEW", "#tags"]}
    response = client.put(f"/api/contacts/{contact.id}", json=update_data)
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert set(data["hashtags"]) == {"#new", "#tags"}

    # Remove all hashtags
    update_data["hashtags"] = []
    response = client.put(f"/api/contacts/{contact.id}", json=update_data)
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert not data["hashtags"]

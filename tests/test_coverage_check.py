"""Simple test file to verify coverage reporting."""

from datetime import datetime, UTC
from uuid import uuid4
from backend.app.models.domain.contact_model import Contact


def test_contact_creation_coverage():
    """Test creating a contact with all fields to ensure coverage."""
    contact_id = uuid4()
    now = datetime.now(UTC)

    # Create contact with all possible fields
    contact = Contact(
        name="Coverage Test",
        first_name="Coverage",
        briefing_text="Testing coverage reporting",
        sub_information={
            "test": "value",
            "nested": {
                "key": "value"
            }
        },
        last_contact=now,
        contact_briefing_text="Last contact test"
    )

    # Set ID manually to test ID handling
    contact.id = contact_id

    # Verify all fields
    assert contact.id == contact_id
    assert contact.name == "Coverage Test"
    assert contact.first_name == "Coverage"
    assert contact.briefing_text == "Testing coverage reporting"
    assert contact.sub_information["test"] == "value"
    assert contact.sub_information["nested"]["key"] == "value"
    assert contact.last_contact == now
    assert contact.contact_briefing_text == "Last contact test"

    # Test tag management
    contact.add_tag("#test")
    contact.add_tag("#coverage")
    assert len(contact.tags) == 2
    assert "#test" in contact.hashtag_names
    assert "#coverage" in contact.hashtag_names

    # Test note management
    note = contact.add_note("Test note for coverage")
    assert len(contact.notes) == 1
    assert note.content == "Test note for coverage"

    # Test removing items
    contact.remove_note(note)
    assert len(contact.notes) == 0

    tag_to_remove = next(t for t in contact.tags if t.name == "#test")
    contact.remove_tag(tag_to_remove)
    assert len(contact.tags) == 1
    assert "#test" not in contact.hashtag_names


def test_contact_validation_coverage():
    """Test contact validation scenarios for coverage."""
    # Test invalid sub_information
    try:
        Contact(name="Invalid", sub_information="not a dict")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert str(e) == "sub_information must be a dictionary"

    # Test invalid tag
    contact = Contact(name="Tag Test")
    try:
        contact.add_tag("invalid")  # Missing #
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert str(e) == "Tag must start with #"

    # Test empty note
    try:
        contact.add_note("")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert str(e) == "Content cannot be empty"

    # Test whitespace note
    try:
        contact.add_note("   ")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert str(e) == "Content cannot be empty"

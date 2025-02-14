"""Tests for the Contact domain model."""

import pytest
from uuid import UUID
from backend.app.models.domain.contact import Contact
from backend.app.models.domain.tag import Tag, EntityType


TEST_UUID = UUID("11111111-1111-1111-1111-111111111111")


def test_contact_creation():
    """Test creating a contact with basic properties.

    A contact must have:
    1. A name
    2. Optional first name
    3. Optional briefing text
    4. Optional sub_information dictionary
    """
    # Test with only required fields
    contact = Contact(name="John Doe")
    assert contact.name == "John Doe"
    assert contact.first_name is None
    assert contact.briefing_text is None
    assert contact.sub_information == {}
    assert contact.notes == []
    assert contact.tags == []

    # Test with all fields
    sub_info = {"family_status": "Married", "professional_situation": "CEO"}
    contact = Contact(
        name="John Doe",
        first_name="John",
        briefing_text="Important business contact",
        sub_information=sub_info,
    )
    assert contact.name == "John Doe"
    assert contact.first_name == "John"
    assert contact.briefing_text == "Important business contact"
    assert contact.sub_information == sub_info


def test_contact_sub_information_validation():
    """Test sub_information validation.

    Sub_information rules:
    1. Must be a dictionary if provided
    2. Defaults to empty dict if not provided
    3. Can contain nested dictionaries
    """
    # Test invalid type
    with pytest.raises(ValueError):
        Contact(name="John Doe", sub_information="invalid")

    # Test default empty dict
    contact = Contact(name="John Doe")
    assert contact.sub_information == {}

    # Test nested dictionary
    sub_info = {
        "personal": {
            "hobbies": ["reading", "hiking"],
            "family": {"status": "married", "children": 2},
        },
        "professional": {"role": "developer", "skills": ["python", "typescript"]},
    }
    contact = Contact(name="John Doe", sub_information=sub_info)
    assert contact.sub_information == sub_info


def test_contact_tag_management():
    """Test adding and managing tags.

    Tag management rules:
    1. Can add tags
    2. Tags must start with #
    3. Tags are stored in lowercase
    4. Duplicate tags are ignored
    5. Can remove tags
    """
    contact = Contact(name="John Doe")

    # Add valid tags
    contact.add_tag("#test")
    contact.add_tag("#project")

    assert len(contact.tags) == 2
    assert "#test" in [t.name for t in contact.tags]
    assert "#project" in [t.name for t in contact.tags]

    # Test invalid tag format
    with pytest.raises(ValueError, match="Tag must start with #"):
        contact.add_tag("invalid")

    # Test duplicate tag
    contact.add_tag("#test")  # Should be ignored
    assert len(contact.tags) == 2

    # Test case normalization
    contact.add_tag("#TEST")  # Should be normalized to #test
    assert len(contact.tags) == 2

    # Remove tag
    test_tag = next(t for t in contact.tags if t.name == "#test")
    contact.remove_tag(test_tag)
    assert len(contact.tags) == 1
    assert "#test" not in [t.name for t in contact.tags]


def test_contact_note_management():
    """Test adding and managing notes.

    Note management rules:
    1. Can add notes
    2. Notes maintain order
    3. Can remove notes
    4. Note content is validated
    """
    contact = Contact(name="John Doe")

    # Add notes
    note1 = contact.add_note("First note")
    note2 = contact.add_note("Second note")

    assert len(contact.notes) == 2
    assert contact.notes[0] is note1
    assert contact.notes[1] is note2
    assert note1.content == "First note"
    assert note2.content == "Second note"

    # Test empty note
    with pytest.raises(ValueError, match="Content cannot be empty"):
        contact.add_note("")

    # Test whitespace note
    with pytest.raises(ValueError, match="Content cannot be empty"):
        contact.add_note("   ")

    # Remove note
    contact.remove_note(note1)
    assert len(contact.notes) == 1
    assert contact.notes[0] is note2
    assert contact.notes[0].content == "Second note"

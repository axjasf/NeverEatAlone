"""Tests for the Note domain model."""
import pytest
from datetime import datetime, UTC
from uuid import UUID
from typing import List

# We'll create these domain models next
from backend.app.models.domain.note import Note, Statement
from backend.app.models.domain.tag import Tag


TEST_UUID = UUID("11111111-1111-1111-1111-111111111111")


def test_note_creation():
    """Test creating a note with required fields.

    A note must have:
    1. A contact_id identifying which contact it belongs to
    2. Content (the actual note text)
    """
    note = Note(
        contact_id=TEST_UUID,
        content="Test note content"
    )

    assert note.contact_id == TEST_UUID
    assert note.content == "Test note content"
    assert note.statements == []
    assert note.tags == []
    assert isinstance(note.created_at, datetime)
    assert isinstance(note.updated_at, datetime)


def test_note_content_validation():
    """Test note content validation.

    Content validation rules:
    1. Content cannot be empty
    2. Content cannot be just whitespace
    3. Content is trimmed
    """
    # Test empty content
    with pytest.raises(ValueError, match="Content cannot be empty"):
        Note(contact_id=TEST_UUID, content="")

    # Test whitespace content
    with pytest.raises(ValueError, match="Content cannot be empty"):
        Note(contact_id=TEST_UUID, content="   ")

    # Test content trimming
    note = Note(contact_id=TEST_UUID, content="  Test content  ")
    assert note.content == "Test content"


def test_note_statement_management():
    """Test adding and managing statements.

    Statement management rules:
    1. Can add statements
    2. Statements maintain order
    3. Can remove statements
    4. Statement content is validated
    """
    note = Note(contact_id=TEST_UUID, content="Main note")

    # Add statements
    note.add_statement("First statement")
    note.add_statement("Second statement")

    assert len(note.statements) == 2
    assert note.statements[0].content == "First statement"
    assert note.statements[1].content == "Second statement"

    # Test empty statement
    with pytest.raises(ValueError, match="Statement content cannot be empty"):
        note.add_statement("")

    # Test whitespace statement
    with pytest.raises(ValueError, match="Statement content cannot be empty"):
        note.add_statement("   ")

    # Remove statement
    note.remove_statement(note.statements[0])
    assert len(note.statements) == 1
    assert note.statements[0].content == "Second statement"


def test_note_tag_management():
    """Test adding and managing tags.

    Tag management rules:
    1. Can add tags
    2. Tags must start with #
    3. Tags are stored in lowercase
    4. Duplicate tags are ignored
    5. Can remove tags
    """
    note = Note(contact_id=TEST_UUID, content="Test note")

    # Add valid tags
    note.add_tag("#test")
    note.add_tag("#project")

    assert len(note.tags) == 2
    assert "#test" in [t.name for t in note.tags]
    assert "#project" in [t.name for t in note.tags]

    # Test invalid tag format
    with pytest.raises(ValueError, match="Tag must start with #"):
        note.add_tag("invalid")

    # Test duplicate tag
    note.add_tag("#test")  # Should be ignored
    assert len(note.tags) == 2

    # Test case normalization
    note.add_tag("#TEST")  # Should be normalized to #test
    assert len(note.tags) == 2

    # Remove tag
    test_tag = next(t for t in note.tags if t.name == "#test")
    note.remove_tag(test_tag)
    assert len(note.tags) == 1
    assert "#test" not in [t.name for t in note.tags]


def test_note_update_tracking():
    """Test that updates are tracked properly.

    Update tracking rules:
    1. created_at is set on creation
    2. updated_at changes when content changes
    3. updated_at changes when statements change
    4. updated_at changes when tags change
    """
    note = Note(contact_id=TEST_UUID, content="Original content")
    original_updated_at = note.updated_at

    # Wait a moment to ensure timestamp difference
    import time
    time.sleep(0.001)

    # Test content update
    note.update_content("New content")
    assert note.updated_at > original_updated_at

    # Test statement update
    original_updated_at = note.updated_at
    time.sleep(0.001)
    note.add_statement("New statement")
    assert note.updated_at > original_updated_at

    # Test tag update
    original_updated_at = note.updated_at
    time.sleep(0.001)
    note.add_tag("#newtag")
    assert note.updated_at > original_updated_at

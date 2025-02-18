"""Tests for the Note domain model.

Tests are organized by complexity and frequency of use:
1. Basic Tests - Creation and validation
2. Relationship Tests - Statement and tag management
3. State Management Tests - Update tracking and interactions
4. Temporal Tests - Timezone handling
"""

import pytest
from datetime import datetime, UTC, timedelta, timezone
from zoneinfo import ZoneInfo
from uuid import UUID
from backend.app.models.domain.note_model import Note

TEST_UUID = UUID("11111111-1111-1111-1111-111111111111")


# region Basic Tests (Common)

def test_note_creation():
    """Test creating a note with required fields.

    A note must have:
    1. A contact_id identifying which contact it belongs to
    2. Content (the actual note text)
    """
    note = Note(contact_id=TEST_UUID, content="Test note content")

    assert note.contact_id == TEST_UUID
    assert note.content == "Test note content"
    assert note.statements == []
    assert note.tags == []
    assert isinstance(note.created_at, datetime)
    assert isinstance(note.updated_at, datetime)


def test_note_content_validation():
    """Test note content validation.

    Content validation rules:
    1. Content notes require content
    2. Content cannot be just whitespace
    3. Content is trimmed
    """
    # Test empty content
    with pytest.raises(ValueError, match="Content notes require content"):
        Note(contact_id=TEST_UUID, content="")

    # Test whitespace content
    with pytest.raises(ValueError, match="Content notes require content"):
        Note(contact_id=TEST_UUID, content="   ")

    # Test content trimming
    note = Note(contact_id=TEST_UUID, content="  Test content  ")
    assert note.content == "Test content"


def test_note_interaction_defaults():
    """Test default values for notes.

    Default rules:
    1. is_interaction defaults to False
    2. interaction_date defaults to None
    3. Content notes work as before
    """
    # Test regular content note
    note = Note(contact_id=TEST_UUID, content="Test note")
    assert not note.is_interaction
    assert note.interaction_date is None
    assert note.content == "Test note"

# endregion


# region Relationship Tests (Common)

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

# endregion


# region State Management Tests (Moderate)

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


def test_note_interaction_creation():
    """Test creating an interaction note.

    Interaction notes:
    1. Must have interaction_date
    2. Content is optional
    3. Update contact's last_contact_at
    """
    # Test valid interaction note with content
    interaction_time = datetime.now(UTC)
    note = Note(
        contact_id=TEST_UUID,
        content="Met for coffee",
        is_interaction=True,
        interaction_date=interaction_time
    )
    assert note.is_interaction
    assert note.interaction_date == interaction_time
    assert note.content == "Met for coffee"

    # Test valid interaction note without content
    note_no_content = Note(
        contact_id=TEST_UUID,
        is_interaction=True,
        interaction_date=interaction_time
    )
    assert note_no_content.is_interaction
    assert note_no_content.interaction_date == interaction_time
    assert note_no_content.content is None


def test_note_interaction_validation():
    """Test interaction note validation rules.

    Validation rules:
    1. If is_interaction=True, must have interaction_date
    2. If is_interaction=False, must have content
    3. If is_interaction=False, cannot have interaction_date
    4. interaction_date cannot be in the future
    """
    # Test missing interaction_date
    with pytest.raises(ValueError, match="Interaction notes require a date"):
        Note(
            contact_id=TEST_UUID,
            is_interaction=True
        )

    # Test content note without content
    with pytest.raises(ValueError, match="Content notes require content"):
        Note(
            contact_id=TEST_UUID,
            is_interaction=False
        )

    # Test content note with interaction_date
    with pytest.raises(ValueError, match="Content notes cannot have interaction date"):
        Note(
            contact_id=TEST_UUID,
            content="Test",
            is_interaction=False,
            interaction_date=datetime.now(UTC)
        )

    # Test future interaction_date
    future_time = datetime.now(UTC) + timedelta(days=1)
    with pytest.raises(ValueError, match="Interaction date cannot be in the future"):
        Note(
            contact_id=TEST_UUID,
            is_interaction=True,
            interaction_date=future_time
        )

# endregion


# region Temporal Tests (Complex)

def test_note_timezone_handling():
    """Test timezone handling in notes.

    Timezone rules:
    1. Interaction dates must be timezone-aware
    2. Different input timezones are converted to UTC
    3. Timezone information is preserved
    4. Naive datetimes are rejected
    """
    # Test with UTC time
    utc_time = datetime.now(UTC)
    note = Note(
        contact_id=TEST_UUID,
        is_interaction=True,
        interaction_date=utc_time
    )
    assert note.interaction_date is not None
    assert note.interaction_date == utc_time
    assert note.interaction_date.tzinfo == UTC

    # Test with different timezone (Tokyo)
    tokyo_time = datetime.now(ZoneInfo("Asia/Tokyo"))
    note = Note(
        contact_id=TEST_UUID,
        is_interaction=True,
        interaction_date=tokyo_time
    )
    assert note.interaction_date is not None
    assert (
        note.interaction_date ==
        tokyo_time.astimezone(UTC)
    )
    assert note.interaction_date.tzinfo == UTC

    # Test with custom timezone offset
    custom_tz = timezone(
        timedelta(hours=5, minutes=30)  # UTC+5:30
    )
    custom_time = datetime.now(custom_tz)
    note = Note(
        contact_id=TEST_UUID,
        is_interaction=True,
        interaction_date=custom_time
    )
    assert note.interaction_date is not None
    assert (
        note.interaction_date ==
        custom_time.astimezone(UTC)
    )
    assert note.interaction_date.tzinfo == UTC

    # Test rejection of naive datetime
    naive_time = datetime.now()
    with pytest.raises(
        ValueError,
        match="Interaction date must be timezone-aware"
    ):
        Note(
            contact_id=TEST_UUID,
            is_interaction=True,
            interaction_date=naive_time
        )


def test_note_timezone_edge_cases():
    """Test timezone edge cases.

    Edge cases:
    1. DST transitions
    2. Day boundaries
    3. Timezone conversions
    4. Extreme offsets
    """
    # Test DST transition
    ny_tz = ZoneInfo("America/New_York")
    winter_time = datetime(
        2024, 1, 1, 12, 0, tzinfo=ny_tz  # During EST
    )
    summer_time = datetime(
        2024, 7, 1, 12, 0, tzinfo=ny_tz  # During EDT
    )

    # Winter note (EST)
    winter_note = Note(
        contact_id=TEST_UUID,
        is_interaction=True,
        interaction_date=winter_time
    )
    assert (
        winter_note.interaction_date ==
        winter_time.astimezone(UTC)
    )

    # Summer note (EDT)
    summer_note = Note(
        contact_id=TEST_UUID,
        is_interaction=True,
        interaction_date=summer_time
    )
    assert (
        summer_note.interaction_date ==
        summer_time.astimezone(UTC)
    )

    # Test day boundary
    tokyo_tz = ZoneInfo("Asia/Tokyo")
    ny_time = datetime(2024, 1, 1, 0, 0, tzinfo=ny_tz)
    tokyo_time = ny_time.astimezone(tokyo_tz)

    ny_note = Note(
        contact_id=TEST_UUID,
        is_interaction=True,
        interaction_date=ny_time
    )
    tokyo_note = Note(
        contact_id=TEST_UUID,
        is_interaction=True,
        interaction_date=tokyo_time
    )

    assert ny_note.interaction_date == tokyo_note.interaction_date

# endregion

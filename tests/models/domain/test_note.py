"""Tests for the Note domain model."""

import pytest
from datetime import datetime, UTC, timedelta
from zoneinfo import ZoneInfo
from uuid import UUID
from backend.app.models.domain.note_model import Note

TEST_UUID = UUID("11111111-1111-1111-1111-111111111111")


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


def test_note_timezone_handling():
    """Test timezone handling in notes.

    Timezone rules:
    1. Interaction dates must be timezone-aware
    2. Different input timezones are converted to UTC
    3. Timezone information is preserved
    4. Future date validation works across timezones
    """
    # Test timezone-naive date rejection
    naive_date = datetime.now()
    with pytest.raises(ValueError, match="Interaction date must be timezone-aware"):
        Note(
            contact_id=TEST_UUID,
            is_interaction=True,
            interaction_date=naive_date
        )

    # Test different input timezones
    sydney_tz = ZoneInfo("Australia/Sydney")
    ny_tz = ZoneInfo("America/New_York")

    # Create a reference time in Sydney
    sydney_time = datetime.now(sydney_tz).replace(microsecond=0)
    expected_utc = sydney_time.astimezone(UTC)

    note_sydney = Note(
        contact_id=TEST_UUID,
        content="Meeting in Sydney",
        is_interaction=True,
        interaction_date=sydney_time
    )

    # Verify conversion to UTC
    assert note_sydney.interaction_date is not None
    assert note_sydney.interaction_date == expected_utc
    assert note_sydney.interaction_date.tzinfo == UTC

    # Test future date validation across timezones
    future_ny_time = datetime.now(ny_tz) + timedelta(days=1)
    with pytest.raises(ValueError, match="Interaction date cannot be in the future"):
        Note(
            contact_id=TEST_UUID,
            is_interaction=True,
            interaction_date=future_ny_time
        )


def test_note_timezone_edge_cases():
    """Test edge cases in timezone handling.

    Edge cases:
    1. Dates near UTC day boundary
    2. Dates in different DST periods
    3. Dates with fractional hours offset
    """
    # Test date near UTC day boundary
    india_tz = ZoneInfo("Asia/Kolkata")  # UTC+5:30
    # Create a time that's the next day in India but same day in UTC
    india_time = datetime.now(india_tz).replace(hour=1, minute=0, second=0, microsecond=0)

    note_india = Note(
        contact_id=TEST_UUID,
        content="Early morning meeting in India",
        is_interaction=True,
        interaction_date=india_time
    )

    # Verify correct UTC conversion
    assert note_india.interaction_date is not None
    assert note_india.interaction_date.tzinfo == UTC
    assert note_india.interaction_date < india_time

    # Test DST transition handling
    paris_tz = ZoneInfo("Europe/Paris")
    # Create a time during DST
    paris_dst_time = datetime(2024, 7, 1, 14, 0, tzinfo=paris_tz)

    note_paris = Note(
        contact_id=TEST_UUID,
        content="Summer meeting in Paris",
        is_interaction=True,
        interaction_date=paris_dst_time
    )

    # Verify DST handling
    assert note_paris.interaction_date is not None
    assert note_paris.interaction_date.tzinfo == UTC
    assert note_paris.interaction_date.hour == 12  # UTC+2 during DST


def test_note_interaction_timezone_consistency():
    """Test timezone consistency in interaction notes.

    Consistency rules:
    1. All datetime fields use UTC internally
    2. Timezone information is preserved in conversions
    3. Comparison operations work correctly
    """
    tokyo_tz = ZoneInfo("Asia/Tokyo")
    la_tz = ZoneInfo("America/Los_Angeles")

    # Create two notes with different timezone inputs
    tokyo_time = datetime.now(tokyo_tz).replace(microsecond=0)
    la_time = tokyo_time.astimezone(la_tz)

    note_tokyo = Note(
        contact_id=TEST_UUID,
        content="Tokyo meeting",
        is_interaction=True,
        interaction_date=tokyo_time
    )

    note_la = Note(
        contact_id=TEST_UUID,
        content="LA meeting",
        is_interaction=True,
        interaction_date=la_time
    )

    # Verify both notes have same UTC time
    assert note_tokyo.interaction_date is not None
    assert note_la.interaction_date is not None
    assert note_tokyo.interaction_date == note_la.interaction_date
    assert note_tokyo.interaction_date.tzinfo == UTC
    assert note_la.interaction_date.tzinfo == UTC

    # Verify original timezone info can be recovered
    assert note_tokyo.interaction_date.astimezone(tokyo_tz).hour == tokyo_time.hour
    assert note_la.interaction_date.astimezone(la_tz).hour == la_time.hour

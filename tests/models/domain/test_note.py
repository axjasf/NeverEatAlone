"""Tests for the Note domain model."""

import pytest
from datetime import datetime, timezone, timedelta
from uuid import UUID
from backend.app.models.domain.note_model import Note
from backend.app.models.domain.contact_model import Contact


TEST_UUID = UUID("11111111-1111-1111-1111-111111111111")


# 1. Basic CRUD Operations
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


# 2. Statement Management
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


# 3. Tag Management
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


def test_batch_tag_updates():
    """Test updating multiple tags at once.

    Batch update rules:
    1. Can set multiple tags at once
    2. All tags are validated
    3. Timestamps update correctly
    4. Previous tags are removed
    """
    note = Note(contact_id=TEST_UUID, content="Test note")

    # Add initial tags
    note.add_tag("#test")
    note.add_tag("#project")
    assert len(note.tags) == 2

    # Batch update tags
    new_tags = ["#new1", "#new2", "#new3"]
    note.set_tags(new_tags)

    # Verify new tags
    assert len(note.tags) == 3
    assert all(t.name in new_tags for t in note.tags)
    assert all(t.name.islower() for t in note.tags)

    # Test invalid tags in batch
    with pytest.raises(ValueError, match="Tag must start with #"):
        note.set_tags(["#valid", "invalid", "#alsovalid"])


# 4. Type Validation
def test_note_requires_either_content_or_interaction():
    """Test that a note must have either content or be an interaction record.

    Rules:
    1. Cannot create empty note (no content and not interaction)
    2. Content notes must have content
    3. Interaction notes don't require content
    """
    # Test empty note (should fail)
    with pytest.raises(ValueError, match="Note must have either content or be an interaction record"):
        Note(contact_id=TEST_UUID, is_interaction=False)

    # Test content note without content (should fail)
    with pytest.raises(ValueError, match="Content cannot be empty for content notes"):
        Note(contact_id=TEST_UUID, is_interaction=False)

    # Test interaction note without content (should pass)
    interaction_date = datetime.now(timezone.utc)
    note = Note(contact_id=TEST_UUID, is_interaction=True, interaction_date=interaction_date)
    assert note.is_interaction
    assert not note.content
    assert note.interaction_date == interaction_date

    # Test content note with content (should pass)
    note = Note(contact_id=TEST_UUID, content="Test content")
    assert not note.is_interaction
    assert note.content == "Test content"
    assert not note.interaction_date


def test_content_note_cannot_have_interaction_date():
    """Test that content notes cannot have interaction dates.

    Rules:
    1. Content notes cannot have interaction_date set
    2. Interaction flag and date must be consistent
    """
    # Test content note with interaction date
    with pytest.raises(ValueError, match="Content notes cannot have interaction date"):
        Note(
            contact_id=TEST_UUID,
            content="Test content",
            interaction_date=datetime.now(timezone.utc)
        )

    # Test content note with is_interaction but no date
    with pytest.raises(ValueError, match="Interaction notes must have an interaction date"):
        Note(
            contact_id=TEST_UUID,
            content="Test content",
            is_interaction=True
        )


# 5. Interaction Date Validation
def test_interaction_note_requires_date():
    """Test that interaction notes must have a valid interaction date.

    Rules:
    1. Interaction notes must have interaction_date
    2. Interaction date must be timezone-aware
    3. Interaction date cannot be in the future
    """
    # Test interaction note without date
    with pytest.raises(ValueError, match="Interaction notes must have an interaction date"):
        Note(contact_id=TEST_UUID, is_interaction=True)

    # Test with naive datetime
    naive_date = datetime.now()
    with pytest.raises(ValueError, match="Interaction date must be timezone-aware"):
        Note(contact_id=TEST_UUID, is_interaction=True, interaction_date=naive_date)

    # Test with future date
    future_date = datetime.now(timezone.utc) + timedelta(days=1)
    with pytest.raises(ValueError, match="Interaction date cannot be in the future"):
        Note(contact_id=TEST_UUID, is_interaction=True, interaction_date=future_date)

    # Test valid interaction note
    now = datetime.now(timezone.utc)
    note = Note(contact_id=TEST_UUID, is_interaction=True, interaction_date=now)
    assert note.interaction_date == now


def test_interaction_date_timezone_validation():
    """Test that interaction dates must be timezone-aware.

    Rules:
    1. Creation with naive datetime fails
    2. Updating to naive datetime fails
    3. Different timezones are preserved
    """
    # Test creation with naive datetime
    naive_date = datetime.now()
    with pytest.raises(ValueError, match="Interaction date must be timezone-aware"):
        Note(contact_id=TEST_UUID, is_interaction=True, interaction_date=naive_date)

    # Test updating to naive datetime
    note = Note(
        contact_id=TEST_UUID,
        is_interaction=True,
        interaction_date=datetime.now(timezone.utc)
    )
    with pytest.raises(ValueError, match="Interaction date must be timezone-aware"):
        note.interaction_date = naive_date

    # Test different timezones
    pst = timezone(timedelta(hours=-8))
    pst_time = datetime.now(pst)
    note.interaction_date = pst_time
    assert note.interaction_date.tzinfo == pst


def test_interaction_date_future_validation():
    """Test that interaction dates cannot be in the future.

    Rules:
    1. Creation with future date fails
    2. Updating to future date fails
    3. Dates up to current time are allowed
    """
    now = datetime.now(timezone.utc)
    future = now + timedelta(seconds=1)
    past = now - timedelta(days=1)

    # Test creation with future date
    with pytest.raises(ValueError, match="Interaction date cannot be in the future"):
        Note(contact_id=TEST_UUID, is_interaction=True, interaction_date=future)

    # Test updating to future date
    note = Note(contact_id=TEST_UUID, is_interaction=True, interaction_date=past)
    with pytest.raises(ValueError, match="Interaction date cannot be in the future"):
        note.interaction_date = future

    # Test valid dates
    note.interaction_date = now  # Current time should work
    note.interaction_date = past  # Past should work


def test_interaction_date_changes():
    """Test changing interaction date after creation.

    Rules:
    1. Can update to valid past dates
    2. Updates trigger timestamp updates
    3. Updates trigger tag timestamp updates
    4. Cannot update to invalid dates
    """
    now = datetime.now(timezone.utc)
    past1 = now - timedelta(days=1)
    past2 = now - timedelta(days=2)

    note = Note(contact_id=TEST_UUID, is_interaction=True, interaction_date=past1)
    note.add_tag("#test")

    # Update to valid date
    note.interaction_date = past2
    assert note.interaction_date == past2
    assert note.tags[0].last_contact == past2

    # Verify timestamp update
    assert note.updated_at > now

    # Test invalid updates
    with pytest.raises(ValueError):
        note.interaction_date = datetime.now()  # naive datetime
    with pytest.raises(ValueError):
        note.interaction_date = now + timedelta(days=1)  # future


def test_note_validation_edge_cases():
    """Test edge cases in note validation.

    Cases:
    1. Mixing content and interaction flags
    2. Updating content on interaction notes
    3. Converting between note types
    """
    # Test creating note with both content and interaction
    interaction_date = datetime.now(timezone.utc)
    note = Note(
        contact_id=TEST_UUID,
        content="Test content",
        is_interaction=True,
        interaction_date=interaction_date
    )
    assert note.is_interaction
    assert note.content == "Test content"
    assert note.interaction_date == interaction_date

    # Test updating content on interaction note
    note.update_content("New content")
    assert note.content == "New content"
    assert note.is_interaction  # Should still be an interaction note

    # Cannot convert interaction note to content note if it has no content
    interaction_note = Note(
        contact_id=TEST_UUID,
        is_interaction=True,
        interaction_date=datetime.now(timezone.utc)
    )
    with pytest.raises(ValueError, match="Cannot convert to content note without content"):
        interaction_note.is_interaction = False


def test_interaction_note_updates_contact_timestamp():
    """Test that interaction notes update contact's last_contact_at.

    Rules:
    1. Creating interaction note updates contact timestamp
    2. Timestamp is set to interaction_date
    3. Only interaction notes trigger updates
    """
    # Setup
    contact = Contact(name="Test Contact")
    assert not contact.last_contact_at  # Initially no contact

    # Create interaction note
    interaction_date = datetime.now(timezone.utc)
    note = Note(
        contact_id=contact.id,
        is_interaction=True,
        interaction_date=interaction_date
    )
    note.update_contact(contact)  # This will be our new method

    # Verify contact timestamp updated
    assert contact.last_contact_at == interaction_date

    # Content note should not update timestamp
    original_timestamp = contact.last_contact_at
    content_note = Note(
        contact_id=contact.id,
        content="Test content"
    )
    content_note.update_contact(contact)
    assert contact.last_contact_at == original_timestamp  # Unchanged


def test_interaction_note_updates_tag_timestamps():
    """Test that interaction notes update tag last_contact timestamps.

    Rules:
    1. Tags on interaction notes get their last_contact updated
    2. Timestamp is set to interaction_date
    3. Only interaction notes trigger updates
    4. Updates happen when adding tags to interaction notes
    """
    from backend.app.models.domain.tag_model import Tag, EntityType

    # Setup
    interaction_date = datetime.now(timezone.utc)
    note = Note(
        contact_id=TEST_UUID,
        is_interaction=True,
        interaction_date=interaction_date
    )

    # Add tag to interaction note
    note.add_tag("#test")
    tag = note.tags[0]
    assert tag.last_contact == interaction_date

    # Content note should not update tag timestamp
    content_note = Note(
        contact_id=TEST_UUID,
        content="Test content"
    )
    content_note.add_tag("#test")
    tag = content_note.tags[0]
    assert not tag.last_contact  # Should not be set


def test_note_tag_update_triggers():
    """Test when tag updates are triggered.

    Cases:
    1. Adding tag to existing interaction note
    2. Converting note to interaction note with existing tags
    3. Updating interaction_date with existing tags
    """
    # Setup
    note = Note(
        contact_id=TEST_UUID,
        content="Test content"
    )
    note.add_tag("#test")
    original_tag = note.tags[0]
    assert not original_tag.last_contact  # No contact yet

    # Convert to interaction note
    interaction_date = datetime.now(timezone.utc)
    note.is_interaction = True
    note.interaction_date = interaction_date
    assert original_tag.last_contact == interaction_date

    # Update interaction date
    new_date = interaction_date - timedelta(days=1)  # Earlier date
    note.interaction_date = new_date
    assert original_tag.last_contact == new_date

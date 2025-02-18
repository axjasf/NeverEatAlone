"""Tests for the Note ORM model.

Tests are organized by complexity and frequency of use:
1. Basic Tests - Creation and validation
2. Data Structure Tests - Statement and tag management
3. State Management Tests - Update tracking and interactions
4. Temporal Tests - Timezone handling
"""

import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, UTC
from zoneinfo import ZoneInfo
from backend.app.models.orm.contact_orm import ContactORM
from backend.app.models.orm.note_orm import NoteORM
from backend.app.models.orm.statement_orm import StatementORM


# region Basic Tests (Common)

def test_note_creation_with_required_fields(db_session: Session) -> None:
    """Test creating a note with only required fields."""
    # Create a contact first
    contact = ContactORM(name="John Doe")
    db_session.add(contact)
    db_session.commit()

    # Create note
    note = NoteORM(
        contact_id=contact.id,
        content="Had a great meeting today."
    )
    db_session.add(note)
    db_session.commit()
    db_session.refresh(note)

    # Verify note
    saved_note = db_session.get(NoteORM, note.id)
    assert saved_note is not None
    assert saved_note.content == "Had a great meeting today."
    assert saved_note.contact_id == contact.id
    assert saved_note.created_at is not None
    assert saved_note.statements == []  # No statements yet
    assert saved_note.tags == []  # No tags yet


def test_note_requires_contact(db_session: Session) -> None:
    """Test that notes must be associated with a contact."""
    note = NoteORM(content="Test note")
    db_session.add(note)
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_note_requires_content(db_session: Session) -> None:
    """Test that notes must have content."""
    contact = ContactORM(name="John Doe")
    db_session.add(contact)
    db_session.commit()

    note = NoteORM(contact_id=contact.id)  # type: ignore
    db_session.add(note)
    with pytest.raises(IntegrityError):
        db_session.commit()

# endregion


# region Data Structure Tests (Common)

def test_note_statement_creation(db_session: Session) -> None:
    """Test creating statements from a note."""
    # Create contact and note
    contact = ContactORM(name="John Doe")
    db_session.add(contact)
    db_session.commit()

    note = NoteORM(
        contact_id=contact.id,
        content=(
            "Had a great meeting today. "
            "Discussed project timeline. "
            "Need to follow up next week."
        )
    )
    db_session.add(note)
    db_session.commit()

    # Create statements
    statements = [
        StatementORM(
            note_id=note.id,
            content="Had a great meeting today.",
            sequence_number=1
        ),
        StatementORM(
            note_id=note.id,
            content="Discussed project timeline.",
            sequence_number=2
        ),
        StatementORM(
            note_id=note.id,
            content="Need to follow up next week.",
            sequence_number=3
        ),
    ]
    for stmt in statements:
        db_session.add(stmt)
    db_session.commit()
    db_session.refresh(note)

    # Verify statements
    assert len(note.statements) == 3
    assert [s.content for s in note.statements] == [
        "Had a great meeting today.",
        "Discussed project timeline.",
        "Need to follow up next week.",
    ]


def test_note_statement_deletion(db_session: Session) -> None:
    """Test that deleting a note also deletes its statements."""
    # Create contact and note with statements
    contact = ContactORM(name="John Doe")
    db_session.add(contact)
    db_session.commit()

    note = NoteORM(
        contact_id=contact.id,
        content="Statement 1. Statement 2."
    )
    db_session.add(note)
    db_session.commit()

    statements = [
        StatementORM(
            note_id=note.id,
            content="Statement 1.",
            sequence_number=1
        ),
        StatementORM(
            note_id=note.id,
            content="Statement 2.",
            sequence_number=2
        ),
    ]
    for stmt in statements:
        db_session.add(stmt)
    db_session.commit()

    # Delete note
    db_session.delete(note)
    db_session.commit()

    # Verify statements are deleted
    remaining_statements = (
        db_session.query(StatementORM)
        .filter_by(note_id=note.id)
        .all()
    )
    assert len(remaining_statements) == 0


def test_note_tagging(db_session: Session) -> None:
    """Test adding tags to a note."""
    # Create contact and note
    contact = ContactORM(name="John Doe")
    db_session.add(contact)
    db_session.commit()

    note = NoteORM(
        contact_id=contact.id,
        content="Meeting about #project timeline."
    )
    db_session.add(note)
    db_session.commit()

    # Add tags to note
    note.set_tags(["#meeting", "#project"])
    db_session.commit()
    db_session.refresh(note)

    # Verify tags
    assert len(note.tags) == 2
    assert sorted(t.name for t in note.tags) == ["#meeting", "#project"]


def test_statement_tagging(db_session: Session) -> None:
    """Test adding tags to individual statements."""
    # Create contact and note with statement
    contact = ContactORM(name="John Doe")
    db_session.add(contact)
    db_session.commit()

    note = NoteORM(
        contact_id=contact.id,
        content="Meeting about project timeline."
    )
    db_session.add(note)
    db_session.commit()

    statement = StatementORM(
        note_id=note.id,
        content="Meeting about project timeline.",
        sequence_number=1
    )
    db_session.add(statement)
    db_session.commit()

    # Add tags to statement
    statement.set_tags(["#meeting", "#project"])
    db_session.commit()
    db_session.refresh(statement)

    # Verify tags
    assert len(statement.tags) == 2
    assert sorted(t.name for t in statement.tags) == ["#meeting", "#project"]

# endregion


# region Temporal Tests (Complex)

def test_note_timezone_handling(db_session: Session) -> None:
    """Test timezone handling in notes.

    Verify:
    1. Timezone-aware interaction dates are stored correctly
    2. Dates are stored in UTC
    3. Different input timezones are handled
    4. Timezone information is preserved
    """
    # Create a contact
    contact = ContactORM(name="John Doe")
    db_session.add(contact)
    db_session.commit()

    # Test with different input timezones
    sydney_tz = ZoneInfo("Australia/Sydney")
    ny_tz = ZoneInfo("America/New_York")

    # Create a reference time in Sydney
    sydney_time = datetime.now(sydney_tz).replace(microsecond=0)
    expected_utc = sydney_time.astimezone(UTC)

    # Create note with Sydney timezone
    note_sydney = NoteORM(
        contact_id=contact.id,
        content="Meeting in Sydney",
        is_interaction=True,
        interaction_date=sydney_time
    )
    db_session.add(note_sydney)
    db_session.commit()
    db_session.refresh(note_sydney)

    # Verify UTC storage
    assert note_sydney.interaction_date is not None
    assert note_sydney.interaction_date.tzinfo == UTC
    assert note_sydney.interaction_date == expected_utc

    # Create same moment in NY timezone
    ny_time = sydney_time.astimezone(ny_tz)
    note_ny = NoteORM(
        contact_id=contact.id,
        content="Same meeting from NY perspective",
        is_interaction=True,
        interaction_date=ny_time
    )
    db_session.add(note_ny)
    db_session.commit()
    db_session.refresh(note_ny)

    # Verify both notes represent the same moment
    assert note_ny.interaction_date is not None
    assert note_ny.interaction_date == note_sydney.interaction_date


def test_note_timezone_edge_cases(db_session: Session) -> None:
    """Test timezone edge cases in notes.

    Verify:
    1. Dates near UTC day boundary
    2. Dates in different DST periods
    3. Dates with fractional hours offset
    """
    # Create a contact
    contact = ContactORM(name="John Doe")
    db_session.add(contact)
    db_session.commit()

    # Test date near UTC day boundary with fractional offset
    india_tz = ZoneInfo("Asia/Kolkata")  # UTC+5:30
    india_time = datetime.now(india_tz).replace(
        hour=1,
        minute=0,
        second=0,
        microsecond=0
    )

    note_india = NoteORM(
        contact_id=contact.id,
        content="Early morning meeting in India",
        is_interaction=True,
        interaction_date=india_time
    )
    db_session.add(note_india)
    db_session.commit()
    db_session.refresh(note_india)

    # Verify UTC conversion
    assert note_india.interaction_date is not None
    assert note_india.interaction_date.tzinfo == UTC
    assert note_india.interaction_date == india_time.astimezone(UTC)

    # Test DST transition handling
    paris_tz = ZoneInfo("Europe/Paris")
    # Create a time during DST
    paris_dst_time = datetime(
        2024, 7, 1, 14, 0,
        tzinfo=paris_tz
    )

    note_paris = NoteORM(
        contact_id=contact.id,
        content="Summer meeting in Paris",
        is_interaction=True,
        interaction_date=paris_dst_time
    )
    db_session.add(note_paris)
    db_session.commit()
    db_session.refresh(note_paris)

    # Verify DST handling
    assert note_paris.interaction_date is not None
    assert note_paris.interaction_date.tzinfo == UTC
    assert note_paris.interaction_date == paris_dst_time.astimezone(UTC)


def test_note_created_at_timezone(db_session: Session) -> None:
    """Test timezone handling for created_at field.

    Verify:
    1. created_at is always in UTC
    2. created_at is automatically set
    3. created_at reflects server time
    """
    # Create a contact
    contact = ContactORM(name="John Doe")
    db_session.add(contact)
    db_session.commit()

    # Record time before and after note creation
    before = datetime.now(UTC)
    note = NoteORM(contact_id=contact.id, content="Test note")
    db_session.add(note)
    db_session.commit()
    db_session.refresh(note)
    after = datetime.now(UTC)

    # Verify created_at
    assert note.created_at is not None
    assert note.created_at.tzinfo == UTC
    assert before <= note.created_at <= after

# endregion

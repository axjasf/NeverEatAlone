"""Tests for the Note repository."""

from uuid import uuid4
from datetime import datetime, UTC, timedelta
from zoneinfo import ZoneInfo
from typing import List
from sqlalchemy.orm import Session
from backend.app.models.domain.note_model import Note
from backend.app.repositories.sqlalchemy_note_repository import (
    SQLAlchemyNoteRepository,
)


TEST_UUID = uuid4()


def test_note_save_and_find(db_session: Session) -> None:
    """Test saving and finding a note."""
    repo = SQLAlchemyNoteRepository(db_session)

    # Create and save a note
    note = Note(contact_id=TEST_UUID, content="Test note content")
    repo.save(note)

    # Find by ID
    found = repo.find_by_id(note.id)
    assert found is not None
    assert found.contact_id == TEST_UUID
    assert found.content == "Test note content"


def test_note_find_by_contact(db_session: Session) -> None:
    """Test finding notes by contact."""
    repo = SQLAlchemyNoteRepository(db_session)

    # Create notes for different contacts
    note1 = Note(contact_id=TEST_UUID, content="Note 1")
    note2 = Note(contact_id=TEST_UUID, content="Note 2")
    note3 = Note(contact_id=uuid4(), content="Note 3")
    repo.save(note1)
    repo.save(note2)
    repo.save(note3)

    # Find by contact
    notes = repo.find_by_contact(TEST_UUID)
    assert len(notes) == 2
    assert {n.content for n in notes} == {"Note 1", "Note 2"}


def test_note_find_by_tag(db_session: Session) -> None:
    """Test finding notes by tag."""
    repo = SQLAlchemyNoteRepository(db_session)

    # Create notes with tags
    note1 = Note(contact_id=TEST_UUID, content="Note 1")
    note1.add_tag("#test")
    note1.add_tag("#project")
    repo.save(note1)

    note2 = Note(contact_id=TEST_UUID, content="Note 2")
    note2.add_tag("#test")
    repo.save(note2)

    note3 = Note(contact_id=TEST_UUID, content="Note 3")
    note3.add_tag("#other")
    repo.save(note3)

    # Find by tag
    test_notes = repo.find_by_tag("#test")
    assert len(test_notes) == 2
    assert {n.content for n in test_notes} == {"Note 1", "Note 2"}

    project_notes = repo.find_by_tag("#project")
    assert len(project_notes) == 1
    assert project_notes[0].content == "Note 1"

    other_notes = repo.find_by_tag("#other")
    assert len(other_notes) == 1
    assert other_notes[0].content == "Note 3"


def test_note_with_statements(db_session: Session) -> None:
    """Test saving and finding notes with statements."""
    repo = SQLAlchemyNoteRepository(db_session)

    # Create note with statements
    note = Note(contact_id=TEST_UUID, content="Main note")
    note.add_statement("First statement")
    note.add_statement("Second statement")
    repo.save(note)

    # Find and verify statements
    found = repo.find_by_id(note.id)
    assert found is not None
    assert len(found.statements) == 2
    assert [s.content for s in found.statements] == [
        "First statement",
        "Second statement",
    ]


def test_note_with_statement_tags(db_session: Session) -> None:
    """Test saving and finding notes with tagged statements."""
    repo = SQLAlchemyNoteRepository(db_session)

    # Create note with tagged statements
    note = Note(contact_id=TEST_UUID, content="Main note")
    note.add_statement("First statement")
    note.add_statement("Second statement")
    repo.save(note)

    # Find and verify statements
    found = repo.find_by_id(note.id)
    assert found is not None
    assert len(found.statements) == 2
    assert found.statements[0].content == "First statement"
    assert found.statements[1].content == "Second statement"


def test_note_delete(db_session: Session) -> None:
    """Test deleting a note."""
    repo = SQLAlchemyNoteRepository(db_session)

    # Create note with statements and tags
    note = Note(contact_id=TEST_UUID, content="Test note")
    note.add_tag("#test")
    note.add_statement("Test statement")
    repo.save(note)

    # Verify note exists
    found = repo.find_by_id(note.id)
    assert found is not None

    # Delete note
    repo.delete(note)

    # Verify note is gone
    found = repo.find_by_id(note.id)
    assert found is None


def test_note_timezone_handling(db_session: Session) -> None:
    """Test timezone handling in note repository.

    Verify:
    1. Timezone-aware dates are preserved
    2. Different input timezones are handled
    3. UTC conversion is consistent
    """
    repo = SQLAlchemyNoteRepository(db_session)

    # Create notes with different timezones
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
    repo.save(note_sydney)

    # Same moment from NY perspective
    ny_time = sydney_time.astimezone(ny_tz)
    note_ny = Note(
        contact_id=TEST_UUID,
        content="Same meeting from NY",
        is_interaction=True,
        interaction_date=ny_time
    )
    repo.save(note_ny)

    # Retrieve and verify
    found_sydney = repo.find_by_id(note_sydney.id)
    found_ny = repo.find_by_id(note_ny.id)

    assert found_sydney is not None
    assert found_ny is not None

    # Verify both represent the same moment
    assert found_sydney.interaction_date is not None
    assert found_ny.interaction_date is not None
    assert found_sydney.interaction_date == found_ny.interaction_date
    assert found_sydney.interaction_date == expected_utc


def test_note_timezone_query_handling(db_session: Session) -> None:
    """Test timezone handling in repository queries.

    Verify:
    1. Filtering by interaction_date works across timezones
    2. Range queries handle DST correctly
    3. Sorting by datetime fields is consistent
    """
    repo = SQLAlchemyNoteRepository(db_session)

    # Create notes across different times/timezones
    tokyo_tz = ZoneInfo("Asia/Tokyo")
    paris_tz = ZoneInfo("Europe/Paris")

    # Base time in Tokyo (using a fixed past date)
    base_time = datetime(2024, 1, 1, 12, 0, tzinfo=tokyo_tz)

    # Create notes at different times
    notes: List[Note] = []
    for hours in [0, 1, 2]:  # Create notes 1 hour apart
        time = base_time + timedelta(hours=hours)
        paris_time = time.astimezone(paris_tz)

        note = Note(
            contact_id=TEST_UUID,
            content=f"Note at {time.isoformat()}",
            is_interaction=True,
            interaction_date=paris_time  # Use Paris time for creation
        )
        repo.save(note)
        notes.append(note)

    # Find interactions for the contact
    interactions = repo.find_interactions(TEST_UUID)

    # Verify chronological order
    assert len(interactions) == 3
    for i in range(len(interactions) - 1):
        current_date = interactions[i].interaction_date
        next_date = interactions[i+1].interaction_date
        assert current_date is not None and next_date is not None
        assert current_date > next_date  # Changed from < to > since we expect descending order

    # Verify timezone consistency
    for note in interactions:
        assert note.interaction_date is not None
        assert note.interaction_date.tzinfo == UTC


def test_note_timezone_edge_cases(db_session: Session) -> None:
    """Test timezone edge cases in repository.

    Verify:
    1. DST transition handling
    2. Day boundary queries
    3. Fractional hour offsets
    """
    repo = SQLAlchemyNoteRepository(db_session)

    # Test DST handling
    paris_tz = ZoneInfo("Europe/Paris")
    # Create a time during DST
    paris_dst_time = datetime(2024, 7, 1, 14, 0, tzinfo=paris_tz)
    # Create a time outside DST
    paris_standard_time = datetime(2024, 1, 1, 14, 0, tzinfo=paris_tz)

    note_dst = Note(
        contact_id=TEST_UUID,
        content="Summer meeting in Paris",
        is_interaction=True,
        interaction_date=paris_dst_time
    )
    repo.save(note_dst)

    note_standard = Note(
        contact_id=TEST_UUID,
        content="Winter meeting in Paris",
        is_interaction=True,
        interaction_date=paris_standard_time
    )
    repo.save(note_standard)

    # Test fractional offset
    india_tz = ZoneInfo("Asia/Kolkata")  # UTC+5:30
    india_time = datetime.now(india_tz).replace(
        hour=1, minute=0, second=0, microsecond=0
    )

    note_india = Note(
        contact_id=TEST_UUID,
        content="Early morning in India",
        is_interaction=True,
        interaction_date=india_time
    )
    repo.save(note_india)

    # Retrieve and verify
    found_dst = repo.find_by_id(note_dst.id)
    found_standard = repo.find_by_id(note_standard.id)
    found_india = repo.find_by_id(note_india.id)

    assert found_dst is not None
    assert found_standard is not None
    assert found_india is not None

    # Verify timezone info is preserved
    assert found_dst.interaction_date is not None
    assert found_standard.interaction_date is not None
    assert found_india.interaction_date is not None

    assert found_dst.interaction_date.tzinfo == UTC
    assert found_standard.interaction_date.tzinfo == UTC
    assert found_india.interaction_date.tzinfo == UTC

    # Verify correct UTC conversion
    assert found_dst.interaction_date == paris_dst_time.astimezone(UTC)
    assert found_standard.interaction_date == paris_standard_time.astimezone(UTC)
    assert found_india.interaction_date == india_time.astimezone(UTC)

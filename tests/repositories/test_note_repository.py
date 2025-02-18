"""Tests for the Note repository.

Tests are organized by complexity and frequency of use:
1. Basic Tests - CRUD operations
2. Query Tests - Search and filtering
3. State Management Tests - Updates and tracking
4. Temporal Tests - Timezone handling
"""

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


# region Basic Tests (Common)

def test_note_save_and_find(db_session: Session) -> None:
    """Test basic CRUD operations.

    Rules:
    1. Note creation
    2. Persistence
    3. Retrieval
    4. Field verification
    """
    repo = SQLAlchemyNoteRepository(db_session)

    # Create and save a note
    note = Note(contact_id=TEST_UUID, content="Test note content")
    repo.save(note)

    # Find by ID
    found = repo.find_by_id(note.id)
    assert found is not None
    assert found.contact_id == TEST_UUID
    assert found.content == "Test note content"


def test_note_update(db_session: Session) -> None:
    """Test entity updates.

    Rules:
    1. Content updates
    2. Statement updates
    3. Tag updates
    4. Timestamp tracking
    """
    repo = SQLAlchemyNoteRepository(db_session)

    # Create initial note
    note = Note(contact_id=TEST_UUID, content="Initial content")
    note.add_statement("Initial statement")
    note.add_tag("#initial")
    repo.save(note)
    initial_updated_at = note.updated_at

    # Update note
    note.update_content("Updated content")
    note.add_statement("New statement")
    note.add_tag("#updated")
    repo.save(note)

    # Verify updates
    found = repo.find_by_id(note.id)
    assert found is not None
    assert found.content == "Updated content"
    assert len(found.statements) == 2
    assert found.statements[1].content == "New statement"
    assert "#updated" in [t.name for t in found.tags]
    assert found.updated_at > initial_updated_at

# endregion


# region Query Tests (Common)

def test_note_find_by_contact(db_session: Session) -> None:
    """Test contact-based queries.

    Rules:
    1. Single contact queries
    2. Multiple matches
    3. No match cases
    4. Result completeness
    """
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
    """Test tag-based queries.

    Rules:
    1. Single tag queries
    2. Multiple matches
    3. No match cases
    4. Result order
    """
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
    """Test statement relationship queries.

    Rules:
    1. Statement creation
    2. Order preservation
    3. Relationship loading
    4. Content verification
    """
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
    """Test nested relationship queries.

    Rules:
    1. Statement tag creation
    2. Tag persistence
    3. Relationship loading
    4. Content verification
    """
    repo = SQLAlchemyNoteRepository(db_session)

    # Create note with tagged statements
    note = Note(contact_id=TEST_UUID, content="Main note")
    statement1 = note.add_statement("First statement")
    statement1.add_tag("#test")
    statement2 = note.add_statement("Second statement")
    statement2.add_tag("#project")
    repo.save(note)

    # Find and verify statements with tags
    found = repo.find_by_id(note.id)
    assert found is not None
    assert len(found.statements) == 2
    assert found.statements[0].content == "First statement"
    assert found.statements[1].content == "Second statement"
    assert found.statements[0].tags[0].name == "#test"
    assert found.statements[1].tags[0].name == "#project"

# endregion


# region State Management Tests (Moderate)

def test_note_delete(db_session: Session) -> None:
    """Test entity deletion.

    Rules:
    1. Note deletion
    2. Cascade behavior
    3. Statement cleanup
    4. Tag cleanup
    """
    repo = SQLAlchemyNoteRepository(db_session)

    # Create note with statements and tags
    note = Note(contact_id=TEST_UUID, content="Test note")
    note.add_tag("#test")
    statement = note.add_statement("Test statement")
    statement.add_tag("#statement_tag")
    repo.save(note)

    # Verify note exists
    found = repo.find_by_id(note.id)
    assert found is not None

    # Delete note
    repo.delete(note)

    # Verify note and related entities are gone
    found = repo.find_by_id(note.id)
    assert found is None

# endregion


# region Temporal Tests (Complex)

def test_note_timezone_handling(db_session: Session) -> None:
    """Test timezone handling.

    Rules:
    1. Timezone info preservation
    2. UTC conversion
    3. Cross-timezone operations
    4. State consistency
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
    """Test timezone-aware queries.

    Rules:
    1. Timezone criteria
    2. UTC conversion
    3. Cross-timezone matching
    4. Time thresholds
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
        assert current_date > next_date  # Descending order


def test_note_timezone_edge_cases(db_session: Session) -> None:
    """Test timezone edge cases.

    Rules:
    1. DST transitions
    2. Day boundaries
    3. Fractional offsets
    4. Extreme timezones
    """
    repo = SQLAlchemyNoteRepository(db_session)

    # Test DST transition
    paris_tz = ZoneInfo("Europe/Paris")
    # Create a time during DST
    paris_dst_time = datetime(2024, 7, 1, 14, 0, tzinfo=paris_tz)

    note_paris = Note(
        contact_id=TEST_UUID,
        content="Summer meeting in Paris",
        is_interaction=True,
        interaction_date=paris_dst_time
    )
    repo.save(note_paris)

    # Create a time during non-DST
    paris_non_dst_time = datetime(2024, 1, 1, 14, 0, tzinfo=paris_tz)

    note_paris_winter = Note(
        contact_id=TEST_UUID,
        content="Winter meeting in Paris",
        is_interaction=True,
        interaction_date=paris_non_dst_time
    )
    repo.save(note_paris_winter)

    # Test fractional offset
    india_tz = ZoneInfo("Asia/Kolkata")  # UTC+5:30
    india_time = datetime(2024, 1, 1, 1, 0, tzinfo=india_tz)

    note_india = Note(
        contact_id=TEST_UUID,
        content="Early morning meeting in India",
        is_interaction=True,
        interaction_date=india_time
    )
    repo.save(note_india)

    # Retrieve and verify
    found_paris = repo.find_by_id(note_paris.id)
    found_paris_winter = repo.find_by_id(note_paris_winter.id)
    found_india = repo.find_by_id(note_india.id)

    assert found_paris is not None
    assert found_paris_winter is not None
    assert found_india is not None

    # Verify timezone conversion
    assert found_paris.interaction_date == paris_dst_time.astimezone(UTC)
    assert (
        found_paris_winter.interaction_date ==
        paris_non_dst_time.astimezone(UTC)
    )
    assert found_india.interaction_date == india_time.astimezone(UTC)

    # Verify chronological order
    interactions = repo.find_interactions(TEST_UUID)
    dates = [n.interaction_date for n in interactions if n.interaction_date]
    assert all(
        dates[i] > dates[i+1]
        for i in range(len(dates)-1)
    )  # Descending order

# endregion

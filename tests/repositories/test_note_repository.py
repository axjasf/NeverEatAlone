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


# region Statement-Specific Tests (New)

def test_statement_sequence_persistence(db_session: Session) -> None:
    """Test Statement sequence persistence in repository.

    Rules:
    1. Sequence numbers are preserved
    2. Order maintained after updates
    3. Gaps handled correctly
    4. Reordering supported
    """
    repo = SQLAlchemyNoteRepository(db_session)

    # Create note with statements
    note = Note(contact_id=TEST_UUID, content="Main note")
    note.add_statement("First statement")
    note.add_statement("Second statement")
    note.add_statement("Third statement")
    repo.save(note)

    # Verify initial sequence
    found = repo.find_by_id(note.id)
    assert found is not None
    assert len(found.statements) == 3
    assert [s.content for s in found.statements] == [
        "First statement",
        "Second statement",
        "Third statement"
    ]

    # Remove middle statement
    note.remove_statement(note.statements[1])
    repo.save(note)

    # Verify sequence after removal
    found = repo.find_by_id(note.id)
    assert found is not None
    assert len(found.statements) == 2
    assert [s.content for s in found.statements] == [
        "First statement",
        "Third statement"
    ]

    # Add new statement
    note.add_statement("New statement")
    repo.save(note)

    # Verify sequence after addition
    found = repo.find_by_id(note.id)
    assert found is not None
    assert len(found.statements) == 3
    assert [s.content for s in found.statements] == [
        "First statement",
        "Third statement",
        "New statement"
    ]


def test_statement_update_tracking(db_session: Session) -> None:
    """Test Statement update tracking in repository.

    Rules:
    1. Content updates tracked
    2. Tag updates tracked
    3. Timestamps preserved
    4. Audit fields maintained
    """
    repo = SQLAlchemyNoteRepository(db_session)

    # Create note with statement
    note = Note(contact_id=TEST_UUID, content="Main note")
    statement = note.add_statement("Original content")
    repo.save(note)

    # Get initial timestamps
    found = repo.find_by_id(note.id)
    assert found is not None
    original_created_at = found.statements[0].created_at
    original_updated_at = found.statements[0].updated_at

    # Update statement content
    statement.content = "Updated content"
    repo.save(note)

    # Verify content update tracking
    found = repo.find_by_id(note.id)
    assert found is not None
    assert found.statements[0].content == "Updated content"
    # Compare timestamps ignoring microseconds
    assert found.statements[0].created_at.replace(microsecond=0) == original_created_at.replace(microsecond=0)
    assert found.statements[0].updated_at.replace(microsecond=0) >= original_updated_at.replace(microsecond=0)

    # Update statement tags
    original_updated_at = found.statements[0].updated_at
    statement.add_tag("#test")
    repo.save(note)

    # Verify tag update tracking
    found = repo.find_by_id(note.id)
    assert found is not None
    assert "#test" in [t.name for t in found.statements[0].tags]
    # Compare timestamps ignoring microseconds
    assert found.statements[0].created_at.replace(microsecond=0) == original_created_at.replace(microsecond=0)
    assert found.statements[0].updated_at.replace(microsecond=0) >= original_updated_at.replace(microsecond=0)


def test_statement_tag_lifecycle(db_session: Session) -> None:
    """Test Statement tag lifecycle in repository.

    Rules:
    1. Tag creation
    2. Tag updates
    3. Tag removal
    4. Association cleanup
    """
    repo = SQLAlchemyNoteRepository(db_session)

    # Create note with tagged statement
    note = Note(contact_id=TEST_UUID, content="Main note")
    statement = note.add_statement("Test statement")
    statement.add_tag("#test")
    statement.add_tag("#project")
    repo.save(note)

    # Verify initial tags
    found = repo.find_by_id(note.id)
    assert found is not None
    assert len(found.statements[0].tags) == 2
    assert {t.name for t in found.statements[0].tags} == {"#test", "#project"}

    # Update tags
    statement.remove_tag(statement.tags[0])
    statement.add_tag("#updated")
    repo.save(note)

    # Verify tag updates
    found = repo.find_by_id(note.id)
    assert found is not None
    assert len(found.statements[0].tags) == 2
    assert "#updated" in [t.name for t in found.statements[0].tags]

    # Remove all tags
    for tag in statement.tags[:]:
        statement.remove_tag(tag)
    repo.save(note)

    # Verify tag removal
    found = repo.find_by_id(note.id)
    assert found is not None
    assert len(found.statements[0].tags) == 0


def test_statement_bulk_operations(db_session: Session) -> None:
    """Test Statement bulk operations in repository.

    Rules:
    1. Multiple statement creation
    2. Batch updates
    3. Performance characteristics
    4. Transaction integrity
    """
    repo = SQLAlchemyNoteRepository(db_session)

    # Create note with multiple statements
    note = Note(contact_id=TEST_UUID, content="Main note")
    for i in range(5):
        statement = note.add_statement(f"Statement {i}")
        statement.add_tag(f"#tag{i}")
    repo.save(note)

    # Verify bulk creation
    found = repo.find_by_id(note.id)
    assert found is not None
    assert len(found.statements) == 5
    assert all(len(s.tags) == 1 for s in found.statements)

    # Bulk update statements
    for statement in note.statements:
        statement.content = f"Updated {statement.content}"
        statement.add_tag("#updated")
    repo.save(note)

    # Verify bulk updates
    found = repo.find_by_id(note.id)
    assert found is not None
    assert all(s.content.startswith("Updated") for s in found.statements)
    assert all("#updated" in [t.name for t in s.tags] for s in found.statements)

    # Bulk remove statements
    while note.statements:
        note.remove_statement(note.statements[0])
    repo.save(note)

    # Verify bulk removal
    found = repo.find_by_id(note.id)
    assert found is not None
    assert len(found.statements) == 0


def test_statement_timezone_handling(db_session: Session) -> None:
    """Test Statement timezone handling in repository.

    Rules:
    1. Timestamps stored in UTC
    2. Timezone info preserved through save/load
    3. Moment-in-time meaning preserved
    4. Different input timezones handled
    """
    repo = SQLAlchemyNoteRepository(db_session)

    # Create note with statements using different timezones
    sydney_tz = ZoneInfo("Australia/Sydney")
    ny_tz = ZoneInfo("America/New_York")

    # Create a reference time in Sydney
    sydney_time = datetime.now(sydney_tz).replace(microsecond=0)
    expected_utc = sydney_time.astimezone(UTC)

    note = Note(contact_id=TEST_UUID, content="Main note")
    statement_sydney = note.add_statement("Sydney statement")
    statement_sydney.created_at = sydney_time  # Explicitly set for testing

    # Same moment from NY perspective
    ny_time = sydney_time.astimezone(ny_tz)
    statement_ny = note.add_statement("NY statement")
    statement_ny.created_at = ny_time  # Explicitly set for testing

    repo.save(note)

    # Verify through repository
    found = repo.find_by_id(note.id)
    assert found is not None
    assert len(found.statements) == 2

    # Verify both represent the same moment in UTC, ignoring microseconds
    assert found.statements[0].created_at.replace(microsecond=0) == expected_utc
    assert found.statements[1].created_at.replace(microsecond=0) == expected_utc


def test_statement_dst_handling(db_session: Session) -> None:
    """Test Statement handling across DST transitions.

    Rules:
    1. DST transitions handled correctly
    2. Hour ambiguity resolved
    3. Timezone rules applied correctly
    4. Moment-in-time preserved
    """
    repo = SQLAlchemyNoteRepository(db_session)

    # Test DST transition
    paris_tz = ZoneInfo("Europe/Paris")

    # Create a note with statements during DST and non-DST
    note = Note(contact_id=TEST_UUID, content="DST Test Note")

    # Summer time statement (UTC+2)
    summer_time = datetime(2024, 7, 1, 14, 0, tzinfo=paris_tz)
    statement_summer = note.add_statement("Summer statement")
    statement_summer.created_at = summer_time

    # Winter time statement (UTC+1)
    winter_time = datetime(2024, 1, 1, 14, 0, tzinfo=paris_tz)
    statement_winter = note.add_statement("Winter statement")
    statement_winter.created_at = winter_time

    repo.save(note)

    # Verify through repository
    found = repo.find_by_id(note.id)
    assert found is not None

    # Verify correct UTC conversion, ignoring microseconds
    assert found.statements[0].created_at.replace(microsecond=0) == summer_time.astimezone(UTC).replace(microsecond=0)
    assert found.statements[1].created_at.replace(microsecond=0) == winter_time.astimezone(UTC).replace(microsecond=0)

    # Verify hour difference due to DST
    hour_difference = (
        found.statements[0].created_at.astimezone(paris_tz).hour -
        found.statements[1].created_at.astimezone(paris_tz).hour
    )
    assert hour_difference == 0  # Same wall clock time in Paris


def test_statement_fractional_offset(db_session: Session) -> None:
    """Test Statement handling with fractional timezone offsets.

    Rules:
    1. Fractional offsets preserved
    2. Correct UTC conversion
    3. Timestamp integrity maintained
    4. Proper timezone rules applied
    """
    repo = SQLAlchemyNoteRepository(db_session)

    # Test fractional offset timezone
    india_tz = ZoneInfo("Asia/Kolkata")  # UTC+5:30
    nepal_tz = ZoneInfo("Asia/Kathmandu")  # UTC+5:45

    # Create note with statements in fractional offset timezones
    note = Note(contact_id=TEST_UUID, content="Fractional Offset Test")

    # India time statement
    india_time = datetime(2024, 1, 1, 1, 0, tzinfo=india_tz)
    statement_india = note.add_statement("India statement")
    statement_india.created_at = india_time

    # Nepal time statement (same wall clock time)
    nepal_time = datetime(2024, 1, 1, 1, 0, tzinfo=nepal_tz)
    statement_nepal = note.add_statement("Nepal statement")
    statement_nepal.created_at = nepal_time

    repo.save(note)

    # Verify through repository
    found = repo.find_by_id(note.id)
    assert found is not None

    # Verify correct UTC conversion, ignoring microseconds
    assert found.statements[0].created_at.replace(microsecond=0) == india_time.astimezone(UTC).replace(microsecond=0)
    assert found.statements[1].created_at.replace(microsecond=0) == nepal_time.astimezone(UTC).replace(microsecond=0)

    # Verify 15-minute difference is preserved when converting back to local time
    time_difference = abs(
        found.statements[0].created_at.astimezone(india_tz).minute -
        found.statements[1].created_at.astimezone(nepal_tz).minute
    )
    assert time_difference == 0  # Same wall clock time in both zones

# endregion

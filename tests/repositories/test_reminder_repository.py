"""Integration tests for reminder repository."""

import pytest
from datetime import datetime, timezone, timedelta
from uuid import UUID
from sqlalchemy.orm import Session

from backend.app.models.domain.reminder import (
    Reminder,
    ReminderStatus,
    RecurrencePattern,
    RecurrenceUnit
)
from backend.app.models.orm.contact import ContactORM
from backend.app.models.orm.note import NoteORM
from backend.app.models.repositories.sqlalchemy_reminder_repository import (
    SQLAlchemyReminderRepository
)

# Test data
TEST_UUID = UUID("11111111-1111-1111-1111-111111111111")
TEST_DATETIME = datetime(2024, 1, 1, tzinfo=timezone.utc)

# Fixtures
@pytest.fixture
def reminder_repository(db_session: Session) -> SQLAlchemyReminderRepository:
    """Create a reminder repository for testing."""
    return SQLAlchemyReminderRepository(db_session)

@pytest.fixture
def contact(db_session: Session) -> ContactORM:
    """Create a test contact."""
    contact = ContactORM(name="Test Contact")
    db_session.add(contact)
    db_session.commit()
    return contact

@pytest.fixture
def note(db_session: Session, contact: ContactORM) -> NoteORM:
    """Create a test note."""
    note = NoteORM(contact_id=contact.id, content="Test note")
    db_session.add(note)
    db_session.commit()
    return note

# Basic CRUD Operations
def test_save_and_find_by_id(
    reminder_repository: SQLAlchemyReminderRepository,
    contact: ContactORM,
    db_session: Session
) -> None:
    """Test basic save and find operations.

    Should:
    - Save new reminder
    - Find it by ID
    - Return None for non-existent ID
    """
    # Create and save
    reminder = Reminder(
        contact_id=contact.id,
        title="Test reminder",
        due_date=TEST_DATETIME
    )
    saved = reminder_repository.save(reminder)
    db_session.commit()

    # Find by ID
    found = reminder_repository.find_by_id(saved.id)
    assert found is not None
    assert found.title == "Test reminder"
    assert found.due_date == TEST_DATETIME

    # Find non-existent
    not_found = reminder_repository.find_by_id(TEST_UUID)
    assert not_found is None


def test_update_existing_reminder(
    reminder_repository: SQLAlchemyReminderRepository,
    contact: ContactORM,
    db_session: Session
) -> None:
    """Test updating an existing reminder.

    Should:
    - Update all fields
    - Preserve unchanged fields
    - Return updated reminder
    """
    # Create initial reminder
    reminder = Reminder(
        contact_id=contact.id,
        title="Original title",
        description="Original description",
        due_date=TEST_DATETIME
    )
    saved = reminder_repository.save(reminder)
    db_session.commit()

    # Update fields
    updated = Reminder(
        contact_id=contact.id,
        title="Updated title",
        description="Updated description",
        due_date=TEST_DATETIME + timedelta(days=1)
    )
    updated.id = saved.id
    result = reminder_repository.save(updated)
    db_session.commit()

    # Verify updates
    found = reminder_repository.find_by_id(saved.id)
    assert found is not None
    assert found.title == "Updated title"
    assert found.description == "Updated description"
    assert found.due_date == TEST_DATETIME + timedelta(days=1)


def test_delete_reminder(
    reminder_repository: SQLAlchemyReminderRepository,
    contact: ContactORM,
    db_session: Session
) -> None:
    """Test deleting a reminder.

    Should:
    - Delete existing reminder
    - Handle non-existent reminder
    - Not affect other reminders
    """
    # Create reminders
    reminder1 = Reminder(
        contact_id=contact.id,
        title="Reminder 1",
        due_date=TEST_DATETIME
    )
    reminder2 = Reminder(
        contact_id=contact.id,
        title="Reminder 2",
        due_date=TEST_DATETIME
    )
    saved1 = reminder_repository.save(reminder1)
    saved2 = reminder_repository.save(reminder2)
    db_session.commit()

    # Delete one reminder
    reminder_repository.delete(saved1)
    db_session.commit()

    # Verify deletion
    assert reminder_repository.find_by_id(saved1.id) is None
    assert reminder_repository.find_by_id(saved2.id) is not None

    # Delete non-existent (should not raise)
    reminder_repository.delete(saved1)
    db_session.commit()


# Query Operations
def test_find_by_contact(
    reminder_repository: SQLAlchemyReminderRepository,
    contact: ContactORM,
    db_session: Session
) -> None:
    """Test finding reminders by contact.

    Should:
    - Find all reminders for contact
    - Return empty list for contact without reminders
    - Not return reminders for other contacts
    """
    # Create another contact
    other_contact = ContactORM(name="Other Contact")
    db_session.add(other_contact)
    db_session.commit()

    # Create reminders for both contacts
    reminder1 = Reminder(
        contact_id=contact.id,
        title="Contact 1 Reminder",
        due_date=TEST_DATETIME
    )
    reminder2 = Reminder(
        contact_id=other_contact.id,
        title="Contact 2 Reminder",
        due_date=TEST_DATETIME
    )
    reminder_repository.save(reminder1)
    reminder_repository.save(reminder2)
    db_session.commit()

    # Find reminders for first contact
    found = reminder_repository.find_by_contact(contact.id)
    assert len(found) == 1
    assert found[0].title == "Contact 1 Reminder"

    # Find reminders for contact without any
    empty = reminder_repository.find_by_contact(TEST_UUID)
    assert len(empty) == 0


def test_find_by_note(
    reminder_repository: SQLAlchemyReminderRepository,
    contact: ContactORM,
    note: NoteORM,
    db_session: Session
) -> None:
    """Test finding reminders by note.

    Should:
    - Find all reminders for note
    - Return empty list for note without reminders
    - Not return unlinked reminders
    """
    # Create reminders
    linked = Reminder(
        contact_id=contact.id,
        title="Linked Reminder",
        due_date=TEST_DATETIME,
        note_id=note.id
    )
    unlinked = Reminder(
        contact_id=contact.id,
        title="Unlinked Reminder",
        due_date=TEST_DATETIME
    )
    reminder_repository.save(linked)
    reminder_repository.save(unlinked)
    db_session.commit()

    # Find reminders for note
    found = reminder_repository.find_by_note(note.id)
    assert len(found) == 1
    assert found[0].title == "Linked Reminder"

    # Find reminders for non-existent note
    empty = reminder_repository.find_by_note(TEST_UUID)
    assert len(empty) == 0


def test_find_pending(
    reminder_repository: SQLAlchemyReminderRepository,
    contact: ContactORM,
    db_session: Session
) -> None:
    """Test finding pending reminders.

    Should:
    - Find all pending reminders
    - Not return completed reminders
    - Not return cancelled reminders
    """
    # Create reminders in different states
    pending = Reminder(
        contact_id=contact.id,
        title="Pending Reminder",
        due_date=TEST_DATETIME
    )
    completed = Reminder(
        contact_id=contact.id,
        title="Completed Reminder",
        due_date=TEST_DATETIME
    )
    completed.complete(TEST_DATETIME + timedelta(hours=1))
    cancelled = Reminder(
        contact_id=contact.id,
        title="Cancelled Reminder",
        due_date=TEST_DATETIME
    )
    cancelled.cancel()

    reminder_repository.save(pending)
    reminder_repository.save(completed)
    reminder_repository.save(cancelled)
    db_session.commit()

    # Find pending reminders
    found = reminder_repository.find_pending()
    assert len(found) == 1
    assert found[0].title == "Pending Reminder"
    assert found[0].status == ReminderStatus.PENDING


def test_find_overdue(
    reminder_repository: SQLAlchemyReminderRepository,
    contact: ContactORM,
    db_session: Session
) -> None:
    """Test finding overdue reminders.

    Should:
    - Find pending reminders past due date
    - Not return future reminders
    - Not return completed/cancelled reminders
    """
    now = datetime.now(timezone.utc)
    past = now - timedelta(days=1)
    future = now + timedelta(days=1)

    # Create reminders
    overdue = Reminder(
        contact_id=contact.id,
        title="Overdue Reminder",
        due_date=past
    )
    future_reminder = Reminder(
        contact_id=contact.id,
        title="Future Reminder",
        due_date=future
    )
    completed = Reminder(
        contact_id=contact.id,
        title="Completed Reminder",
        due_date=past
    )
    completed.complete(now)

    reminder_repository.save(overdue)
    reminder_repository.save(future_reminder)
    reminder_repository.save(completed)
    db_session.commit()

    # Find overdue reminders
    found = reminder_repository.find_overdue()
    assert len(found) == 1
    assert found[0].title == "Overdue Reminder"
    assert found[0].due_date < now


# Complex Operations
def test_save_recurring_reminder(
    reminder_repository: SQLAlchemyReminderRepository,
    contact: ContactORM,
    db_session: Session
) -> None:
    """Test saving recurring reminders.

    Should:
    - Save reminder with recurrence pattern
    - Preserve pattern on retrieval
    - Handle pattern updates
    """
    # Create recurring reminder
    pattern = RecurrencePattern(
        interval=1,
        unit=RecurrenceUnit.WEEK.value,
        end_date=TEST_DATETIME + timedelta(days=30)
    )
    reminder = Reminder(
        contact_id=contact.id,
        title="Weekly Reminder",
        due_date=TEST_DATETIME,
        recurrence_pattern=pattern
    )
    saved = reminder_repository.save(reminder)
    db_session.commit()

    # Verify pattern persistence
    found = reminder_repository.find_by_id(saved.id)
    assert found is not None
    assert found.recurrence_pattern is not None
    assert found.recurrence_pattern.interval == 1
    assert found.recurrence_pattern.unit == RecurrenceUnit.WEEK.value
    assert found.recurrence_pattern.end_date == TEST_DATETIME + timedelta(days=30)

    # Update pattern
    new_pattern = RecurrencePattern(
        interval=2,
        unit=RecurrenceUnit.WEEK.value
    )
    found.recurrence_pattern = new_pattern
    updated = reminder_repository.save(found)
    db_session.commit()

    # Verify pattern update
    reloaded = reminder_repository.find_by_id(updated.id)
    assert reloaded is not None
    assert reloaded.recurrence_pattern is not None
    assert reloaded.recurrence_pattern.interval == 2
    assert reloaded.recurrence_pattern.end_date is None


def test_complete_recurring_reminder(
    reminder_repository: SQLAlchemyReminderRepository,
    contact: ContactORM,
    db_session: Session
) -> None:
    """Test completing recurring reminders.

    Should:
    - Complete current reminder
    - Create and save next occurrence
    - Handle last occurrence completion
    """
    # Create recurring reminder
    pattern = RecurrencePattern(
        interval=1,
        unit=RecurrenceUnit.WEEK.value,
        end_date=TEST_DATETIME + timedelta(days=10)
    )
    reminder = Reminder(
        contact_id=contact.id,
        title="Weekly Reminder",
        due_date=TEST_DATETIME,
        recurrence_pattern=pattern
    )
    saved = reminder_repository.save(reminder)
    db_session.commit()

    # Complete reminder
    completion_date = TEST_DATETIME + timedelta(hours=1)
    next_reminder = saved.complete(completion_date)
    reminder_repository.save(saved)
    if next_reminder:
        reminder_repository.save(next_reminder)
    db_session.commit()

    # Verify completion and next occurrence
    completed = reminder_repository.find_by_id(saved.id)
    assert completed is not None
    assert completed.status == ReminderStatus.COMPLETED
    assert completed.completion_date == completion_date

    # Find all reminders for contact
    all_reminders = reminder_repository.find_by_contact(contact.id)
    assert len(all_reminders) == 2
    next_found = next(r for r in all_reminders if r.status == ReminderStatus.PENDING)
    assert next_found.due_date == TEST_DATETIME + timedelta(weeks=1)
    assert next_found.recurrence_pattern == pattern

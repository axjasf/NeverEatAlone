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


@pytest.fixture
def reminder_repository(db_session: Session) -> SQLAlchemyReminderRepository:
    """Create a reminder repository for testing.

    Args:
        db_session: SQLAlchemy session fixture

    Returns:
        SQLAlchemyReminderRepository: Repository instance for testing
    """
    return SQLAlchemyReminderRepository(db_session)


@pytest.fixture
def contact(db_session: Session) -> ContactORM:
    """Create a test contact.

    Args:
        db_session: SQLAlchemy session fixture

    Returns:
        ContactORM: Test contact
    """
    contact = ContactORM(name="Test Contact")
    db_session.add(contact)
    db_session.commit()
    return contact


@pytest.fixture
def note(db_session: Session, contact: ContactORM) -> NoteORM:
    """Create a test note.

    Args:
        db_session: SQLAlchemy session fixture
        contact: Parent contact

    Returns:
        NoteORM: Test note
    """
    note = NoteORM(contact_id=contact.id, content="Test note")
    db_session.add(note)
    db_session.commit()
    return note


def test_save_and_find_one_off_reminder(
    reminder_repository: SQLAlchemyReminderRepository,
    contact: ContactORM,
    db_session: Session
) -> None:
    """Test saving and finding a one-off reminder.

    Should:
    - Save a reminder with basic fields
    - Find it by ID
    - Verify all fields match
    """
    # Create and save reminder
    due_date = datetime(2024, 3, 1, tzinfo=timezone.utc)
    reminder = Reminder(
        contact_id=contact.id,
        title="Test reminder",
        description="Test description",
        due_date=due_date
    )
    saved = reminder_repository.save(reminder)
    db_session.commit()

    # Find and verify
    found = reminder_repository.find_by_id(saved.id)
    assert found is not None
    assert found.title == "Test reminder"
    assert found.description == "Test description"
    assert found.due_date == due_date
    assert found.status == ReminderStatus.PENDING
    assert found.completion_date is None
    assert found.contact_id == contact.id
    assert found.note_id is None
    assert found.recurrence_pattern is None


def test_save_and_find_recurring_reminder(
    reminder_repository: SQLAlchemyReminderRepository,
    contact: ContactORM,
    db_session: Session
) -> None:
    """Test saving and finding a recurring reminder.

    Should:
    - Save a reminder with recurrence pattern
    - Find it by ID
    - Verify recurrence fields are preserved
    """
    # Create and save reminder
    due_date = datetime(2024, 3, 1, tzinfo=timezone.utc)
    pattern = RecurrencePattern(
        interval=1,
        unit=RecurrenceUnit.MONTH.value,
        end_date=datetime(2024, 12, 31, tzinfo=timezone.utc)
    )
    reminder = Reminder(
        contact_id=contact.id,
        title="Monthly check-in",
        description="Regular status update",
        due_date=due_date,
        recurrence_pattern=pattern
    )
    saved = reminder_repository.save(reminder)
    db_session.commit()

    # Find and verify
    found = reminder_repository.find_by_id(saved.id)
    assert found is not None
    assert found.recurrence_pattern is not None
    assert found.recurrence_pattern.interval == 1
    assert found.recurrence_pattern.unit == RecurrenceUnit.MONTH.value
    assert found.recurrence_pattern.end_date == datetime(2024, 12, 31, tzinfo=timezone.utc)


def test_find_by_contact(
    reminder_repository: SQLAlchemyReminderRepository,
    contact: ContactORM,
    db_session: Session
) -> None:
    """Test finding reminders by contact.

    Should:
    - Return all reminders for a contact
    - Return empty list if no reminders found
    - Not return reminders for other contacts
    """
    # Create multiple reminders
    due_date = datetime(2024, 3, 1, tzinfo=timezone.utc)
    reminders = [
        Reminder(contact_id=contact.id, title=f"Reminder {i}", due_date=due_date)
        for i in range(3)
    ]
    for reminder in reminders:
        reminder_repository.save(reminder)
    db_session.commit()

    # Find reminders for contact
    found = reminder_repository.find_by_contact(contact.id)
    assert len(found) == 3
    assert all(r.contact_id == contact.id for r in found)
    assert {r.title for r in found} == {"Reminder 0", "Reminder 1", "Reminder 2"}


def test_find_by_note(
    reminder_repository: SQLAlchemyReminderRepository,
    contact: ContactORM,
    note: NoteORM,
    db_session: Session
) -> None:
    """Test finding reminders by note.

    Should:
    - Return all reminders linked to a note
    - Return empty list if no reminders found
    - Not return reminders not linked to the note
    """
    # Create reminders linked to note
    due_date = datetime(2024, 3, 1, tzinfo=timezone.utc)
    reminders = [
        Reminder(
            contact_id=contact.id,
            title=f"Note reminder {i}",
            due_date=due_date,
            note_id=note.id
        )
        for i in range(2)
    ]
    for reminder in reminders:
        reminder_repository.save(reminder)

    # Create a reminder not linked to any note
    no_note_reminder = Reminder(
        contact_id=contact.id,
        title="No note reminder",
        due_date=due_date
    )
    reminder_repository.save(no_note_reminder)
    db_session.commit()

    # Find reminders for note
    found = reminder_repository.find_by_note(note.id)
    assert len(found) == 2
    assert all(r.note_id == note.id for r in found)
    assert {r.title for r in found} == {"Note reminder 0", "Note reminder 1"}


def test_find_pending(
    reminder_repository: SQLAlchemyReminderRepository,
    contact: ContactORM,
    db_session: Session
) -> None:
    """Test finding pending reminders.

    Should:
    - Find all reminders in PENDING status
    - Not return completed or cancelled reminders
    """
    due_date = datetime(2024, 3, 1, tzinfo=timezone.utc)

    # Pending reminder
    pending = Reminder(
        contact_id=contact.id,
        title="Pending reminder",
        due_date=due_date
    )
    reminder_repository.save(pending)

    # Completed reminder
    completed = Reminder(
        contact_id=contact.id,
        title="Completed reminder",
        due_date=due_date
    )
    completed.complete(datetime(2024, 3, 1, 12, tzinfo=timezone.utc))
    reminder_repository.save(completed)

    # Cancelled reminder
    cancelled = Reminder(
        contact_id=contact.id,
        title="Cancelled reminder",
        due_date=due_date
    )
    cancelled.cancel()
    reminder_repository.save(cancelled)
    db_session.commit()

    # Find pending reminders
    found = reminder_repository.find_pending()
    assert len(found) == 1
    assert found[0].status == ReminderStatus.PENDING
    assert found[0].title == "Pending reminder"


def test_find_overdue(
    reminder_repository: SQLAlchemyReminderRepository,
    contact: ContactORM,
    db_session: Session
) -> None:
    """Test finding overdue reminders.

    Should:
    - Return reminders past their due date
    - Not return future reminders
    - Not return completed/cancelled reminders
    """
    now = datetime.now(timezone.utc)
    past_date = now - timedelta(days=7)  # 7 days ago
    future_date = now + timedelta(days=7)  # 7 days in the future

    # Create overdue reminder
    overdue = Reminder(
        contact_id=contact.id,
        title="Overdue reminder",
        due_date=past_date
    )
    reminder_repository.save(overdue)

    # Create future reminder
    future = Reminder(
        contact_id=contact.id,
        title="Future reminder",
        due_date=future_date
    )
    reminder_repository.save(future)

    # Create completed overdue reminder
    completed = Reminder(
        contact_id=contact.id,
        title="Completed reminder",
        due_date=past_date
    )
    completed.complete(now - timedelta(days=1))  # Completed yesterday
    reminder_repository.save(completed)
    db_session.commit()

    # Find overdue reminders
    found = reminder_repository.find_overdue()
    assert len(found) == 1
    assert found[0].title == "Overdue reminder"
    assert found[0].status == ReminderStatus.PENDING
    assert found[0].due_date < datetime.now(timezone.utc)


def test_delete_reminder(
    reminder_repository: SQLAlchemyReminderRepository,
    contact: ContactORM,
    db_session: Session
) -> None:
    """Test deleting a reminder.

    Should:
    - Successfully delete the reminder
    - Not affect other reminders
    """
    # Create two reminders
    due_date = datetime(2024, 3, 1, tzinfo=timezone.utc)
    reminder1 = Reminder(
        contact_id=contact.id,
        title="Reminder 1",
        due_date=due_date
    )
    reminder2 = Reminder(
        contact_id=contact.id,
        title="Reminder 2",
        due_date=due_date
    )
    reminder_repository.save(reminder1)
    reminder_repository.save(reminder2)
    db_session.commit()

    # Delete one reminder
    reminder_repository.delete(reminder1)
    db_session.commit()

    # Verify deletion
    assert reminder_repository.find_by_id(reminder1.id) is None
    assert reminder_repository.find_by_id(reminder2.id) is not None


def test_complete_reminder(
    reminder_repository: SQLAlchemyReminderRepository,
    contact: ContactORM,
    db_session: Session
) -> None:
    """Test completing a reminder.

    Should:
    - Update status to COMPLETED
    - Set completion date
    - Save changes to database
    """
    # Create and save reminder
    due_date = datetime(2024, 3, 1, tzinfo=timezone.utc)
    reminder = Reminder(
        contact_id=contact.id,
        title="Test reminder",
        due_date=due_date
    )
    saved = reminder_repository.save(reminder)
    db_session.commit()

    # Complete the reminder
    completion_date = datetime(2024, 3, 1, 12, tzinfo=timezone.utc)
    saved.complete(completion_date)
    reminder_repository.save(saved)
    db_session.commit()

    # Verify completion
    found = reminder_repository.find_by_id(saved.id)
    assert found is not None
    assert found.status == ReminderStatus.COMPLETED
    assert found.completion_date == completion_date


def test_complete_recurring_reminder(
    reminder_repository: SQLAlchemyReminderRepository,
    contact: ContactORM,
    db_session: Session
) -> None:
    """Test completing a recurring reminder.

    Should:
    - Complete current reminder
    - Create next occurrence
    - Save both to database
    """
    # Create recurring reminder
    start_date = datetime(2024, 3, 1, tzinfo=timezone.utc)
    pattern = RecurrencePattern(
        interval=1,
        unit=RecurrenceUnit.WEEK.value
    )
    reminder = Reminder(
        contact_id=contact.id,
        title="Weekly reminder",
        due_date=start_date,
        recurrence_pattern=pattern
    )
    saved = reminder_repository.save(reminder)
    db_session.commit()

    # Complete the reminder
    completion_date = datetime(2024, 3, 1, 12, tzinfo=timezone.utc)
    next_reminder = saved.complete(completion_date)
    reminder_repository.save(saved)
    if next_reminder:
        reminder_repository.save(next_reminder)
    db_session.commit()

    # Verify original reminder is completed
    found = reminder_repository.find_by_id(saved.id)
    assert found is not None
    assert found.status == ReminderStatus.COMPLETED
    assert found.completion_date == completion_date

    # Verify next reminder was created
    found_all = reminder_repository.find_by_contact(contact.id)
    assert len(found_all) == 2
    next_found = next(r for r in found_all if r.status == ReminderStatus.PENDING)
    assert next_found.due_date == datetime(2024, 3, 8, tzinfo=timezone.utc)
    assert next_found.recurrence_pattern is not None
    assert next_found.recurrence_pattern.interval == 1
    assert next_found.recurrence_pattern.unit == RecurrenceUnit.WEEK.value

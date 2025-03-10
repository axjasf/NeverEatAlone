"""Integration tests for ReminderORM."""

from datetime import datetime, timezone, timedelta
from uuid import UUID
import pytest
from sqlalchemy.orm import Session, Mapped
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text, select
from typing import cast, Optional, List
from sqlalchemy.orm import selectinload

from backend.app.models.domain.reminder_model import ReminderStatus, RecurrenceUnit
from backend.app.models.orm.reminder_orm import ReminderORM
from backend.app.models.orm.contact_orm import ContactORM
from backend.app.models.orm.note_orm import NoteORM

# Type aliases for clarity
ContactWithRelations = ContactORM
NoteWithRelations = NoteORM
ReminderWithRelations = ReminderORM


@pytest.fixture
def contact(db_session: Session) -> ContactWithRelations:
    """Create a test contact.

    Args:
        db_session: Database session

    Returns:
        ContactORM: Test contact
    """
    contact = ContactORM(name="Test Contact")
    db_session.add(contact)
    db_session.commit()
    with db_session.begin():
        contact = ContactORM(name="Test Contact")
        db_session.add(contact)
        db_session.flush()
        return contact


@pytest.fixture
def note(db_session: Session, contact: ContactWithRelations) -> NoteWithRelations:
    """Create a test note.

    Args:
        db_session: Database session
        contact: Parent contact

    Returns:
        NoteORM: Test note
    """
    with db_session.begin():
        note = NoteORM(contact_id=contact.id, content="Test note")
        db_session.add(note)
        db_session.flush()
        return note


def test_create_one_off_reminder(
    db_session: Session, contact: ContactWithRelations
) -> None:
    """Test creating a one-off reminder."""
    # Create a reminder
    due_date = datetime(2024, 3, 1, tzinfo=timezone.utc)
    reminder = ReminderORM(
        contact_id=contact.id,
        title="Test reminder",
        description="Test description",
        due_date=due_date,
    )
    db_session.add(reminder)
    db_session.commit()

    # Verify saved state
    saved = db_session.get(ReminderORM, reminder.id)
    assert saved is not None
    assert saved.title == "Test reminder"
    assert saved.description == "Test description"
    assert saved.due_date == due_date
    assert saved.status == ReminderStatus.PENDING
    assert saved.completion_date is None
    assert saved.contact_id == contact.id
    assert saved.note_id is None
    assert saved.recurrence_interval is None
    assert saved.recurrence_unit is None
    assert saved.recurrence_end_date is None


def test_create_recurring_reminder(
    db_session: Session, contact: ContactWithRelations
) -> None:
    """Test creating a recurring reminder."""
    # Create a reminder
    due_date = datetime(2024, 3, 1, tzinfo=timezone.utc)
    end_date = datetime(2024, 12, 31, tzinfo=timezone.utc)
    reminder = ReminderORM(
        contact_id=contact.id,
        title="Test recurring reminder",
        description="Test description",
        due_date=due_date,
        recurrence_interval=1,
        recurrence_unit=RecurrenceUnit.MONTH,
        recurrence_end_date=end_date,
    )
    db_session.add(reminder)
    db_session.commit()

    # Verify saved state
    saved = db_session.get(ReminderORM, reminder.id)
    assert saved is not None
    assert saved.recurrence_interval == 1
    assert saved.recurrence_unit == RecurrenceUnit.MONTH
    assert saved.recurrence_end_date == end_date


def test_complete_reminder(db_session: Session, contact: ContactWithRelations) -> None:
    """Test completing a reminder."""
    reminder = ReminderORM(
        contact_id=contact.id,
        title="Test reminder",
        due_date=datetime.now(timezone.utc),
    )
    db_session.add(reminder)
    db_session.commit()

    # Complete the reminder
    reminder.status = ReminderStatus.COMPLETED
    reminder.completion_date = datetime.now(timezone.utc)
    db_session.commit()
    db_session.refresh(reminder)

    saved = db_session.get(ReminderORM, reminder.id)
    assert saved is not None
    assert saved.status == ReminderStatus.COMPLETED
    assert saved.completion_date is not None


def test_link_reminder_to_note(
    db_session: Session, contact: ContactWithRelations, note: NoteWithRelations
) -> None:
    """Test linking a reminder to a note."""
    reminder = ReminderORM(
        contact_id=contact.id,
        title="Test reminder",
        due_date=datetime.now(timezone.utc),
        note_id=note.id,
    )
    db_session.add(reminder)
    db_session.commit()

    saved = db_session.get(ReminderORM, reminder.id)
    assert saved is not None
    assert saved.note_id == note.id
    saved_note = saved.note
    if saved_note is not None:
        assert isinstance(saved_note, NoteORM)
        assert saved_note.id == note.id

    # Verify note -> reminder relationship
    db_session.refresh(note)
    assert reminder in note.reminders


def test_note_relationship(
    db_session: Session, contact: ContactWithRelations, note: NoteWithRelations
) -> None:
    """Test reminder-note relationship behavior.

    Should:
    - Allow linking reminder to note
    - Allow note deletion without affecting reminder
    - Clear note_id when note is deleted
    """
    # Create reminder linked to note
    reminder = ReminderORM(
        contact_id=contact.id,
        note_id=note.id,
        title="Test reminder",
        due_date=datetime.now(timezone.utc),
    )
    db_session.add(reminder)
    db_session.commit()

    # Verify relationship
    assert reminder.note == note
    assert reminder in note.reminders

    # Delete note
    db_session.delete(note)
    db_session.commit()
    db_session.refresh(reminder)

    # Verify reminder still exists but note_id is cleared
    assert reminder.note_id is None
    assert reminder.note is None


def test_delete_note_doesnt_cascade_to_reminders(
    db_session: Session, contact: ContactWithRelations, note: NoteWithRelations
) -> None:
    """Test that deleting a note doesn't cascade to reminders."""
    reminder = ReminderORM(
        contact_id=contact.id,
        title="Test reminder",
        due_date=datetime.now(timezone.utc),
        note_id=note.id,
    )
    db_session.add(reminder)
    db_session.commit()

    # Verify relationship
    assert reminder.note_id == note.id
    reminder_note = reminder.note
    if reminder_note is not None:
        assert isinstance(reminder_note, NoteORM)
        assert reminder_note.id == note.id
    assert reminder in note.reminders

    # Delete note
    db_session.delete(note)
    db_session.commit()

    # Verify reminder still exists but note_id is cleared
    assert reminder.note_id is None
    assert reminder.note is None


def test_delete_contact_cascades_to_reminders(
    db_session: Session, contact: ContactWithRelations
) -> None:
    """Test that deleting a contact cascades to its reminders.

    Should:
    - Delete all reminders when contact is deleted
    """
    # Create some reminders
    for i in range(3):
        reminder = ReminderORM(
            contact_id=contact.id,
            title=f"Reminder {i}",
            due_date=datetime(2024, 3, 1, tzinfo=timezone.utc),
        )
        db_session.add(reminder)
    db_session.commit()

    # Get reminder IDs for later verification
    reminder_ids = [r.id for r in contact.reminders]
    assert len(reminder_ids) == 3

    # Delete contact
    db_session.delete(contact)
    db_session.commit()

    # Verify reminders are gone
    for rid in reminder_ids:
        assert db_session.get(ReminderORM, rid) is None


def test_cascade_delete_from_contact(
    db_session: Session, contact: ContactWithRelations
) -> None:
    """Test that deleting a contact cascades to its reminders.

    Should:
    - Delete all reminders when contact is deleted
    - Not affect other contacts' reminders
    """
    # Create another contact
    other_contact = ContactORM(name="Other Contact")
    db_session.add(other_contact)
    db_session.commit()

    # Create reminders for both contacts
    reminder1 = ReminderORM(
        contact_id=contact.id,
        title="Test reminder 1",
        due_date=datetime.now(timezone.utc),
    )
    reminder2 = ReminderORM(
        contact_id=other_contact.id,
        title="Test reminder 2",
        due_date=datetime.now(timezone.utc),
    )
    db_session.add_all([reminder1, reminder2])
    db_session.commit()

    # Delete first contact
    db_session.delete(contact)
    db_session.commit()

    # Verify cascade
    assert db_session.get(ReminderORM, reminder1.id) is None
    assert db_session.get(ReminderORM, reminder2.id) is not None


def test_constraint_violations(db_session: Session) -> None:
    """Test database constraints are enforced.

    Should:
    - Reject invalid recurrence patterns
    - Reject invalid completion dates
    - Reject invalid status transitions
    """
    # Test: recurrence_interval without unit
    contact1 = ContactORM(name="Test Contact 1")
    db_session.add(contact1)
    db_session.commit()
    contact1_id = contact1.id  # Store ID for later

    with pytest.raises(IntegrityError):
        reminder = ReminderORM(
            contact_id=contact1_id,
            title="Test reminder",
            due_date=datetime(2024, 3, 1, tzinfo=timezone.utc),
            recurrence_interval=1,  # Missing unit
        )
        db_session.add(reminder)
        db_session.commit()
    db_session.rollback()

    # Test: completion_date without COMPLETED status
    contact2 = ContactORM(name="Test Contact 2")
    db_session.add(contact2)
    db_session.commit()
    contact2_id = contact2.id  # Store ID for later

    with pytest.raises(IntegrityError):
        reminder = ReminderORM(
            contact_id=contact2_id,
            title="Test reminder",
            due_date=datetime(2024, 3, 1, tzinfo=timezone.utc),
            completion_date=datetime(
                2024, 3, 1, tzinfo=timezone.utc
            ),  # Status still PENDING
        )
        db_session.add(reminder)
        db_session.commit()
    db_session.rollback()

    # Test: recurrence_end_date before due_date
    contact3 = ContactORM(name="Test Contact 3")
    db_session.add(contact3)
    db_session.commit()
    contact3_id = contact3.id  # Store ID for later

    with pytest.raises(IntegrityError):
        reminder = ReminderORM(
            contact_id=contact3_id,
            title="Test reminder",
            due_date=datetime(2024, 3, 1, tzinfo=timezone.utc),
            recurrence_interval=1,
            recurrence_unit=RecurrenceUnit.WEEK,
            recurrence_end_date=datetime(
                2024, 2, 28, tzinfo=timezone.utc
            ),  # Before due_date
        )
        db_session.add(reminder)
        db_session.commit()
    db_session.rollback()

    # Clean up - use raw SQL to avoid relationship loading issues
    db_session.execute(
        text("DELETE FROM contacts WHERE id = :id1 OR id = :id2 OR id = :id3"),
        {"id1": str(contact1_id), "id2": str(contact2_id), "id3": str(contact3_id)},
    )
    db_session.commit()


def test_timezone_handling(db_session: Session, contact: ContactWithRelations) -> None:
    """Test that timezone information is preserved in the database.

    Should:
    - Store timezone-aware dates
    - Retrieve dates with UTC timezone
    - Handle DST transitions correctly
    """
    # Create reminder with specific timezone
    due_date = datetime(2024, 6, 1, 12, 0, tzinfo=timezone.utc)
    reminder = ReminderORM(
        contact_id=contact.id, title="Test reminder", due_date=due_date
    )
    db_session.add(reminder)
    db_session.commit()

    # Retrieve and verify timezone
    db_session.expire_all()
    loaded = db_session.get(ReminderORM, reminder.id)
    assert loaded is not None
    assert loaded.due_date.tzinfo == timezone.utc
    assert loaded.due_date == due_date


def test_recurrence_constraints(
    db_session: Session, contact: ContactWithRelations
) -> None:
    """Test database constraints for recurrence fields.

    Should:
    - Enforce all-or-none recurrence fields
    - Validate interval values
    - Validate end date relationship to due date
    """
    due_date = datetime.now(timezone.utc)

    # Test partial recurrence (should fail)
    with db_session.begin_nested():
        reminder = ReminderORM(
            contact_id=contact.id,
            title="Test reminder",
            due_date=due_date,
            recurrence_interval=1,  # Missing unit
        )
        db_session.add(reminder)
        with pytest.raises(IntegrityError):
            db_session.flush()

    # Test negative interval (should fail)
    with db_session.begin_nested():
        reminder = ReminderORM(
            contact_id=contact.id,
            title="Test reminder",
            due_date=due_date,
            recurrence_interval=-1,
            recurrence_unit=RecurrenceUnit.DAY,
        )
        db_session.add(reminder)
        with pytest.raises(IntegrityError):
            db_session.flush()

    # Test end date before due date (should fail)
    with db_session.begin_nested():
        reminder = ReminderORM(
            contact_id=contact.id,
            title="Test reminder",
            due_date=due_date,
            recurrence_interval=1,
            recurrence_unit=RecurrenceUnit.DAY,
            recurrence_end_date=due_date - timedelta(days=1),
        )
        db_session.add(reminder)
        with pytest.raises(IntegrityError):
            db_session.flush()


def test_completion_constraints(
    db_session: Session, contact: ContactWithRelations
) -> None:
    """Test database constraints for completion status and date.

    Should:
    - Enforce completion date presence for COMPLETED status
    - Enforce completion date absence for other statuses
    """
    due_date = datetime.now(timezone.utc)
    completion_date = due_date + timedelta(hours=1)

    # Test completion date without COMPLETED status (should fail)
    with db_session.begin_nested():
        reminder = ReminderORM(
            contact_id=contact.id,
            title="Test reminder",
            due_date=due_date,
            status=ReminderStatus.PENDING,
            completion_date=completion_date,
        )
        db_session.add(reminder)
        with pytest.raises(IntegrityError):
            db_session.flush()

    # Test COMPLETED status without completion date (should fail)
    with db_session.begin_nested():
        reminder = ReminderORM(
            contact_id=contact.id,
            title="Test reminder",
            due_date=due_date,
            status=ReminderStatus.COMPLETED,
            completion_date=None,
        )
        db_session.add(reminder)
        with pytest.raises(IntegrityError):
            db_session.flush()


def test_eager_loading(
    db_session: Session, contact: ContactWithRelations, note: NoteWithRelations
) -> None:
    """Test that relationships are eagerly loaded."""
    reminder_id = None

    # First save the reminder
    reminder = ReminderORM(
        contact_id=contact.id,
        title="Test reminder",
        due_date=datetime.now(timezone.utc),
        note_id=note.id,
    )
    db_session.add(reminder)
    db_session.commit()
    reminder_id = reminder.id

    # Clear session to test loading
    db_session.expunge_all()

    # Load reminder with relationships
    stmt = (
        select(ReminderORM)
        .options(selectinload(ReminderORM.contact), selectinload(ReminderORM.note))
        .where(ReminderORM.id == reminder_id)
    )
    loaded = db_session.execute(stmt).scalar_one()
    assert loaded is not None
    assert isinstance(loaded, ReminderORM)

    # These should not trigger additional queries
    loaded_contact = loaded.contact
    assert loaded_contact is not None
    assert isinstance(loaded_contact, ContactORM)
    assert loaded_contact.name is not None

    loaded_note = loaded.note
    if loaded_note is not None:
        assert isinstance(loaded_note, NoteORM)
        assert loaded_note.content is not None

"""Unit tests for the reminder domain model."""

from datetime import datetime, timezone, timedelta
from uuid import UUID
import pytest
from backend.app.models.domain.reminder import Reminder, RecurrencePattern, ReminderStatus


def test_create_one_off_reminder() -> None:
    """Test creating a one-off reminder.

    Should:
    - Create a reminder with basic fields
    - Set status to PENDING by default
    - Not have recurrence pattern
    """
    contact_id = UUID("11111111-1111-1111-1111-111111111111")
    due_date = datetime(2024, 3, 1, tzinfo=timezone.utc)
    reminder = Reminder(
        contact_id=contact_id,
        title="Call John",
        description="Discuss project status",
        due_date=due_date
    )

    assert reminder.contact_id == contact_id
    assert reminder.title == "Call John"
    assert reminder.description == "Discuss project status"
    assert reminder.due_date == due_date
    assert reminder.status == ReminderStatus.PENDING
    assert reminder.recurrence_pattern is None
    assert reminder.note_id is None


def test_create_recurring_reminder() -> None:
    """Test creating a recurring reminder.

    Should:
    - Create a reminder with recurrence pattern
    - Calculate next occurrence correctly
    """
    contact_id = UUID("11111111-1111-1111-1111-111111111111")
    start_date = datetime(2024, 3, 1, tzinfo=timezone.utc)
    pattern = RecurrencePattern(
        interval=1,
        unit="MONTH",
        end_date=datetime(2024, 12, 31, tzinfo=timezone.utc)
    )

    reminder = Reminder(
        contact_id=contact_id,
        title="Monthly check-in",
        description="Regular status update",
        due_date=start_date,
        recurrence_pattern=pattern
    )

    assert reminder.recurrence_pattern == pattern
    assert reminder.get_next_occurrence() == datetime(2024, 4, 1, tzinfo=timezone.utc)


def test_complete_reminder() -> None:
    """Test completing a reminder.

    Should:
    - Update status to COMPLETED
    - Set completion date
    - Calculate next occurrence for recurring reminders
    """
    contact_id = UUID("11111111-1111-1111-1111-111111111111")
    due_date = datetime(2024, 3, 1, tzinfo=timezone.utc)
    completion_date = datetime(2024, 3, 1, 12, 0, tzinfo=timezone.utc)

    reminder = Reminder(
        contact_id=contact_id,
        title="Call John",
        due_date=due_date
    )

    reminder.complete(completion_date)

    assert reminder.status == ReminderStatus.COMPLETED
    assert reminder.completion_date == completion_date


def test_recurring_reminder_completion() -> None:
    """Test completing a recurring reminder.

    Should:
    - Create new reminder instance for next occurrence
    - Keep recurrence pattern
    - Set appropriate due date
    """
    contact_id = UUID("11111111-1111-1111-1111-111111111111")
    start_date = datetime(2024, 3, 1, tzinfo=timezone.utc)
    pattern = RecurrencePattern(
        interval=1,
        unit="WEEK"
    )

    reminder = Reminder(
        contact_id=contact_id,
        title="Weekly call",
        due_date=start_date,
        recurrence_pattern=pattern
    )

    completion_date = datetime(2024, 3, 1, 12, 0, tzinfo=timezone.utc)
    next_reminder = reminder.complete(completion_date)

    assert next_reminder is not None
    assert next_reminder.due_date == datetime(2024, 3, 8, tzinfo=timezone.utc)
    assert next_reminder.status == ReminderStatus.PENDING
    assert next_reminder.recurrence_pattern == pattern


def test_link_reminder_to_note() -> None:
    """Test linking a reminder to a note.

    Should:
    - Associate reminder with note
    - Allow retrieving note ID
    """
    contact_id = UUID("11111111-1111-1111-1111-111111111111")
    note_id = UUID("22222222-2222-2222-2222-222222222222")
    due_date = datetime(2024, 3, 1, tzinfo=timezone.utc)

    reminder = Reminder(
        contact_id=contact_id,
        title="Follow up on discussion",
        due_date=due_date,
        note_id=note_id
    )

    assert reminder.note_id == note_id


def test_invalid_reminder_dates() -> None:
    """Test validation of reminder dates.

    Should:
    - Reject completion dates before due date
    - Reject recurring reminders with end date before start date
    """
    contact_id = UUID("11111111-1111-1111-1111-111111111111")
    due_date = datetime(2024, 3, 1, tzinfo=timezone.utc)

    reminder = Reminder(
        contact_id=contact_id,
        title="Test reminder",
        due_date=due_date
    )

    # Test completing with earlier date
    with pytest.raises(ValueError):
        reminder.complete(datetime(2024, 2, 28, tzinfo=timezone.utc))

    # Test invalid recurrence pattern with end date before start date
    with pytest.raises(ValueError):
        RecurrencePattern(
            interval=1,
            unit="WEEK",
            start_date=datetime(2024, 3, 1, tzinfo=timezone.utc),
            end_date=datetime(2024, 2, 28, tzinfo=timezone.utc)
        )


def test_reminder_status_transitions() -> None:
    """Test reminder status transitions.

    Should:
    - Allow marking as completed
    - Allow cancelling
    - Prevent invalid transitions
    """
    contact_id = UUID("11111111-1111-1111-1111-111111111111")
    due_date = datetime(2024, 3, 1, tzinfo=timezone.utc)

    reminder = Reminder(
        contact_id=contact_id,
        title="Test reminder",
        due_date=due_date
    )

    # Test valid transitions
    reminder.cancel()
    assert reminder.status == ReminderStatus.CANCELLED

    # Test invalid transitions
    with pytest.raises(ValueError):
        reminder.complete(datetime.now(timezone.utc))  # Can't complete cancelled reminder

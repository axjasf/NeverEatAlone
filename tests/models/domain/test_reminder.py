"""Unit tests for the reminder domain model."""

from datetime import datetime, timezone, timedelta
from uuid import UUID
import pytest
from backend.app.models.domain.reminder_model import (
    Reminder,
    RecurrencePattern,
    ReminderStatus,
    RecurrenceUnit,
)

# Test data
TEST_UUID = UUID("11111111-1111-1111-1111-111111111111")
TEST_DATETIME = datetime(2024, 1, 1, tzinfo=timezone.utc)


def test_reminder_minimum_fields() -> None:
    """Test reminder creation with minimum required fields.

    Should:
    - Create with only required fields
    - Set appropriate defaults
    - Validate required fields
    """
    # Test minimum valid fields
    reminder = Reminder(
        contact_id=TEST_UUID, title="Test reminder", due_date=TEST_DATETIME
    )
    assert reminder.title == "Test reminder"
    assert reminder.due_date == TEST_DATETIME
    assert reminder.description is None
    assert reminder.note_id is None
    assert reminder.recurrence_pattern is None
    assert reminder.status == ReminderStatus.PENDING
    assert reminder.completion_date is None

    # Test empty title
    with pytest.raises(ValueError, match="Title cannot be empty"):
        Reminder(contact_id=TEST_UUID, title="", due_date=TEST_DATETIME)

    # Test whitespace title
    with pytest.raises(ValueError, match="Title cannot be empty"):
        Reminder(contact_id=TEST_UUID, title="   ", due_date=TEST_DATETIME)


def test_reminder_requires_timezone() -> None:
    """Test that reminder creation requires timezone-aware datetime.

    Should:
    - Reject naive datetime
    - Accept timezone-aware datetime
    - Preserve timezone information
    """
    # Reject naive datetime
    with pytest.raises(ValueError, match="must be timezone-aware"):
        Reminder(
            contact_id=TEST_UUID,
            title="Test reminder",
            due_date=datetime(2024, 1, 1),  # No timezone
        )

    # Accept timezone-aware datetime
    reminder = Reminder(
        contact_id=TEST_UUID, title="Test reminder", due_date=TEST_DATETIME
    )
    assert reminder.due_date.tzinfo == timezone.utc


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
        due_date=due_date,
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
        interval=1, unit="MONTH", end_date=datetime(2024, 12, 31, tzinfo=timezone.utc)
    )

    reminder = Reminder(
        contact_id=contact_id,
        title="Monthly check-in",
        description="Regular status update",
        due_date=start_date,
        recurrence_pattern=pattern,
    )

    assert reminder.recurrence_pattern == pattern
    assert reminder.get_next_occurrence() == datetime(2024, 4, 1, tzinfo=timezone.utc)


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
        note_id=note_id,
    )

    assert reminder.note_id == note_id


def test_reminder_status_transitions() -> None:
    """Test reminder status transitions.

    Should:
    - Start as PENDING
    - Allow completion with valid date
    - Allow cancellation
    - Prevent invalid transitions
    """
    reminder = Reminder(
        contact_id=TEST_UUID, title="Test reminder", due_date=TEST_DATETIME
    )
    assert reminder.status == ReminderStatus.PENDING

    # Test completion
    completion_date = TEST_DATETIME + timedelta(days=1)
    reminder.complete(completion_date)
    assert reminder.status == ReminderStatus.COMPLETED
    assert reminder.completion_date == completion_date

    # Test completing already completed reminder
    with pytest.raises(
        ValueError, match="Cannot complete reminder in COMPLETED status"
    ):
        reminder.complete(completion_date)

    # Test cancellation
    reminder = Reminder(
        contact_id=TEST_UUID, title="Test reminder", due_date=TEST_DATETIME
    )
    reminder.cancel()
    assert reminder.status == ReminderStatus.CANCELLED

    # Test completing cancelled reminder
    with pytest.raises(
        ValueError, match="Cannot complete reminder in CANCELLED status"
    ):
        reminder.complete(completion_date)


def test_reminder_cancellation() -> None:
    """Test reminder cancellation.

    Should:
    - Allow cancelling
    - Prevent completing cancelled reminders
    """
    contact_id = UUID("11111111-1111-1111-1111-111111111111")
    due_date = datetime(2024, 3, 1, tzinfo=timezone.utc)

    reminder = Reminder(contact_id=contact_id, title="Test reminder", due_date=due_date)

    # Test valid transitions
    reminder.cancel()
    assert reminder.status == ReminderStatus.CANCELLED

    # Test invalid transitions
    with pytest.raises(ValueError):
        reminder.complete(
            datetime.now(timezone.utc)
        )  # Can't complete cancelled reminder


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

    reminder = Reminder(contact_id=contact_id, title="Call John", due_date=due_date)

    reminder.complete(completion_date)

    assert reminder.status == ReminderStatus.COMPLETED
    assert reminder.completion_date == completion_date


def test_reminder_completion_date_validation() -> None:
    """Test validation of reminder completion dates.

    Should:
    - Reject completion before due date
    - Accept completion on due date
    - Accept completion after due date
    - Require timezone-aware completion date
    """
    reminder = Reminder(
        contact_id=TEST_UUID, title="Test reminder", due_date=TEST_DATETIME
    )

    # Test completion before due date
    early_date = TEST_DATETIME - timedelta(days=1)
    with pytest.raises(ValueError, match="Completion date cannot be before due date"):
        reminder.complete(early_date)

    # Test completion on due date
    reminder.complete(TEST_DATETIME)
    assert reminder.status == ReminderStatus.COMPLETED
    assert reminder.completion_date == TEST_DATETIME

    # Test naive completion date
    reminder = Reminder(
        contact_id=TEST_UUID, title="Test reminder", due_date=TEST_DATETIME
    )
    with pytest.raises(ValueError, match="must be timezone-aware"):
        reminder.complete(datetime(2024, 1, 1))


def test_recurrence_pattern_validation() -> None:
    """Test validation of recurrence patterns.

    Should:
    - Validate interval values
    - Validate unit values
    - Validate end date if provided
    """
    # Test invalid interval
    with pytest.raises(ValueError, match="Interval must be at least 1"):
        RecurrencePattern(interval=0, unit="DAY")

    # Test invalid unit
    with pytest.raises(ValueError, match="Invalid recurrence unit"):
        RecurrencePattern(interval=1, unit="INVALID")

    # Test end date before start date
    end_date = TEST_DATETIME - timedelta(days=1)
    with pytest.raises(ValueError, match="End date must be after start date"):
        RecurrencePattern(
            interval=1, unit="DAY", start_date=TEST_DATETIME, end_date=end_date
        )

    # Test naive end date
    with pytest.raises(ValueError, match="must be timezone-aware"):
        RecurrencePattern(interval=1, unit="DAY", end_date=datetime(2024, 1, 1))


def test_recurrence_next_occurrence() -> None:
    """Test calculation of next occurrence dates.

    Should:
    - Calculate correct next date for each unit
    - Handle month/year transitions
    - Respect end date if set
    """
    # Daily recurrence
    pattern = RecurrencePattern(interval=1, unit="DAY")
    next_date = pattern.get_next_date(TEST_DATETIME)
    assert next_date == TEST_DATETIME + timedelta(days=1)

    # Weekly recurrence
    pattern = RecurrencePattern(interval=2, unit="WEEK")
    next_date = pattern.get_next_date(TEST_DATETIME)
    assert next_date == TEST_DATETIME + timedelta(weeks=2)

    # Monthly recurrence (handle different month lengths)
    jan31 = datetime(2024, 1, 31, tzinfo=timezone.utc)
    pattern = RecurrencePattern(interval=1, unit="MONTH")
    next_date = pattern.get_next_date(jan31)
    assert next_date == datetime(2024, 2, 29, tzinfo=timezone.utc)  # Leap year

    # Yearly recurrence
    pattern = RecurrencePattern(interval=1, unit="YEAR")
    next_date = pattern.get_next_date(TEST_DATETIME)
    assert next_date == datetime(2025, 1, 1, tzinfo=timezone.utc)

    # With end date
    pattern = RecurrencePattern(
        interval=1, unit="DAY", end_date=TEST_DATETIME + timedelta(days=1)
    )
    next_date = pattern.get_next_date(TEST_DATETIME)
    assert next_date == TEST_DATETIME + timedelta(days=1)
    assert pattern.get_next_date(next_date) is None  # No more occurrences


def test_recurring_reminder_completion() -> None:
    """Test completing a recurring reminder.

    Should:
    - Complete current reminder
    - Create next occurrence if within end date
    - Not create next occurrence if past end date
    - Preserve recurrence pattern in next occurrence
    """
    pattern = RecurrencePattern(interval=1, unit="WEEK")
    reminder = Reminder(
        contact_id=TEST_UUID,
        title="Weekly reminder",
        due_date=TEST_DATETIME,
        recurrence_pattern=pattern,
    )

    # Complete and get next occurrence
    completion_date = TEST_DATETIME + timedelta(hours=1)
    next_reminder = reminder.complete(completion_date)
    assert next_reminder is not None
    assert next_reminder.due_date == TEST_DATETIME + timedelta(weeks=1)
    assert next_reminder.title == "Weekly reminder"
    assert next_reminder.recurrence_pattern == pattern

    # Test with end date
    pattern_with_end = RecurrencePattern(
        interval=1, unit="WEEK", end_date=TEST_DATETIME + timedelta(days=1)
    )
    reminder = Reminder(
        contact_id=TEST_UUID,
        title="Limited reminder",
        due_date=TEST_DATETIME,
        recurrence_pattern=pattern_with_end,
    )
    next_reminder = reminder.complete(completion_date)
    assert next_reminder is None  # No next occurrence as it would be past end date


def test_invalid_reminder_dates() -> None:
    """Test validation of reminder dates.

    Should:
    - Reject completion dates before due date
    - Reject recurring reminders with end date before start date
    """
    contact_id = UUID("11111111-1111-1111-1111-111111111111")
    due_date = datetime(2024, 3, 1, tzinfo=timezone.utc)

    reminder = Reminder(contact_id=contact_id, title="Test reminder", due_date=due_date)

    # Test completing with earlier date
    with pytest.raises(ValueError):
        reminder.complete(datetime(2024, 2, 28, tzinfo=timezone.utc))

    # Test invalid recurrence pattern with end date before start date
    with pytest.raises(ValueError):
        RecurrencePattern(
            interval=1,
            unit="WEEK",
            start_date=datetime(2024, 3, 1, tzinfo=timezone.utc),
            end_date=datetime(2024, 2, 28, tzinfo=timezone.utc),
        )

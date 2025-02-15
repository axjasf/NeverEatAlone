"""Reminder domain model."""

from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Optional
from uuid import UUID
from .base_model import BaseModel


class ReminderStatus(str, Enum):
    """Status of a reminder."""

    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class RecurrenceUnit(str, Enum):
    """Unit of time for recurrence pattern."""

    DAY = "DAY"
    WEEK = "WEEK"
    MONTH = "MONTH"
    YEAR = "YEAR"


class RecurrencePattern:
    """Pattern for recurring reminders."""

    def __init__(
        self,
        interval: int,
        unit: str,
        end_date: Optional[datetime] = None,
        start_date: Optional[datetime] = None,
    ) -> None:
        """Initialize a recurrence pattern.

        Args:
            interval: Number of units between occurrences
            unit: Time unit (DAY, WEEK, MONTH, YEAR)
            end_date: Optional end date for the recurrence
            start_date: Optional start date for validation

        Raises:
            ValueError: If interval is less than 1 or unit is invalid
        """
        if interval < 1:
            raise ValueError("Interval must be at least 1")

        try:
            self.unit = RecurrenceUnit(unit)
        except ValueError:
            raise ValueError(
                "Invalid recurrence unit. Must be one of: "
                f"{', '.join(u.value for u in RecurrenceUnit)}"
            )

        self.interval = interval

        # Validate end_date
        if end_date:
            if not end_date.tzinfo:
                raise ValueError("End date must be timezone-aware")
            if start_date and end_date <= start_date:
                raise ValueError("End date must be after start date")
        self.end_date = end_date

    def __eq__(self, other: object) -> bool:
        """Compare two recurrence patterns for equality.

        Args:
            other: The other pattern to compare with

        Returns:
            True if patterns are equal, False otherwise
        """
        if not isinstance(other, RecurrencePattern):
            return NotImplemented
        return (
            self.interval == other.interval
            and self.unit == other.unit
            and self.end_date == other.end_date
        )

    def get_next_date(self, from_date: datetime) -> Optional[datetime]:
        """Calculate the next occurrence after a given date.

        Args:
            from_date: The date to calculate from

        Returns:
            Next occurrence date, or None if recurrence has ended
        """
        if not self._is_valid_date(from_date):
            return None

        normalized_date = self._normalize_to_midnight_utc(from_date)
        next_date = self._calculate_next_date(normalized_date)

        return next_date if self._is_within_bounds(next_date) else None

    def _is_valid_date(self, date: datetime) -> bool:
        """Check if date is valid for calculation."""
        if not date.tzinfo:
            raise ValueError("From date must be timezone-aware")
        return not (self.end_date and date >= self.end_date)

    def _normalize_to_midnight_utc(self, date: datetime) -> datetime:
        """Normalize date to midnight UTC."""
        return datetime.combine(
            date.date(),
            datetime.min.time(),
            tzinfo=timezone.utc
        )

    def _calculate_next_date(self, date: datetime) -> datetime:
        """Calculate next date based on recurrence unit."""
        if self.unit == RecurrenceUnit.DAY:
            return date + timedelta(days=self.interval)
        if self.unit == RecurrenceUnit.WEEK:
            return date + timedelta(weeks=self.interval)
        if self.unit == RecurrenceUnit.YEAR:
            return date.replace(year=date.year + self.interval)

        # Handle monthly recurrence
        return self._calculate_next_month_date(date)

    def _calculate_next_month_date(self, date: datetime) -> datetime:
        """Handle the complex case of monthly recurrence."""
        year, month = self._get_next_year_and_month(date)
        day = min(date.day, self._get_days_in_month(year, month))
        return datetime(year, month, day, tzinfo=timezone.utc)

    def _get_next_year_and_month(self, date: datetime) -> tuple[int, int]:
        """Calculate the next year and month."""
        year = date.year
        month = date.month + self.interval

        # Adjust year and month if we've gone past December
        year += (month - 1) // 12
        month = ((month - 1) % 12) + 1

        return year, month

    def _get_days_in_month(self, year: int, month: int) -> int:
        """Get number of days in the specified month."""
        days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        if month == 2 and year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
            return 29
        return days[month - 1]

    def _is_within_bounds(self, date: datetime) -> bool:
        """Check if date is within the recurrence bounds."""
        return not (self.end_date and date > self.end_date)


class Reminder(BaseModel):
    """A reminder for a contact.

    Can be one-off or recurring, and can be linked to a specific note.
    """

    def __init__(
        self,
        contact_id: UUID,
        title: str,
        due_date: datetime,
        description: Optional[str] = None,
        recurrence_pattern: Optional[RecurrencePattern] = None,
        note_id: Optional[UUID] = None,
    ) -> None:
        """Initialize a reminder.

        Args:
            contact_id: ID of the contact this reminder is for
            title: Title of the reminder
            due_date: When the reminder is due
            description: Optional description
            recurrence_pattern: Optional pattern for recurring reminders
            note_id: Optional ID of a linked note

        Raises:
            ValueError: If title is empty or due_date has no timezone
        """
        super().__init__()
        if not title.strip():
            raise ValueError("Title cannot be empty")
        if not due_date.tzinfo:
            raise ValueError("Due date must be timezone-aware")

        self.contact_id = contact_id
        self.title = title.strip()
        self.description = description.strip() if description else None
        self.due_date = due_date
        self.status = ReminderStatus.PENDING
        self.completion_date: Optional[datetime] = None
        self.recurrence_pattern = recurrence_pattern
        self.note_id = note_id

        # Validate recurrence pattern if provided
        if recurrence_pattern:
            recurrence_pattern.get_next_date(due_date)  # This will validate dates

    def complete(self, completion_date: datetime) -> Optional["Reminder"]:
        """Mark the reminder as completed.

        Args:
            completion_date: When the reminder was completed

        Returns:
            New reminder instance if this was recurring, None otherwise

        Raises:
            ValueError: If reminder is already completed/cancelled or
                completion_date is invalid
        """
        if self.status != ReminderStatus.PENDING:
            raise ValueError(
                f"Cannot complete reminder in {self.status.value.upper()} status"
            )

        if not completion_date.tzinfo:
            raise ValueError("Completion date must be timezone-aware")

        if completion_date < self.due_date:
            raise ValueError("Completion date cannot be before due date")

        self.status = ReminderStatus.COMPLETED
        self.completion_date = completion_date
        self._update_timestamp()

        # If this is a recurring reminder, create the next instance
        if self.recurrence_pattern:
            next_date = self.get_next_occurrence()
            if next_date:
                return Reminder(
                    contact_id=self.contact_id,
                    title=self.title,
                    description=self.description,
                    due_date=next_date,
                    recurrence_pattern=self.recurrence_pattern,
                    note_id=self.note_id,
                )
        return None

    def cancel(self) -> None:
        """Cancel the reminder.

        Raises:
            ValueError: If reminder is already completed/cancelled
        """
        if self.status != ReminderStatus.PENDING:
            raise ValueError(f"Cannot cancel reminder in {self.status} status")

        self.status = ReminderStatus.CANCELLED
        self._update_timestamp()

    def get_next_occurrence(self) -> Optional[datetime]:
        """Calculate the next occurrence date for a recurring reminder.

        Returns:
            Next occurrence date, or None if not recurring or no more occurrences
        """
        if not self.recurrence_pattern:
            return None

        from_date = self.completion_date or self.due_date
        return self.recurrence_pattern.get_next_date(from_date)

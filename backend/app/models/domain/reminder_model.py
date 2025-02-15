"""Reminder domain model."""

from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Optional, Dict, Callable
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


class DateValidationError(ValueError):
    """Custom error for date validation failures."""

    pass


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
            DateValidationError: If dates are invalid
        """
        self._validate_interval(interval)
        self.interval = interval
        self.unit = self._validate_and_parse_unit(unit)
        self.end_date = self._validate_end_date(end_date, start_date)

    def _validate_interval(self, interval: int) -> None:
        """Validate the recurrence interval."""
        if interval < 1:
            raise ValueError("Interval must be at least 1")

    def _validate_and_parse_unit(self, unit: str) -> RecurrenceUnit:
        """Validate and parse the recurrence unit."""
        try:
            return RecurrenceUnit(unit)
        except ValueError:
            raise ValueError(
                "Invalid recurrence unit. Must be one of: "
                f"{', '.join(u.value for u in RecurrenceUnit)}"
            )

    def _validate_end_date(
        self, end_date: Optional[datetime], start_date: Optional[datetime]
    ) -> Optional[datetime]:
        """Validate the end date if provided."""
        if not end_date:
            return None

        if not end_date.tzinfo:
            raise DateValidationError("End date must be timezone-aware")

        if start_date and end_date <= start_date:
            raise DateValidationError("End date must be after start date")

        return end_date

    def __eq__(self, other: object) -> bool:
        """Compare two recurrence patterns for equality."""
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

        Raises:
            DateValidationError: If from_date is not timezone-aware
        """
        self._validate_from_date(from_date)

        if self._is_past_end_date(from_date):
            return None

        next_date = self._calculate_next_date(from_date)
        return next_date if not self._is_past_end_date(next_date) else None

    def _validate_from_date(self, date: datetime) -> None:
        """Validate that a date is timezone-aware."""
        if not date.tzinfo:
            raise DateValidationError("From date must be timezone-aware")

    def _is_past_end_date(self, date: datetime) -> bool:
        """Check if a date is past the end date."""
        return bool(self.end_date and date > self.end_date)

    def _calculate_next_date(self, from_date: datetime) -> datetime:
        """Calculate the next occurrence date based on the unit.

        Args:
            from_date: Base date for calculation

        Returns:
            Next occurrence date
        """
        # Normalize to midnight UTC for consistent calculations
        date = datetime.combine(
            from_date.date(), datetime.min.time(), tzinfo=timezone.utc
        )

        calculation_methods: Dict[RecurrenceUnit, Callable[[datetime], datetime]] = {
            RecurrenceUnit.DAY: self._add_days,
            RecurrenceUnit.WEEK: self._add_weeks,
            RecurrenceUnit.MONTH: self._add_months,
            RecurrenceUnit.YEAR: self._add_years,
        }

        return calculation_methods[self.unit](date)

    def _add_days(self, date: datetime) -> datetime:
        """Add days to a date."""
        return date + timedelta(days=self.interval)

    def _add_weeks(self, date: datetime) -> datetime:
        """Add weeks to a date."""
        return date + timedelta(weeks=self.interval)

    def _add_months(self, date: datetime) -> datetime:
        """Add months to a date, handling month length differences."""
        year = date.year
        month = date.month + self.interval

        # Handle year rollover
        if month > 12:
            year += month // 12
            month = month % 12
            if month == 0:
                month = 12
                year -= 1

        # Handle month length differences (e.g., Jan 31 -> Feb 28)
        max_day = self._get_days_in_month(year, month)
        day = min(date.day, max_day)

        return datetime(year, month, day, tzinfo=timezone.utc)

    def _add_years(self, date: datetime) -> datetime:
        """Add years to a date."""
        return date.replace(year=date.year + self.interval)

    def _get_days_in_month(self, year: int, month: int) -> int:
        """Get the number of days in a specific month."""
        days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

        if month == 2 and self._is_leap_year(year):
            return 29

        return days_in_month[month - 1]

    def _is_leap_year(self, year: int) -> bool:
        """Check if a year is a leap year."""
        return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


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
        self._validate_title(title)
        self._validate_due_date(due_date)

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

    def _validate_title(self, title: str) -> None:
        """Validate the reminder title."""
        if not title.strip():
            raise ValueError("Title cannot be empty")

    def _validate_due_date(self, due_date: datetime) -> None:
        """Validate the due date."""
        if not due_date.tzinfo:
            raise ValueError("Due date must be timezone-aware")

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
        self._validate_completion(completion_date)

        self.status = ReminderStatus.COMPLETED
        self.completion_date = completion_date
        self._update_timestamp()

        return self._create_next_occurrence() if self.recurrence_pattern else None

    def _validate_completion(self, completion_date: datetime) -> None:
        """Validate completion state and date."""
        if self.status != ReminderStatus.PENDING:
            raise ValueError(
                f"Cannot complete reminder in {self.status.value.upper()} status"
            )

        if not completion_date.tzinfo:
            raise ValueError("Completion date must be timezone-aware")

        if completion_date < self.due_date:
            raise ValueError("Completion date cannot be before due date")

    def _create_next_occurrence(self) -> Optional["Reminder"]:
        """Create the next occurrence of a recurring reminder."""
        if not self.recurrence_pattern:
            return None

        next_date = self.get_next_occurrence()
        if not next_date:
            return None

        return Reminder(
            contact_id=self.contact_id,
            title=self.title,
            description=self.description,
            due_date=next_date,
            recurrence_pattern=self.recurrence_pattern,
            note_id=self.note_id,
        )

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

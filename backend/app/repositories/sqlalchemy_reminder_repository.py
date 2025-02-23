"""SQLAlchemy implementation of reminder repository."""

from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from sqlalchemy import select, and_
from sqlalchemy.orm import Session, selectinload
from ..models.domain.reminder_model import (
    RecurrencePattern,
    Reminder,
    ReminderStatus,
)
from .interfaces import ReminderRepository
from ..models.orm.reminder_orm import ReminderORM


class SQLAlchemyReminderRepository(ReminderRepository):
    """SQLAlchemy implementation of reminder persistence."""

    def __init__(self, session: Session) -> None:
        """Initialize the repository.

        Args:
            session: SQLAlchemy session
        """
        self._session = session

    def save(self, reminder: Reminder) -> Reminder:
        """Save a reminder.

        Args:
            reminder: The reminder to save

        Returns:
            The saved reminder with any updates from the database
        """
        # Convert domain model to ORM
        reminder_orm = ReminderORM(
            id=reminder.id,
            contact_id=reminder.contact_id,
            note_id=reminder.note_id,
            title=reminder.title,
            description=reminder.description,
            due_date=reminder.due_date.astimezone(timezone.utc),  # Store in UTC
            due_date_timezone=reminder.due_date.tzinfo.key if isinstance(reminder.due_date.tzinfo, ZoneInfo) else "UTC",
            status=reminder.status,
            completion_date=(
                reminder.completion_date.astimezone(timezone.utc)
                if reminder.completion_date is not None
                else None
            ),
            completion_date_timezone=(
                reminder.completion_date.tzinfo.key if reminder.completion_date is not None and isinstance(reminder.completion_date.tzinfo, ZoneInfo) else "UTC"
                if reminder.completion_date is not None
                else None
            ),
        )

        # Add recurrence pattern if present
        if reminder.recurrence_pattern:
            reminder_orm.recurrence_interval = reminder.recurrence_pattern.interval
            reminder_orm.recurrence_unit = reminder.recurrence_pattern.unit
            reminder_orm.recurrence_end_date = (
                reminder.recurrence_pattern.end_date.astimezone(timezone.utc)
                if reminder.recurrence_pattern.end_date is not None
                else None
            )

        # Merge to handle both insert and update
        reminder_orm = self._session.merge(reminder_orm)
        self._session.flush()

        # Return the saved reminder
        return self._to_domain(reminder_orm)

    def find_by_id(self, reminder_id: UUID) -> Optional[Reminder]:
        """Find a reminder by its ID.

        Args:
            reminder_id: The ID to search for

        Returns:
            The reminder if found, None otherwise
        """
        stmt = (
            select(ReminderORM)
            .options(selectinload(ReminderORM.contact), selectinload(ReminderORM.note))
            .where(ReminderORM.id == reminder_id)
        )
        reminder_orm = self._session.execute(stmt).unique().scalar_one_or_none()
        if not reminder_orm:
            return None
        return self._to_domain(reminder_orm)

    def find_by_contact(self, contact_id: UUID) -> List[Reminder]:
        """Find all reminders for a contact.

        Args:
            contact_id: The contact's ID

        Returns:
            List of reminders for the contact
        """
        stmt = (
            select(ReminderORM)
            .options(selectinload(ReminderORM.contact), selectinload(ReminderORM.note))
            .where(ReminderORM.contact_id == contact_id)
        )
        reminders_orm = self._session.execute(stmt).unique().scalars().all()
        return [self._to_domain(reminder) for reminder in reminders_orm]

    def find_by_note(self, note_id: UUID) -> List[Reminder]:
        """Find all reminders linked to a note.

        Args:
            note_id: The note's ID

        Returns:
            List of reminders linked to the note
        """
        stmt = (
            select(ReminderORM)
            .options(selectinload(ReminderORM.contact), selectinload(ReminderORM.note))
            .where(ReminderORM.note_id == note_id)
        )
        reminders_orm = self._session.execute(stmt).unique().scalars().all()
        return [self._to_domain(reminder) for reminder in reminders_orm]

    def find_pending(self) -> List[Reminder]:
        """Find all pending reminders.

        Returns:
            List of reminders in PENDING status
        """
        stmt = (
            select(ReminderORM)
            .options(selectinload(ReminderORM.contact), selectinload(ReminderORM.note))
            .where(ReminderORM.status == ReminderStatus.PENDING)
        )
        reminders_orm = self._session.execute(stmt).unique().scalars().all()
        return [self._to_domain(reminder) for reminder in reminders_orm]

    def find_overdue(self) -> List[Reminder]:
        """Find all overdue reminders.

        Returns:
            List of reminders past their due date
        """
        now = datetime.now(timezone.utc)
        stmt = (
            select(ReminderORM)
            .options(selectinload(ReminderORM.contact), selectinload(ReminderORM.note))
            .where(
                and_(
                    ReminderORM.status == ReminderStatus.PENDING,
                    ReminderORM.due_date < now,
                )
            )
        )
        reminders_orm = self._session.execute(stmt).unique().scalars().all()
        return [self._to_domain(reminder) for reminder in reminders_orm]

    def delete(self, reminder: Reminder) -> None:
        """Delete a reminder.

        Args:
            reminder: The reminder to delete
        """
        reminder_orm = self._session.get(ReminderORM, reminder.id)
        if reminder_orm:
            self._session.delete(reminder_orm)
            self._session.flush()

    def _to_domain(self, reminder_orm: ReminderORM) -> Reminder:
        """Convert ORM model to domain model.

        Args:
            reminder_orm: The ORM model to convert

        Returns:
            Domain model instance
        """
        # Create recurrence pattern if applicable
        recurrence_pattern = None
        if reminder_orm.recurrence_interval and reminder_orm.recurrence_unit:
            recurrence_pattern = RecurrencePattern(
                interval=reminder_orm.recurrence_interval,
                unit=reminder_orm.recurrence_unit,
                end_date=reminder_orm.recurrence_end_date,
                start_date=reminder_orm.due_date
            )

        # Get the original timezone
        due_date_tz = ZoneInfo(reminder_orm.due_date_timezone)

        # Convert UTC datetime to original timezone using astimezone
        # This preserves the underlying timestamp during DST transitions
        due_date = reminder_orm.due_date.replace(tzinfo=timezone.utc).astimezone(due_date_tz)

        # Create reminder with base attributes
        reminder = Reminder(
            contact_id=reminder_orm.contact_id,
            title=reminder_orm.title,
            due_date=due_date,
            description=reminder_orm.description,
            recurrence_pattern=recurrence_pattern,
            note_id=reminder_orm.note_id,
        )

        # Set the ID after creation
        reminder.id = reminder_orm.id

        # Handle completion if reminder was completed
        if reminder_orm.status == ReminderStatus.COMPLETED and reminder_orm.completion_date:
            completion_tz = reminder_orm.completion_date_timezone
            if completion_tz is not None:  # Handle the Optional[str] type
                completion_date_tz = ZoneInfo(completion_tz)
                completion_date = reminder_orm.completion_date.replace(tzinfo=timezone.utc).astimezone(completion_date_tz)
                reminder.complete(completion_date)
        elif reminder_orm.status == ReminderStatus.CANCELLED:
            reminder.cancel()

        return reminder

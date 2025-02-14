"""SQLAlchemy implementation of the reminder repository."""

from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy import select, and_
from sqlalchemy.orm import Session, selectinload

from ..domain.reminder import (
    Reminder,
    ReminderStatus,
    RecurrencePattern,
    RecurrenceUnit,
)
from ..orm.reminder import ReminderORM
from .interfaces import ReminderRepository


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
            due_date=reminder.due_date,
            status=reminder.status,
            completion_date=reminder.completion_date,
        )

        # Add recurrence pattern if present
        if reminder.recurrence_pattern:
            reminder_orm.recurrence_interval = reminder.recurrence_pattern.interval
            reminder_orm.recurrence_unit = reminder.recurrence_pattern.unit
            reminder_orm.recurrence_end_date = reminder.recurrence_pattern.end_date

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
            The domain model
        """
        # Create recurrence pattern if present
        recurrence_pattern = None
        if (
            reminder_orm.recurrence_interval is not None
            and reminder_orm.recurrence_unit is not None
        ):
            recurrence_pattern = RecurrencePattern(
                interval=reminder_orm.recurrence_interval,
                unit=reminder_orm.recurrence_unit,
                end_date=reminder_orm.recurrence_end_date,
            )

        # Create domain model
        reminder = Reminder(
            contact_id=reminder_orm.contact_id,
            title=reminder_orm.title,
            due_date=reminder_orm.due_date,
            description=reminder_orm.description,
            recurrence_pattern=recurrence_pattern,
            note_id=reminder_orm.note_id,
        )
        reminder.id = reminder_orm.id

        # Set status and completion date if completed
        if (
            reminder_orm.status == ReminderStatus.COMPLETED
            and reminder_orm.completion_date
        ):
            reminder.complete(reminder_orm.completion_date)
        elif reminder_orm.status == ReminderStatus.CANCELLED:
            reminder.cancel()

        return reminder

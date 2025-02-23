"""SQLAlchemy ORM model for reminders."""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Integer, Enum, CheckConstraint

from ...database import Base
from ..domain.reminder_model import ReminderStatus, RecurrenceUnit
from .base_orm import GUID, UTCDateTime


class ReminderORM(Base):
    """ORM model for storing reminders in the database."""

    __tablename__ = "reminders"

    # Primary key and relationships
    id: Mapped[UUID] = mapped_column(GUID, primary_key=True, default=uuid4)
    contact_id: Mapped[UUID] = mapped_column(ForeignKey("contacts.id"), nullable=False)
    note_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("notes.id"), nullable=True
    )

    # Basic fields
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    due_date: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False)
    status: Mapped[str] = mapped_column(
        Enum(ReminderStatus), nullable=False, default=ReminderStatus.PENDING
    )
    completion_date: Mapped[Optional[datetime]] = mapped_column(
        UTCDateTime, nullable=True
    )

    # Recurrence fields
    recurrence_interval: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    recurrence_unit: Mapped[Optional[str]] = mapped_column(
        Enum(RecurrenceUnit), nullable=True
    )
    recurrence_end_date: Mapped[Optional[datetime]] = mapped_column(
        UTCDateTime, nullable=True
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    contact: Mapped["ContactORM"] = relationship(  # type: ignore
        "ContactORM", back_populates="reminders", lazy="joined"
    )
    note: Mapped[Optional["NoteORM"]] = relationship(  # type: ignore
        "NoteORM", back_populates="reminders", lazy="joined"
    )

    # Constraints
    __table_args__ = (
        # Ensure recurrence fields are all set or all null
        CheckConstraint(
            """
            (recurrence_interval IS NULL AND recurrence_unit IS NULL)
            OR
            (recurrence_interval IS NOT NULL AND recurrence_unit IS NOT NULL)
            """,
            name="valid_recurrence",
        ),
        # Ensure completion_date is only set for completed reminders
        CheckConstraint(
            """
            (status != 'COMPLETED' AND completion_date IS NULL)
            OR
            (status = 'COMPLETED' AND completion_date IS NOT NULL)
            """,
            name="valid_completion",
        ),
        # Ensure recurrence_interval is positive
        CheckConstraint(
            "recurrence_interval IS NULL OR recurrence_interval > 0",
            name="positive_interval",
        ),
        # Ensure recurrence_end_date is after due_date if set
        CheckConstraint(
            "recurrence_end_date IS NULL OR recurrence_end_date > due_date",
            name="valid_end_date",
        ),
    )

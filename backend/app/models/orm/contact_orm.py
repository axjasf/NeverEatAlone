"""SQLAlchemy ORM model for contacts."""

from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, JSON
from .base_orm import BaseORMModel, UTCDateTime
from .tag_orm import TagORM
from .note_orm import NoteORM
from .reminder_orm import ReminderORM
from .contact_tag_orm import contact_tags


class ContactORM(BaseORMModel):
    """ORM model for storing contact information in the database.

    All datetime fields are stored in UTC timezone.
    Timezone-aware datetimes are required for input and output.
    """

    __tablename__ = "contacts"

    name: Mapped[str] = mapped_column(String, nullable=False)
    first_name: Mapped[str] = mapped_column(String, nullable=True)
    briefing_text: Mapped[str] = mapped_column(String, nullable=True)
    sub_information: Mapped[Dict[str, Any]] = mapped_column(
        JSON, nullable=True, default=dict
    )
    # All datetime fields use UTCDateTime to enforce timezone awareness
    last_contact: Mapped[Optional[datetime]] = mapped_column(
        UTCDateTime,
        nullable=True,
        comment="Stored in UTC timezone"
    )
    contact_briefing_text: Mapped[Optional[str]] = mapped_column(
        String, nullable=True
    )

    # Relationships
    notes: Mapped[List[NoteORM]] = relationship(
        NoteORM,
        back_populates="contact",
        cascade="all, delete-orphan",  # Notes are owned by the contact
        lazy="joined",
    )
    # Tags exist independently, no cascade
    tags: Mapped[List[TagORM]] = relationship(
        TagORM, secondary=contact_tags, lazy="joined"
    )
    # Reminders are owned by the contact
    reminders: Mapped[List[ReminderORM]] = relationship(
        ReminderORM,
        back_populates="contact",
        cascade="all, delete-orphan",
        lazy="joined",
    )

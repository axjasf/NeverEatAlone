"""SQLAlchemy ORM model for contacts."""

from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, JSON, DateTime
from .base import BaseORMModel
from .tag import TagORM
from .note import NoteORM
from .reminder import ReminderORM
from .contact_tag import contact_tags


class ContactORM(BaseORMModel):
    """ORM model for storing contact information in the database."""

    __tablename__ = "contacts"

    name: Mapped[str] = mapped_column(String, nullable=False)
    first_name: Mapped[str] = mapped_column(String, nullable=True)
    briefing_text: Mapped[str] = mapped_column(String, nullable=True)
    sub_information: Mapped[Dict[str, Any]] = mapped_column(
        JSON, nullable=True, default=dict
    )
    last_contact: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    contact_briefing_text: Mapped[Optional[str]] = mapped_column(String, nullable=True)

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

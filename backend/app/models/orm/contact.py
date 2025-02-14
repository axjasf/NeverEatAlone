"""SQLAlchemy ORM model for contacts."""

from typing import Dict, Any, List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, JSON
from .base import BaseORMModel
from .tag import TagORM
from .note import NoteORM
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

    # Relationships
    notes: Mapped[List[NoteORM]] = relationship(  # type: ignore
        NoteORM,
        back_populates="contact",
        cascade="all, delete-orphan",  # Notes are owned by the contact
        lazy="joined",
    )
    # Tags exist independently, no cascade
    tags: Mapped[List[TagORM]] = relationship(
        TagORM, secondary=contact_tags, lazy="joined"
    )

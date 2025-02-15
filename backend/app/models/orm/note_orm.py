"""SQLAlchemy ORM model for notes."""

from datetime import datetime, timezone
from typing import List, TYPE_CHECKING
from uuid import UUID, uuid4
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Text, ForeignKey
from ...database import Base
from .statement_orm import StatementORM
from .tag_orm import TagORM
from .reminder_orm import ReminderORM

if TYPE_CHECKING:
    from .contact_orm import ContactORM


class NoteORM(Base):
    """ORM model for storing notes in the database."""

    __tablename__ = "notes"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    contact_id: Mapped[UUID] = mapped_column(ForeignKey("contacts.id"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    contact: Mapped["ContactORM"] = relationship(
        "ContactORM", back_populates="notes", lazy="joined"
    )
    statements: Mapped[List[StatementORM]] = relationship(
        StatementORM,
        back_populates="note",
        cascade="all, delete-orphan",
        lazy="joined",
        order_by="StatementORM.sequence_number",
    )
    tags: Mapped[List[TagORM]] = relationship(
        TagORM, secondary="note_tags", lazy="joined"
    )
    # Reminders referencing this note
    reminders: Mapped[List[ReminderORM]] = relationship(
        ReminderORM,
        back_populates="note",
        lazy="joined",
    )

    def set_tags(self, tag_names: List[str]) -> None:
        """Set the tags for this note.

        Args:
            tag_names: List of tag names to set
        """
        from ..domain.tag_model import EntityType

        # Clear existing tags
        self.tags = []
        # Add new tags
        for name in tag_names:
            tag = TagORM(
                entity_id=self.id, entity_type=EntityType.NOTE.value, name=name.lower()
            )
            self.tags.append(tag)

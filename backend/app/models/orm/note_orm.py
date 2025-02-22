"""SQLAlchemy ORM model for notes."""

from datetime import datetime, timezone
from typing import List, Optional, TYPE_CHECKING, Any
from uuid import UUID, uuid4
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Text, ForeignKey, Boolean, CheckConstraint, event
from ...database import Base
from .statement_orm import StatementORM
from .tag_orm import TagORM
from .reminder_orm import ReminderORM
from .base_orm import UTCDateTime, GUID
from .association_tables_orm import note_tags

if TYPE_CHECKING:
    from .contact_orm import ContactORM


class NoteORM(Base):
    """ORM model for storing notes in the database."""

    __tablename__ = "notes"

    id: Mapped[UUID] = mapped_column(GUID, primary_key=True, default=uuid4)
    contact_id: Mapped[UUID] = mapped_column(ForeignKey("contacts.id"), nullable=False)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_interaction: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    interaction_date: Mapped[Optional[datetime]] = mapped_column(
        UTCDateTime, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
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
        TagORM, secondary=note_tags, lazy="joined"
    )
    # Reminders referencing this note
    reminders: Mapped[List[ReminderORM]] = relationship(
        ReminderORM,
        back_populates="note",
        lazy="joined",
    )

    # Constraints
    __table_args__ = (
        # Interaction notes must have date, content notes must have content
        CheckConstraint(
            """
            (is_interaction = TRUE AND interaction_date IS NOT NULL) OR
            (is_interaction = FALSE AND content IS NOT NULL)
            """,
            name="valid_note_type"
        ),
        # Content notes cannot have interaction date
        CheckConstraint(
            """
            (is_interaction = TRUE) OR
            (is_interaction = FALSE AND interaction_date IS NULL)
            """,
            name="valid_content_note"
        ),
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

    @classmethod
    def __declare_last__(cls) -> None:
        """Set up event listeners after all mappings are configured."""
        @event.listens_for(cls.tags, 'append')
        def receive_append(target: "NoteORM", _: Any, _2: Any) -> None:
            """Update note timestamp when a tag is added."""
            target.updated_at = datetime.now(timezone.utc)

        @event.listens_for(cls.tags, 'remove')
        def receive_remove(target: "NoteORM", _: Any, _2: Any) -> None:
            """Update note timestamp when a tag is removed."""
            target.updated_at = datetime.now(timezone.utc)

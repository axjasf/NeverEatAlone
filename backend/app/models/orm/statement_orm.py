"""SQLAlchemy ORM model for statements."""

from typing import List
from uuid import UUID, uuid4
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Text, ForeignKey, Integer
from ...database import Base
from .tag_orm import TagORM


class StatementORM(Base):
    """ORM model for storing note statements in the database."""

    __tablename__ = "statements"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    note_id: Mapped[UUID] = mapped_column(ForeignKey("notes.id"), nullable=False)
    sequence_number: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationships
    note: Mapped["NoteORM"] = relationship(  # type: ignore
        "NoteORM", back_populates="statements", lazy="joined"
    )
    tags: Mapped[List[TagORM]] = relationship(
        TagORM, secondary="statement_tags", lazy="joined"
    )

    def set_tags(self, tag_names: List[str]) -> None:
        """Set the tags for this statement.

        Args:
            tag_names: List of tag names to set
        """
        from ..domain.tag_model import EntityType

        # Clear existing tags
        self.tags = []
        # Add new tags
        for name in tag_names:
            tag = TagORM(
                entity_id=self.id,
                entity_type=EntityType.STATEMENT.value,
                name=name.lower(),
            )
            self.tags.append(tag)

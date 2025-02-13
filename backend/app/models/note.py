from typing import List, Optional
from sqlalchemy import String, ForeignKey, and_
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .base import BaseModel
from .tag import Tag, EntityType
from backend.app.database import Base
import uuid


class Statement(Base, BaseModel):
    """Model for storing individual statements from notes.

    Each note can be broken down into multiple statements for finer-grained
    tracking and tagging.
    """
    __tablename__ = "statements"

    note_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("notes.id"), nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)

    # Relationship with tags - no cascade, tags exist independently
    tags: Mapped[List[Tag]] = relationship(
        Tag,
        primaryjoin=lambda: and_(
            Statement.id == Tag.entity_id,
            Tag.entity_type == EntityType.STATEMENT.value
        ),
        foreign_keys=[Tag.entity_id],
        overlaps="tags",
        lazy="joined"
    )

    def __init__(self, note_id: uuid.UUID, content: str) -> None:
        """Initialize a new Statement.

        Args:
            note_id: ID of the note this statement belongs to
            content: The statement content
        """
        super().__init__()
        self.note_id = note_id
        self.content = content

    def set_tags(self, tag_names: List[str]) -> None:
        """Set the tags for this statement.

        Args:
            tag_names: List of tag names to set. Each must start with '#'.

        Raises:
            ValueError: If any tag name doesn't start with '#'.
        """
        # Validate tag format
        for name in tag_names:
            if not name.startswith("#"):
                raise ValueError("Each tag must be a string starting with #")

        # Convert names to lowercase for case-insensitive matching
        tag_names = [name.lower() for name in tag_names]

        # Create new tags
        self.tags = [
            Tag(
                entity_id=uuid.UUID(str(self.id)),
                entity_type=EntityType.STATEMENT,
                name=name
            )
            for name in tag_names
        ]


class Note(Base, BaseModel):
    """Model for storing notes about contacts.

    Each note is associated with a contact and can have multiple statements.
    Notes can also be tagged for better organization.

    Attributes:
        contact_id (UUID): ID of the contact this note is about
        content (str): The note content
        tags (List[Tag]): Tags associated with this note
        statements (List[Statement]): Individual statements in this note
    """
    __tablename__ = "notes"

    contact_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("contacts.id"), nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)

    # Relationships
    contact: Mapped["Contact"] = relationship(
        "Contact",
        back_populates="notes",
        lazy="joined"
    )
    statements: Mapped[List[Statement]] = relationship(
        Statement,
        cascade="all, delete-orphan",  # Statements are owned by the note
        lazy="joined",
        order_by=Statement.id
    )
    # Tags exist independently, no cascade
    tags: Mapped[List[Tag]] = relationship(
        Tag,
        primaryjoin=lambda: and_(
            Note.id == Tag.entity_id,
            Tag.entity_type == EntityType.NOTE.value
        ),
        foreign_keys=[Tag.entity_id],
        overlaps="tags",
        lazy="joined"
    )

    def __init__(self, contact_id: uuid.UUID, content: str) -> None:
        """Initialize a new Note.

        Args:
            contact_id: ID of the contact this note is about
            content: The note content
        """
        super().__init__()
        self.contact_id = contact_id
        self.content = content

    def set_tags(self, tag_names: List[str]) -> None:
        """Set the tags for this note.

        Args:
            tag_names: List of tag names to set. Each must start with '#'.

        Raises:
            ValueError: If any tag name doesn't start with '#'.
        """
        # Validate tag format
        for name in tag_names:
            if not name.startswith("#"):
                raise ValueError("Each tag must be a string starting with #")

        # Convert names to lowercase for case-insensitive matching
        tag_names = [name.lower() for name in tag_names]

        # Create new tags
        self.tags = [
            Tag(
                entity_id=uuid.UUID(str(self.id)),
                entity_type=EntityType.NOTE,
                name=name
            )
            for name in tag_names
        ]

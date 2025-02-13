from datetime import datetime, UTC
from typing import List
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship, Mapped
from .base import BaseModel, Base, GUID
from .contact import Contact, Tag, EntityType
import uuid


class Statement(BaseModel):
    """Model for storing individual statements from notes.

    Each note can be broken down into multiple statements for finer-grained
    tracking and tagging.
    """
    __tablename__ = "statements"

    note_id: Mapped[uuid.UUID] = Column(GUID, ForeignKey("notes.id"), nullable=False)
    content: Mapped[str] = Column(String, nullable=False)

    # Relationship with tags
    tags: Mapped[List[Tag]] = relationship(
        "Tag",
        primaryjoin=(
            "and_(Statement.id == Tag.entity_id, "
            "Tag.entity_type == 'statement')"
        ),
        cascade="all, delete-orphan",
        lazy="joined",
        foreign_keys=[Tag.entity_id],
        overlaps="tags"
    )

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
                entity_id=self.id,
                entity_type=EntityType.STATEMENT,
                name=name
            )
            for name in tag_names
        ]


class Note(BaseModel):
    """Model for storing contact notes.

    Notes capture interactions and information about contacts. They can be
    broken down into statements for more granular tracking.

    Attributes:
        contact_id: ID of the contact this note is about
        content: The full text content of the note
        statements: Individual statements extracted from the note
        tags: Tags associated with the entire note
    """
    __tablename__ = "notes"

    contact_id: Mapped[uuid.UUID] = Column(GUID, ForeignKey("contacts.id"), nullable=False)
    content: Mapped[str] = Column(String, nullable=False)

    # Relationships
    contact: Mapped[Contact] = relationship("Contact", back_populates="notes")
    statements: Mapped[List[Statement]] = relationship(
        "Statement",
        cascade="all, delete-orphan",
        lazy="joined"
    )
    tags: Mapped[List[Tag]] = relationship(
        "Tag",
        primaryjoin=(
            "and_(Note.id == Tag.entity_id, "
            "Tag.entity_type == 'note')"
        ),
        cascade="all, delete-orphan",
        lazy="joined",
        foreign_keys=[Tag.entity_id],
        overlaps="tags"
    )

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
                entity_id=self.id,
                entity_type=EntityType.NOTE,
                name=name
            )
            for name in tag_names
        ]

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, JSON, and_
from .base import BaseModel
from .tag import Tag, EntityType
from backend.app.database import Base
import uuid


class Contact(Base, BaseModel):
    """Model for storing contact information.

    A contact represents a person or entity that we want to keep in touch with.
    Each contact can have basic information like name and additional data stored
    in a flexible JSON structure.

    Attributes:
        name (str): The contact's name
        first_name (str): The contact's first name
        briefing_text (str): A brief description of the contact
        sub_information (Dict[str, Any]): Additional information about the contact
        notes (List[Note]): Notes about this contact
        tags (List[Tag]): Tags associated with this contact
    """
    __tablename__ = "contacts"

    name: Mapped[str] = mapped_column(String, nullable=False)
    first_name: Mapped[str] = mapped_column(String, nullable=True)
    briefing_text: Mapped[str] = mapped_column(String, nullable=True)
    sub_information: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=True, default=dict)

    # Relationships
    notes: Mapped[List["Note"]] = relationship(
        "Note",
        back_populates="contact",
        cascade="all, delete-orphan",  # Notes are owned by the contact
        lazy="joined"
    )
    # Tags exist independently, no cascade
    tags: Mapped[List[Tag]] = relationship(
        Tag,
        primaryjoin=lambda: and_(
            Contact.id == Tag.entity_id,
            Tag.entity_type == EntityType.CONTACT.value
        ),
        foreign_keys=[Tag.entity_id],
        lazy="joined"
    )

    def __init__(
        self,
        name: str,
        first_name: Optional[str] = None,
        briefing_text: Optional[str] = None,
        sub_information: Optional[Dict[str, Any]] = None
    ) -> None:
        """Initialize a new Contact.

        Args:
            name: The contact's name
            first_name: The contact's first name (optional)
            briefing_text: A brief description of the contact (optional)
            sub_information: Additional information about the contact (optional)
        """
        super().__init__()
        self.name = name
        self.first_name = first_name
        self.briefing_text = briefing_text
        self.sub_information = sub_information or {}

    def set_tags(self, tag_names: List[str]) -> None:
        """Set the tags for this contact.

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
                entity_type=EntityType.CONTACT,
                name=name
            )
            for name in tag_names
        ]

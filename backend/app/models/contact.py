from typing import Dict, Any, List
from sqlalchemy.orm import Mapped, mapped_column, relationship, foreign, remote
from sqlalchemy import String, JSON
from .base import BaseModel
from .tag import Tag, EntityType
import uuid


class Contact(BaseModel):
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
        primaryjoin=(
            "and_(foreign(Contact.id) == remote(Tag.entity_id), "
            "Tag.entity_type == 'contact')"
        ),
        lazy="joined"
    )

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
            Tag(entity_id=uuid.UUID(str(self.id)), entity_type=EntityType.CONTACT, name=name)
            for name in tag_names
        ]

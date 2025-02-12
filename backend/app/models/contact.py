from typing import Any, Dict, List, cast, Optional
from datetime import datetime, UTC
from sqlalchemy import Column, String, JSON, DateTime, Enum, Integer
from sqlalchemy.orm import relationship, Mapped
import sqlalchemy as sa
from enum import Enum as PyEnum
from .base import BaseModel, Base, GUID
import uuid


class EntityType(str, PyEnum):
    """Types of entities that can have tags."""
    CONTACT = "contact"
    NOTE = "note"
    STATEMENT = "statement"


class Tag(Base):
    """Model for storing tags.

    Each tag is tied to a specific entity (contact, note, or statement).
    The name must start with '#' and is stored in lowercase for case-insensitive matching.
    The entity_type field tracks what type of entity this tag is used with.

    Attributes:
        entity_id (UUID): ID of the entity this tag belongs to
        entity_type (EntityType): Type of entity this tag is used with
        name (str): The tag name (must start with '#')
        frequency_days (Optional[int]): Days between expected contacts
        last_contact (Optional[datetime]): When this tag was last contacted
    """
    __tablename__ = "tags"

    entity_id: Mapped[uuid.UUID] = Column(GUID, primary_key=True)
    entity_type: Mapped[EntityType] = Column(Enum(EntityType), primary_key=True)
    name: Mapped[str] = Column(String, primary_key=True)
    frequency_days: Mapped[Optional[int]] = Column(Integer, nullable=True)
    last_contact: Mapped[Optional[datetime]] = Column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))

    def __init__(self, entity_id: uuid.UUID, entity_type: EntityType, name: str) -> None:
        """Create a new tag.

        Args:
            entity_id: ID of the entity this tag belongs to
            entity_type: Type of entity this tag is used with
            name: The tag name (must start with '#')

        Raises:
            ValueError: If name doesn't start with '#'
        """
        if not name.startswith("#"):
            raise ValueError("Tag must start with '#'")
        super().__init__()
        self.entity_id = entity_id
        self.entity_type = entity_type
        self.name = name.lower()  # Store in lowercase for case-insensitive matching
        self.frequency_days = None
        self.last_contact = None

    def set_frequency(self, days: int) -> None:
        """Set the contact frequency for this tag.

        Args:
            days: Number of days between expected contacts (1-365)

        Raises:
            ValueError: If frequency is invalid
        """
        if not 1 <= days <= 365:
            raise ValueError("Frequency must be between 1 and 365 days")
        self.frequency_days = days

    def update_last_contact(self, contact_date: Optional[datetime] = None) -> None:
        """Update the last contact date.

        Args:
            contact_date: The contact date to set, defaults to now
        """
        self.last_contact = contact_date or datetime.now(UTC)

    def disable_frequency(self) -> None:
        """Disable frequency tracking for this tag."""
        self.frequency_days = None
        self.last_contact = None

    @property
    def staleness_days(self) -> Optional[int]:
        """Calculate how many days overdue this tag is.

        Returns:
            Optional[int]: Number of days overdue, or None if frequency not set
        """
        if not self.frequency_days or not self.last_contact:
            return None

        # Ensure last_contact is timezone-aware
        last_contact = self.last_contact if self.last_contact.tzinfo else self.last_contact.replace(tzinfo=UTC)
        days_since = (datetime.now(UTC) - last_contact).days
        overdue_days = days_since - self.frequency_days
        return max(0, overdue_days)

    def is_stale(self) -> bool:
        """Check if this tag is overdue for contact.

        Returns:
            bool: True if tag has frequency set and is overdue
        """
        if not self.frequency_days or not self.last_contact:
            return False
        staleness = self.staleness_days
        return staleness > 0 if staleness is not None else False


class Contact(BaseModel):
    """Contact model for storing contact information.

    This model represents a contact in the system, storing both required and
    optional information about the contact. It supports flexible additional
    information through a JSON field and categorization via tags.

    Attributes:
        name (str): Required. The full name of the contact.
        first_name (Optional[str]): Optional. The contact's first name.
        briefing_text (Optional[str]): Optional. Brief notes about the contact.
        sub_information (Dict[str, Any]): Additional structured information
            stored as JSON. Defaults to empty dict.
        tags (List[Tag]): List of tags for categorization.
    """

    __tablename__ = "contacts"

    _name: Mapped[str] = Column("name", String, nullable=False)
    _first_name: Mapped[Optional[str]] = Column("first_name", String, nullable=True)
    _briefing_text: Mapped[Optional[str]] = Column("briefing_text", String, nullable=True)
    _sub_information: Mapped[Dict[str, Any]] = Column("sub_information", JSON, nullable=False, default=dict)

    # Relationship with tags
    tags: Mapped[List[Tag]] = relationship(
        "Tag",
        primaryjoin="and_(Contact.id == Tag.entity_id, Tag.entity_type == 'contact')",
        cascade="all, delete-orphan",
        lazy="joined",
        foreign_keys=[Tag.entity_id]
    )

    @property
    def name(self) -> str:
        """The full name of the contact.

        Returns:
            str: The contact's full name, or empty string if not set.
        """
        val = getattr(self, "_name", None)
        return str(val) if val is not None else ""

    @name.setter
    def name(self, value: str) -> None:
        """Set the contact's full name.

        Args:
            value (str): The full name to set.
        """
        self._name = value

    @property
    def first_name(self) -> Optional[str]:
        """The contact's first name.

        Returns:
            Optional[str]: The contact's first name, or None if not set.
        """
        val = getattr(self, "_first_name", None)
        return str(val) if val is not None else None

    @first_name.setter
    def first_name(self, value: Optional[str]) -> None:
        """Set the contact's first name.

        Args:
            value (Optional[str]): The first name to set, or None to unset.
        """
        self._first_name = value

    @property
    def briefing_text(self) -> Optional[str]:
        """Brief notes about the contact.

        Returns:
            Optional[str]: The briefing text, or None if not set.
        """
        val = getattr(self, "_briefing_text", None)
        return str(val) if val is not None else None

    @briefing_text.setter
    def briefing_text(self, value: Optional[str]) -> None:
        """Set the contact briefing text.

        Args:
            value (Optional[str]): The briefing text to set, or None to unset.
        """
        self._briefing_text = value

    @property
    def sub_information(self) -> Dict[str, Any]:
        """Additional structured information about the contact.

        This field can store any JSON-serializable data structure, allowing
        for flexible storage of contact-related information.

        Returns:
            Dict[str, Any]: The stored information, or empty dict if not set.
        """
        val = getattr(self, "_sub_information", {})
        return cast(Dict[str, Any], val)

    @sub_information.setter
    def sub_information(self, value: Dict[str, Any]) -> None:
        """Set additional information about the contact.

        Args:
            value (Dict[str, Any]): The information to store. Must be
                JSON-serializable.

        Raises:
            ValueError: If value is not a dictionary.
        """
        if not isinstance(value, dict):  # type: ignore
            raise ValueError("sub_information must be a dictionary")
        self._sub_information = value

    def set_tags(self, tag_names: List[str]) -> None:
        """Set the tags for this contact.

        This method creates new tag entities for each tag name and associates
        them with this contact. It also removes any existing tag associations
        that are not in the new list.

        Args:
            tag_names: List of tag names to set. Each must start with '#'.

        Raises:
            ValueError: If any tag name doesn't start with '#'.
            RuntimeError: If contact is not attached to a session.
        """
        # Validate tag format
        for name in tag_names:
            if not name.startswith("#"):
                raise ValueError("Each tag must be a string starting with #")

        # Convert names to lowercase for case-insensitive matching
        tag_names = [name.lower() for name in tag_names]

        # Create new tags
        self.tags = [
            Tag(entity_id=self.id, entity_type=EntityType.CONTACT, name=name)
            for name in tag_names
        ]

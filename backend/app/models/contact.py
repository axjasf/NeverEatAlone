from typing import Any, Dict, List, cast, Optional, Sequence
from datetime import datetime, UTC
from sqlalchemy import Column, String, JSON, DateTime, Table, ForeignKey, Enum
from sqlalchemy.orm import relationship, Session, Mapped
import sqlalchemy as sa
from enum import Enum as PyEnum
from .base import BaseModel, Base, GUID
import uuid


class EntityType(str, PyEnum):
    """Types of entities that can have hashtags."""
    CONTACT = "contact"
    NOTE = "note"
    # Add more entity types as needed


# Association table for contact-hashtag relationship
contact_hashtags = Table(
    "contact_hashtags",
    Base.metadata,
    Column("contact_id", GUID, ForeignKey("contacts.id"), primary_key=True),
    Column("hashtag_id", GUID, ForeignKey("hashtags.id"), primary_key=True),
)


class Hashtag(Base):
    """Model for storing hashtags.

    Each hashtag is stored once and can be associated with multiple entities.
    The name must start with '#' and is stored in lowercase for case-insensitive matching.
    The entity_type field tracks what type of entity this hashtag is used with.
    """
    __tablename__ = "hashtags"

    id: Mapped[uuid.UUID] = Column(GUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = Column(String, nullable=False)
    entity_type: Mapped[EntityType] = Column(Enum(EntityType), nullable=False)

    # Enforce uniqueness on combination of name and entity_type
    __table_args__ = (
        sa.UniqueConstraint('name', 'entity_type', name='uq_hashtag_name_type'),
    )

    def __init__(self, name: str, entity_type: EntityType) -> None:
        """Create a new hashtag.

        Args:
            name: The hashtag name (must start with '#')
            entity_type: The type of entity this hashtag is used with

        Raises:
            ValueError: If name doesn't start with '#'
        """
        if not name.startswith("#"):
            raise ValueError("Hashtag must start with '#'")
        super().__init__()
        self.name = name.lower()  # Store in lowercase for case-insensitive matching
        self.entity_type = entity_type


class Contact(BaseModel):
    """Contact model for storing contact information.

    This model represents a contact in the system, storing both required and
    optional information about the contact. It supports flexible additional
    information through a JSON field and categorization via hashtags.

    Attributes:
        name (str): Required. The full name of the contact.
        first_name (Optional[str]): Optional. The contact's first name.
        contact_briefing_text (Optional[str]): Optional. Brief notes about
            the contact.
        last_contact (Optional[datetime]): Last contact date in UTC.
        sub_information (Dict[str, Any]): Additional structured information
            stored as JSON. Defaults to empty dict.
        hashtags (List[str]): List of hashtags for categorization. Each tag
            must start with '#'. Defaults to empty list.

    Example:
        >>> contact = Contact(
        ...     name="John Doe",
        ...     first_name="John",
        ...     contact_briefing_text="Met at conference",
        ...     sub_information={"role": "Developer"},
        ...     hashtags=["#tech", "#conference"]
        ... )
    """

    __tablename__ = "contacts"

    _name: Mapped[str] = Column("name", String, nullable=False)
    _first_name: Mapped[Optional[str]] = Column("first_name", String, nullable=True)
    _contact_briefing_text: Mapped[Optional[str]] = Column("contact_briefing_text", String, nullable=True)
    _last_contact: Mapped[Optional[datetime]] = Column("last_contact", DateTime(timezone=True), nullable=True)
    _sub_information: Mapped[Dict[str, Any]] = Column("sub_information", JSON, nullable=False, default=dict)
    _hashtags: Mapped[List[str]] = Column("hashtags", JSON, nullable=False, default=list)

    # Relationship with hashtags
    hashtags: Mapped[List[Hashtag]] = relationship(
        "Hashtag",
        secondary=contact_hashtags,
        lazy="joined"
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
    def contact_briefing_text(self) -> Optional[str]:
        """Brief notes about the contact.

        Returns:
            Optional[str]: The briefing text, or None if not set.
        """
        val = getattr(self, "_contact_briefing_text", None)
        return str(val) if val is not None else None

    @contact_briefing_text.setter
    def contact_briefing_text(self, value: Optional[str]) -> None:
        """Set the contact briefing text.

        Args:
            value (Optional[str]): The briefing text to set, or None to unset.
        """
        self._contact_briefing_text = value

    @property
    def last_contact(self) -> Optional[datetime]:
        """The date of last contact with this person.

        Returns:
            Optional[datetime]: The last contact date in UTC,
            or None if not set.
        """
        val = getattr(self, "_last_contact", None)
        if val is not None and val.tzinfo is None:
            val = val.replace(tzinfo=UTC)
        return val

    @last_contact.setter
    def last_contact(self, value: Optional[datetime]) -> None:
        """Set the last contact date.

        Args:
            value (Optional[datetime]): The date to set in UTC,
            or None to unset.
        """
        if value is not None and value.tzinfo is None:
            value = value.replace(tzinfo=UTC)
        self._last_contact = value

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

    @property
    def hashtag_names(self) -> List[str]:
        """Get the list of hashtag names associated with this contact.

        Returns:
            List[str]: List of hashtag names (e.g., ["#work", "#tech"]).
        """
        return [tag.name for tag in self.hashtags]

    def set_hashtags(self, hashtag_names: List[str]) -> None:
        """Set the hashtags for this contact.

        This method creates new hashtag entities if they don't exist and
        associates them with this contact. It also removes any existing
        hashtag associations that are not in the new list.

        Args:
            hashtag_names: List of hashtag names to set. Each must start with '#'.

        Raises:
            ValueError: If any hashtag name doesn't start with '#'.
            RuntimeError: If contact is not attached to a session.
        """
        # Validate hashtag format
        for name in hashtag_names:
            if not name.startswith("#"):
                raise ValueError("Each hashtag must be a string starting with #")

        # Get SQLAlchemy session
        session = sa.inspect(self).session
        if session is None:
            raise RuntimeError(
                "Contact must be attached to a session to set hashtags"
            )

        # Clear existing hashtags
        self.hashtags = []

        # Create or get hashtags and associate them
        for name in hashtag_names:
            # Normalize name to lowercase
            name = name.lower()

            # Try to find existing hashtag
            hashtag = session.query(Hashtag).filter(
                Hashtag.name == name,
                Hashtag.entity_type == EntityType.CONTACT
            ).first()

            # Create new hashtag if it doesn't exist
            if hashtag is None:
                hashtag = Hashtag(name=name, entity_type=EntityType.CONTACT)
                session.add(hashtag)

            # Associate hashtag with contact
            self.hashtags.append(hashtag)

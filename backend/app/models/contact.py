from typing import Any, Dict, List, cast, Optional
from datetime import datetime, UTC, timedelta
from sqlalchemy import Column, String, JSON, DateTime, Table, ForeignKey, Enum, Integer
from sqlalchemy.orm import relationship, Session, Mapped
import sqlalchemy as sa
from enum import Enum as PyEnum
from .base import BaseModel, Base, GUID
import uuid


class EntityType(str, PyEnum):
    """Types of entities that can have hashtags."""
    CONTACT = "contact"
    NOTE = "note"
    STATEMENT = "statement"
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

    Attributes:
        name (str): The hashtag name (must start with '#')
        entity_type (EntityType): The type of entity this hashtag is used with
        frequency_days (Optional[int]): Number of days between expected contacts
        last_contact (Optional[datetime]): When this tag was last contacted
    """
    __tablename__ = "hashtags"

    id: Mapped[uuid.UUID] = Column(GUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = Column(String, nullable=False)
    entity_type: Mapped[EntityType] = Column(Enum(EntityType), nullable=False)
    frequency_days: Mapped[Optional[int]] = Column(Integer, nullable=True)
    last_contact: Mapped[Optional[datetime]] = Column(DateTime(timezone=True), nullable=True)

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
        return self.staleness_days > 0


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

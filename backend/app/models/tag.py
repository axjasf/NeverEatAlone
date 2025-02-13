# Minimal implementation to make tests pass
from enum import Enum as PyEnum
import uuid
from datetime import datetime, timezone
from typing import Optional


class EntityType(str, PyEnum):
    """Types of entities that can have tags."""
    CONTACT = "contact"
    NOTE = "note"
    STATEMENT = "statement"


class Tag:
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
        if len(name) <= 1:
            raise ValueError("Tag name must not be empty after '#'")

        self.entity_id = entity_id
        self.entity_type = entity_type
        self.name = self._normalize_name(name)
        self.frequency_days: Optional[int] = None
        self.last_contact: Optional[datetime] = None

    @staticmethod
    def _normalize_name(name: str) -> str:
        """Normalize tag name to lowercase.

        Args:
            name: Tag name to normalize

        Returns:
            Normalized tag name
        """
        return name.lower()

    def update_last_contact(self, timestamp: Optional[datetime] = None) -> None:
        """Update the last contact timestamp.

        Args:
            timestamp: Specific timestamp to set, or None to use current time
        """
        self.last_contact = timestamp if timestamp is not None else datetime.now(timezone.utc)

    def set_frequency(self, days: Optional[int]) -> None:
        """Set the frequency for this tag.

        Args:
            days: Number of days between expected contacts, or None to disable

        Raises:
            ValueError: If days is not between 1 and 365
        """
        if days is not None and (days < 1 or days > 365):
            raise ValueError("Frequency must be between 1 and 365 days")
        self.frequency_days = days

    def disable_frequency(self) -> None:
        """Disable frequency tracking for this tag."""
        self.frequency_days = None
        self.last_contact = None

    def is_stale(self) -> bool:
        """Check if this tag is stale based on frequency and last contact.

        Returns:
            True if contact is overdue based on frequency, False otherwise
        """
        if not self.frequency_days or not self.last_contact:
            return False

        # Ensure last_contact is timezone-aware
        if self.last_contact.tzinfo is None:
            self.last_contact = self.last_contact.replace(tzinfo=timezone.utc)

        time_since_contact = datetime.now(timezone.utc) - self.last_contact
        return bool(time_since_contact.days > self.frequency_days)

    @property
    def staleness_days(self) -> Optional[int]:
        """Get the number of days this tag is overdue.

        Returns:
            Number of days overdue, or None if not stale or no frequency set
        """
        if not self.frequency_days or not self.last_contact:
            return None

        # Ensure last_contact is timezone-aware
        if self.last_contact.tzinfo is None:
            self.last_contact = self.last_contact.replace(tzinfo=timezone.utc)

        time_since_contact = datetime.now(timezone.utc) - self.last_contact
        days_overdue = time_since_contact.days - self.frequency_days
        return days_overdue if days_overdue > 0 else None

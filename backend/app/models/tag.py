"""Tag domain model."""
from datetime import datetime, timezone
from enum import Enum as PyEnum
from typing import Optional
from uuid import UUID
import re
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime, ForeignKey, CheckConstraint
from .base import BaseModel
from backend.app.database import Base


class EntityType(str, PyEnum):
    """Types of entities that can have tags.

    Represents the hierarchical structure:
    - Contacts are the primary entity
    - Notes belong to contacts
    - Statements belong to notes
    All can have tags for categorization and reminders.
    """
    CONTACT = "contact"
    NOTE = "note"
    STATEMENT = "statement"


class Tag(Base, BaseModel):
    """Model for storing tags.

    Each tag is tied to a specific entity (contact, note, or statement) and can
    optionally track contact frequency for reminders.

    A tag is uniquely identified by the combination of:
    - entity_id: What it's attached to
    - entity_type: What kind of thing it's attached to
    - name: The tag text itself

    Attributes:
        entity_id: ID of the entity this tag belongs to
        entity_type: Type of entity this tag is used with
        name: The tag name (must start with '#')
        frequency_days: Optional number of days between expected contacts
        last_contact: When the entity was last contacted
    """
    __tablename__ = "tags"

    # Foreign key constraints for each entity type
    entity_id: Mapped[UUID] = mapped_column(nullable=False)
    entity_type: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    frequency_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    last_contact: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Add check constraint to ensure entity_type is valid
    __table_args__ = (
        CheckConstraint(
            entity_type.in_([e.value for e in EntityType]),
            name="valid_entity_type"
        ),
    )

    @staticmethod
    def get_current_time() -> datetime:
        """Get the current time.

        This method exists to make testing easier by allowing time to be mocked.

        Returns:
            datetime: Current time in UTC
        """
        return datetime.now(timezone.utc)

    def __init__(
        self,
        entity_id: UUID,
        entity_type: EntityType,
        name: str
    ) -> None:
        """Create a new tag.

        Args:
            entity_id: ID of the entity this tag belongs to
            entity_type: Type of entity this tag is used with
            name: The tag name (must start with '#')

        Raises:
            ValueError: If tag name is invalid
        """
        if not name.startswith('#'):
            raise ValueError("Tag name must start with '#'")
        if len(name) <= 1:
            raise ValueError("Tag name cannot be empty")
        if not re.match(r'^#[\w]+$', name):
            raise ValueError("Tag name can only contain letters, numbers, and underscores")

        super().__init__()
        self.entity_id = entity_id
        self.entity_type = entity_type.value
        self.name = name.lower()
        self.frequency_days = None
        self.last_contact = None

    def update_last_contact(self, timestamp: Optional[datetime] = None) -> None:
        """Update the last contact timestamp.

        Args:
            timestamp: Specific timestamp to set, or None to use current time
        """
        self.last_contact = timestamp if timestamp is not None else Tag.get_current_time()

    def set_frequency(self, days: Optional[int]) -> None:
        """Set the frequency for this tag.

        Args:
            days: Number of days between expected contacts, or None to disable

        Raises:
            ValueError: If days is not between 1 and 365
        """
        if days is not None:
            if not (1 <= days <= 365):
                raise ValueError("Frequency must be between 1 and 365 days")
            # Set last_contact to now when enabling frequency
            self.update_last_contact()
        else:
            # Clear last_contact when disabling frequency
            self.last_contact = None

        self.frequency_days = days

    def is_stale(self) -> bool:
        """Check if this tag is stale based on frequency and last contact.

        Returns:
            True if contact is overdue based on frequency, False otherwise
        """
        if not self.frequency_days or not self.last_contact:
            return False

        time_since_contact = self.get_current_time() - self.last_contact
        return time_since_contact.days > self.frequency_days

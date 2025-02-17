"""Tag domain model."""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import UUID
import re
from .base_model import BaseModel


class EntityType(str, Enum):
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


class Tag(BaseModel):
    """Model for storing tags.

    Each tag is tied to a specific entity (contact, note, or statement) and can
    optionally track contact frequency for reminders.

    A tag is uniquely identified by the combination of:
    - entity_id: What it's attached to
    - entity_type: What kind of thing it's attached to
    - name: The tag text itself

    Attributes:
        id: Unique identifier for this tag instance
        entity_id: ID of the entity this tag belongs to
        entity_type: Type of entity this tag is used with
        name: The tag name (must start with '#')
        frequency_days: Optional number of days between expected contacts
        last_contact: When the entity was last contacted
    """

    def __init__(self, entity_id: UUID, entity_type: EntityType, name: str) -> None:
        """Create a new tag.

        Args:
            entity_id: ID of the entity this tag belongs to
            entity_type: Type of entity this tag is used with
            name: The tag name (must start with '#')

        Raises:
            ValueError: If tag name is invalid
        """
        super().__init__()
        if not name.startswith("#"):
            raise ValueError("Tag name must start with '#'")
        if len(name) <= 1:
            raise ValueError("Tag name cannot be empty")
        if not re.match(r"^#[\w]+$", name):
            raise ValueError(
                "Tag name can only contain letters, numbers, and underscores"
            )

        self.entity_id = entity_id
        self.entity_type = entity_type.value
        self.name = name.lower()
        self.frequency_days: Optional[int] = None
        self.last_contact: Optional[datetime] = None

    @staticmethod
    def get_current_time() -> datetime:
        """Get the current time.

        This method exists to make testing easier by allowing time to be mocked.

        Returns:
            datetime: Current time in UTC
        """
        return datetime.now(timezone.utc)

    def update_last_contact(self, timestamp: Optional[datetime] = None) -> None:
        """Update the last contact timestamp.

        Args:
            timestamp: Specific timestamp to set, or None to use current time
        """
        self.last_contact = (
            timestamp if timestamp is not None else Tag.get_current_time()
        )

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

    def handle_note_interaction(self, is_interaction: bool, interaction_date: Optional[datetime] = None) -> None:
        """Handle a note being marked as an interaction.

        This method should be called when a note with this tag is created or updated.
        It will update the last_contact timestamp for contact tags.

        Args:
            is_interaction: Whether the note represents an interaction
            interaction_date: When the interaction occurred (required if is_interaction is True)
        """
        # Only update last_contact for contact tags
        if self.entity_type != EntityType.CONTACT.value:
            return

        # Update last_contact if this is an interaction
        if is_interaction and interaction_date:
            self.update_last_contact(interaction_date)

# Minimal implementation to make tests pass
from enum import Enum as PyEnum
import uuid


class EntityType(str, PyEnum):
    """Types of entities that can have tags."""
    CONTACT = "contact"
    NOTE = "note"
    STATEMENT = "statement"


class Tag:
    """Model for storing tags.

    Each tag is tied to a specific entity (contact, note, or statement).
    """
    def __init__(
        self,
        entity_id: uuid.UUID,
        entity_type: EntityType,
        name: str
    ) -> None:
        """Create a new tag.

        Args:
            entity_id: ID of the entity this tag belongs to
            entity_type: Type of entity this tag is used with
            name: The tag name (must start with '#')
        """
        self.entity_id = entity_id
        self.entity_type = entity_type
        self.name = name

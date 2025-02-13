# Minimal implementation to make tests pass
from enum import Enum as PyEnum
import uuid
from datetime import datetime, timezone
from typing import Optional, cast
from sqlalchemy import Column, String, Enum, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.types import TypeDecorator
from sqlalchemy.orm import validates
from backend.app.database import Base


class GUID(TypeDecorator):
    """Platform-independent GUID type.

    Uses PostgreSQL's UUID type, otherwise uses String(36).
    """
    impl = PGUUID
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PGUUID())
        else:
            return dialect.type_descriptor(String(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return str(uuid.UUID(value))
            return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(value)
            return value


class EntityType(str, PyEnum):
    """Types of entities that can have tags."""
    CONTACT = "contact"
    NOTE = "note"
    STATEMENT = "statement"


class Tag(Base):
    """Model for storing tags.

    Each tag is tied to a specific entity (contact, note, or statement).
    """
    __tablename__ = "tags"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    entity_id = Column(GUID(), nullable=False)
    entity_type = Column(Enum(EntityType), nullable=False)
    name = Column(String, nullable=False)
    frequency_days = Column(Integer, nullable=True)  # e.g., 7 for weekly
    last_contact = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

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
        super().__init__()
        self.entity_id = entity_id
        self.entity_type = entity_type
        self.name = self._normalize_name(name)

    @validates('name')
    def validate_name(self, key: str, name: str) -> str:
        """Validate and normalize tag name.

        Args:
            key: Field name being validated
            name: Tag name to validate

        Returns:
            Normalized tag name

        Raises:
            ValueError: If tag name is invalid
        """
        if not name.startswith('#'):
            raise ValueError("Tag name must start with '#'")
        if len(name) <= 1:
            raise ValueError("Tag name must not be empty after '#'")
        return self._normalize_name(name)

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
        freq_days = cast(Optional[int], self.frequency_days)
        last_contact = cast(Optional[datetime], self.last_contact)

        if not freq_days or not last_contact:
            return False

        # Ensure last_contact is timezone-aware
        if last_contact.tzinfo is None:
            last_contact = last_contact.replace(tzinfo=timezone.utc)

        time_since_contact = datetime.now(timezone.utc) - last_contact
        return bool(time_since_contact.days > freq_days)

    @property
    def staleness_days(self) -> Optional[int]:
        """Get the number of days this tag is overdue.

        Returns:
            Number of days overdue, or None if not stale or no frequency set
        """
        freq_days = cast(Optional[int], self.frequency_days)
        last_contact = cast(Optional[datetime], self.last_contact)

        if not freq_days or not last_contact:
            return None

        # Ensure last_contact is timezone-aware
        if last_contact.tzinfo is None:
            last_contact = last_contact.replace(tzinfo=timezone.utc)

        time_since_contact = datetime.now(timezone.utc) - last_contact
        days_overdue = time_since_contact.days - freq_days
        return days_overdue if days_overdue > 0 else None

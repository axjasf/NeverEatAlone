"""SQLAlchemy ORM model for tags."""

from datetime import datetime, UTC
from typing import Optional, Any
from uuid import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, CheckConstraint, event
from ..domain.tag_model import EntityType
from .base_orm import BaseORMModel, GUID, UTCDateTime


class TagORM(BaseORMModel):
    """ORM model for storing tags in the database."""

    __tablename__ = "tags"

    entity_id: Mapped[UUID] = mapped_column(GUID, nullable=False)
    entity_type: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    frequency_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    frequency_last_updated: Mapped[Optional[datetime]] = mapped_column(
        UTCDateTime, nullable=True
    )
    last_contact: Mapped[Optional[datetime]] = mapped_column(
        UTCDateTime, nullable=True
    )

    # Add check constraint to ensure entity_type is valid and name is not empty
    __table_args__ = (
        CheckConstraint(
            entity_type.in_([e.value for e in EntityType]), name="valid_entity_type"
        ),
        CheckConstraint(name != "", name="non_empty_name"),
    )

    def _ensure_timezone(self, dt: Optional[datetime]) -> Optional[datetime]:
        """Ensure a datetime is timezone-aware in UTC.

        Args:
            dt: The datetime to check

        Returns:
            The datetime in UTC if provided, None if input is None
        """
        if dt is None:
            return None
        if dt.tzinfo is None:
            return dt.replace(tzinfo=UTC)
        return dt.astimezone(UTC)

    def update_frequency(self, days: Optional[int]) -> None:
        """Update frequency_days and frequency_last_updated.

        Args:
            days: Number of days between expected contacts, or None to disable
        """
        self.frequency_days = days
        # Always update frequency_last_updated to track when frequency was changed
        self.frequency_last_updated = datetime.now(UTC)

    @classmethod
    def __declare_last__(cls) -> None:
        """Set up event listeners after all mappings are configured."""
        @event.listens_for(cls, 'load')
        def receive_load(target: "TagORM", _: Any) -> None:
            """Ensure timezone awareness when loading from database."""
            target.frequency_last_updated = target._ensure_timezone(target.frequency_last_updated)
            target.last_contact = target._ensure_timezone(target.last_contact)

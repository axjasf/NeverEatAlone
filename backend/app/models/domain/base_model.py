"""Base domain model."""

from abc import ABC
from datetime import datetime, timezone
from uuid import uuid4
from typing import Optional


class BaseModel(ABC):
    """Base class for all domain models.

    This class ensures that all datetime fields are timezone-aware and stored in UTC.
    When datetime values are provided without timezone information, a ValueError is raised.
    """

    def __init__(self, created_at: Optional[datetime] = None) -> None:
        """Initialize the base model.

        Args:
            created_at: Optional timezone-aware datetime for creation time.
                       If None, current UTC time is used.

        Raises:
            ValueError: If a naive datetime (without timezone) is provided.
        """
        self.id = uuid4()

        # Handle created_at
        if created_at is None:
            self.created_at = datetime.now(timezone.utc)
        else:
            if created_at.tzinfo is None:
                raise ValueError("created_at must be timezone-aware")
            self.created_at = created_at.astimezone(timezone.utc)

        # Initialize updated_at to same time as created_at
        self.updated_at = self.created_at

    def touch(self) -> None:
        """Update the updated_at timestamp to current UTC time."""
        self.updated_at = datetime.now(timezone.utc)

    # Alias for backward compatibility
    _update_timestamp = touch

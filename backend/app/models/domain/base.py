"""Base domain model."""

from abc import ABC
from datetime import datetime, UTC
from uuid import UUID, uuid4
from typing import Optional


class BaseModel(ABC):
    """Base class for all domain models."""

    def __init__(self, id: Optional[UUID] = None) -> None:
        """Initialize the base model.

        Args:
            id: Optional UUID for the model. If not provided, a new UUID will be generated.
        """
        self.id = id or uuid4()
        now = datetime.now(UTC)
        self.created_at = now
        self.updated_at = now

    def touch(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now(UTC)

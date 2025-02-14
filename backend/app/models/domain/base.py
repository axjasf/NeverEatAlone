"""Base domain model."""

from datetime import datetime, timezone
from uuid import UUID, uuid4


class BaseModel:
    """Base model class that includes common fields and methods.

    This class serves as the foundation for all domain models in
    the application. It provides common fields for tracking record
    creation and modification times, and a unique identifier.

    Attributes:
        id: Unique identifier for the model.
        created_at: Timestamp of when the record was created.
        updated_at: Timestamp of the last update.
    """

    def __init__(self) -> None:
        """Initialize base model with tracking fields."""
        self.id: UUID = uuid4()
        self.created_at: datetime = datetime.now(timezone.utc)
        self.updated_at: datetime = self.created_at

    def _update_timestamp(self) -> None:
        """Update the last modified timestamp."""
        self.updated_at = datetime.now(timezone.utc)

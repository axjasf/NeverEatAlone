"""Base ORM model."""

from datetime import datetime, timezone
from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import TypeDecorator
from typing import Any, Optional
import uuid
from ...database import Base


class GUID(TypeDecorator[uuid.UUID]):
    """Platform-independent GUID type.
    Uses String(36) internally for SQLite compatibility.
    """

    impl = String(36)
    cache_ok = True

    def process_bind_param(
        self, value: Optional[uuid.UUID | str], dialect: Any
    ) -> Optional[str]:
        """Process the value before binding to database."""
        return str(value) if value is not None else None

    def process_result_value(
        self, value: Optional[str], dialect: Any
    ) -> Optional[uuid.UUID]:
        """Process the value after retrieving from database."""
        if value is None:
            return value
        return uuid.UUID(value)


class BaseORMModel(Base):
    """Base model class that includes common fields and methods.

    This class serves as the foundation for all database models in
    the application. It provides common fields for tracking record
    creation and modification times, and a unique identifier.

    Attributes:
        id: Primary key column, UUID.
        created_at: Timestamp of when the record was created.
        updated_at: Timestamp of the last update.
    """

    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

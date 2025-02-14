"""Base ORM model."""
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, String
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
        self,
        value: Optional[uuid.UUID | str],
        dialect: Any
    ) -> Optional[str]:
        if value is None:
            return value
        elif isinstance(value, str):
            return value
        else:
            return str(value)

    def process_result_value(
        self,
        value: Optional[str],
        dialect: Any
    ) -> Optional[uuid.UUID]:
        if value is None:
            return value
        else:
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

    id = Column(
        GUID,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

"""SQLAlchemy ORM model for tags."""
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime, CheckConstraint
from ...database import Base
from ..domain.tag import EntityType


class TagORM(Base):
    """ORM model for storing tags in the database."""
    __tablename__ = "tags"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    entity_id: Mapped[UUID] = mapped_column(nullable=False)
    entity_type: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    frequency_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    last_contact: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    # Add check constraint to ensure entity_type is valid
    __table_args__ = (
        CheckConstraint(
            entity_type.in_([e.value for e in EntityType]),
            name="valid_entity_type"
        ),
    )

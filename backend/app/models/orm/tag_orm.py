"""SQLAlchemy ORM model for tags."""

from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime, CheckConstraint
from ..domain.tag_model import EntityType
from .base_orm import BaseORMModel


class TagORM(BaseORMModel):
    """ORM model for storing tags in the database."""

    __tablename__ = "tags"

    entity_id: Mapped[UUID] = mapped_column(nullable=False)
    entity_type: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    frequency_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    last_contact: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Add check constraint to ensure entity_type is valid
    __table_args__ = (
        CheckConstraint(
            entity_type.in_([e.value for e in EntityType]), name="valid_entity_type"
        ),
    )

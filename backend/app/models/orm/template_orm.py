"""SQLAlchemy ORM model for templates."""

from datetime import datetime
from typing import Any, Dict
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import JSON, Integer, PrimaryKeyConstraint
from .base_orm import BaseORMModel, GUID, UTCDateTime
import uuid


class TemplateVersionORM(BaseORMModel):
    """ORM model for storing template versions in the database."""

    __tablename__ = "template_versions"

    # Override id to not be a primary key
    id: Mapped[uuid.UUID] = mapped_column(GUID, nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    categories: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    removed_fields: Mapped[Dict[str, Any]] = mapped_column(
        JSON, nullable=False, default=dict
    )
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime, nullable=False
    )

    __table_args__ = (
        # Make id and version together the primary key
        PrimaryKeyConstraint("id", "version", name="pk_template_version"),
    )

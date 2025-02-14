"""SQLAlchemy ORM model for statement-tag associations."""

from sqlalchemy import Table, Column, ForeignKey
from ...database import Base


statement_tags = Table(
    "statement_tags",
    Base.metadata,
    Column("statement_id", ForeignKey("statements.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)

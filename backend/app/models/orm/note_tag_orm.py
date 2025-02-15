"""SQLAlchemy ORM model for note-tag associations."""

from sqlalchemy import Table, Column, ForeignKey
from ...database import Base


note_tags = Table(
    "note_tags",
    Base.metadata,
    Column("note_id", ForeignKey("notes.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)

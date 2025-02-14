"""SQLAlchemy ORM model for contact-tag associations."""

from sqlalchemy import Table, Column, ForeignKey
from ...database import Base


contact_tags = Table(
    "contact_tags",
    Base.metadata,
    Column("contact_id", ForeignKey("contacts.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)

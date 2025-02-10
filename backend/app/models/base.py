from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, DateTime
from datetime import datetime, UTC


Base = declarative_base()


class BaseModel(Base):
    """Base model class that includes common fields and methods.

    This class serves as the foundation for all database models in the application.
    It provides common fields for tracking record creation and modification times,
    as well as a unique identifier.

    Attributes:
        id (Column): Primary key column, auto-incrementing integer.
        created_at (Column): Timestamp of when the record was created, auto-set.
        updated_at (Column): Timestamp of the last update, auto-updated.
    """

    __abstract__ = True

    id = Column(Integer, primary_key=True)
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        nullable=False
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False
    )

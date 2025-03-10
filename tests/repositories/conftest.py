"""Test configuration for repository tests."""

import pytest
import logging
from typing import Generator
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.engine import Engine
from backend.app.database import Base

# Import all models to ensure they are registered with SQLAlchemy
from backend.app.models.domain.note_model import Note  # noqa: F401
from backend.app.models.domain.tag_model import Tag  # noqa: F401
from backend.app.models.orm.note_orm import NoteORM  # noqa: F401
from backend.app.models.orm.tag_orm import TagORM  # noqa: F401
from backend.app.models.orm.contact_orm import ContactORM  # noqa: F401
from backend.app.models.orm.reminder_orm import ReminderORM  # noqa: F401
from backend.app.models.orm.template_orm import TemplateVersionORM  # noqa: F401

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def engine() -> Engine:
    """Create a SQLite test database engine."""
    engine = create_engine(
        "sqlite:///:memory:",
        echo=True,
        # Explicitly set connection pooling
        pool_pre_ping=True,
        pool_recycle=3600,
        # Ensure proper transaction isolation
        isolation_level="SERIALIZABLE",
    )
    logger.info("Creating database tables...")
    Base.metadata.create_all(engine)

    # Log created tables
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    logger.info(f"Created tables: {tables}")

    return engine


@pytest.fixture
def db_session(engine: Engine) -> Generator[Session, None, None]:
    """Create a new database session for a test."""
    connection = engine.connect()
    # Begin a non-ORM transaction
    transaction = connection.begin()

    # Create session with the connection
    Session = sessionmaker(bind=connection)
    session = Session()

    try:
        yield session
    finally:
        # Ensure proper cleanup
        session.close()
        # Rollback the transaction
        transaction.rollback()
        # Close the connection
        connection.close()

"""Test configuration for model tests."""

import pytest
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.engine import Engine
from backend.app.database import Base

# These imports are needed to register models with SQLAlchemy
# even though they are not directly used in this file
from backend.app.models.domain.note_model import Note  # noqa: F401
from backend.app.models.domain.tag_model import Tag  # noqa: F401
from backend.app.models.orm.note_orm import NoteORM  # noqa: F401
from backend.app.models.orm.tag_orm import TagORM  # noqa: F401
from backend.app.models.orm.contact_orm import ContactORM  # noqa: F401
from backend.app.models.orm.reminder_orm import ReminderORM  # noqa: F401
from backend.app.models.orm.template_orm import TemplateVersionORM  # noqa: F401


@pytest.fixture(scope="session")
def engine() -> Engine:
    """Create a SQLite test database engine."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"detect_types": 3},  # Enable datetime type detection
        echo=True,
    )
    return engine


@pytest.fixture(scope="session")
def tables(engine: Engine) -> Generator[None, None, None]:
    """Create all tables in the test database."""
    Base.metadata.create_all(engine)  # Create tables before tests
    yield None
    Base.metadata.drop_all(engine)  # Drop tables after tests


@pytest.fixture
def db_session(engine: Engine, tables: None) -> Generator[Session, None, None]:
    """Create a new database session for a test."""
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(
        bind=connection,
        expire_on_commit=True,
        autoflush=True,
    )
    session = Session()

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()

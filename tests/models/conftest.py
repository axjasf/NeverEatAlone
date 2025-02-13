"""Test configuration for model tests."""
import pytest
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.engine import Engine
from backend.app.database import Base

# Import all models to ensure they are registered with SQLAlchemy
from backend.app.models.contact import Contact
from backend.app.models.note import Note
from backend.app.models.tag import Tag

@pytest.fixture(scope="session")
def engine() -> Engine:
    """Create a SQLite test database engine."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture(scope="session")
def tables(engine: Engine) -> Generator[None, None, None]:
    """Create all tables in the test database."""
    yield None


@pytest.fixture
def db_session(engine: Engine, tables: None) -> Generator[Session, None, None]:
    """Create a new database session for a test."""
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()

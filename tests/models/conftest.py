"""Test configuration for model tests."""
import pytest
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.engine import Engine
from backend.app.database import Base

# Import all models to ensure they are registered with SQLAlchemy
from backend.app.models.domain.contact import Contact  # noqa: F401
from backend.app.models.domain.note import Note  # noqa: F401
from backend.app.models.domain.tag import Tag  # noqa: F401



@pytest.fixture(scope="session")
def engine() -> Engine:
    """Create a SQLite test database engine."""
    engine = create_engine("sqlite:///:memory:")
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
    Session = sessionmaker(bind=connection)
    session = Session()

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()

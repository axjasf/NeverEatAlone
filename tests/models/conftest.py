import pytest
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.engine import Engine
from backend.app.models.base import Base


@pytest.fixture(scope="session")
def engine() -> Engine:
    """Create a SQLite in-memory database engine for testing."""
    return create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False}
    )


@pytest.fixture(scope="session")
def tables(engine: Engine) -> Generator[None, None, None]:
    """Create all tables in the test database."""
    Base.metadata.create_all(engine)
    yield None


@pytest.fixture
def db_session(engine: Engine, tables: None) -> Generator[Session, None, None]:
    """Create a new database session for a test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()

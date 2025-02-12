import pytest
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine, Connection
from sqlalchemy.engine.base import Transaction
from backend.app.models.base import Base
from fastapi.testclient import TestClient
from backend.app.main import app, override_get_db


@pytest.fixture(scope="session")
def engine() -> Engine:
    """Create a SQLite in-memory database engine for testing.

    This fixture creates a SQLite database in memory that persists for the
    entire test session. This ensures fast test execution while maintaining
    data isolation between test runs.

    Returns:
        Engine: SQLAlchemy engine instance connected to in-memory SQLite.
    """
    return create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}
    )


@pytest.fixture(scope="session")
def tables(engine: Engine) -> Generator[None, None, None]:
    """Create all tables in the test database.

    This fixture creates all database tables defined in the models. The
    tables persist for the entire test session but are dropped at the end.
    This ensures a clean state for each test session.

    Args:
        engine: The SQLAlchemy engine to use for creating tables.

    Yields:
        None: This fixture doesn't yield any value, it just manages tables.
    """
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_session(engine: Engine, tables: None) -> Generator[Session, None, None]:
    """Create a new database session for a test.

    This fixture provides a database session for each test, with automatic
    cleanup. It creates a transaction that is rolled back after the test,
    ensuring perfect isolation between tests.

    Args:
        engine: The SQLAlchemy engine to use.
        tables: The tables fixture (used for dependencies).

    Yields:
        Session: A SQLAlchemy session for database operations.
    """
    connection: Connection = engine.connect()
    transaction: Transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()

    yield session

    if session.is_active:
        session.rollback()
    session.close()
    if transaction.is_active:
        transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Create a test client for the FastAPI application with db session"""
    with override_get_db(db_session):
        yield TestClient(app)

"""Test configuration and fixtures.

This module provides common test fixtures for all tests.
"""

import pytest
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator, Callable

from app.models.orm.base_orm import Base

@pytest.fixture(scope="session")
def engine() -> Generator[Engine, None, None]:
    """Create a test database engine."""
    engine = create_engine("sqlite:///./test.db", echo=False)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)

@pytest.fixture(scope="session")
def session_factory(engine: Engine) -> Callable[[], Generator[Session, None, None]]:
    """Create a session factory for tests."""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def get_session() -> Generator[Session, None, None]:
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    return get_session

@pytest.fixture(scope="function")
def db_session(session_factory: Callable[[], Generator[Session, None, None]]) -> Generator[Session, None, None]:
    """Create a new database session for a test."""
    session = next(session_factory())
    try:
        yield session
    finally:
        session.rollback()
        session.close()

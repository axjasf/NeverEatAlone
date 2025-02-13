"""Test configuration for repository tests."""
import pytest
import logging
from typing import Generator
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.engine import Engine
from backend.app.database import Base

# Import all ORM models to ensure they are registered with SQLAlchemy
from backend.app.repositories.sqlalchemy.tag_repository import TagORM

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def engine() -> Engine:
    """Create a SQLite test database engine."""
    engine = create_engine("sqlite:///:memory:", echo=True)
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
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.rollback()
        session.close()

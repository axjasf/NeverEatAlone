"""Test configuration for service tests."""

import pytest
import logging
from typing import Callable
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.engine import Engine
from backend.app.database import Base

# Re-use the repository fixtures
from tests.repositories.conftest import engine  # noqa: F401

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture
def session_factory(engine: Engine) -> Callable[[], Session]:
    """Create a session factory for service tests.

    This fixture provides a factory function that creates new database sessions,
    which is what our services expect to receive.

    Returns:
        Callable[[], Session]: A factory function that creates new sessions
    """
    Session = sessionmaker(bind=engine)
    return Session

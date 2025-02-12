import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from backend.app.main import app, override_get_db
# Import only what we need from models conftest
from tests.models.conftest import db_session  # noqa: F401


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Create a FastAPI test client."""
    with override_get_db(db_session):
        with TestClient(app) as test_client:
            yield test_client

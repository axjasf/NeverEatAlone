# Re-export fixtures for backward compatibility
from tests.models.conftest import engine, tables, db_session  # noqa: F401

__all__ = ["engine", "tables", "db_session"]

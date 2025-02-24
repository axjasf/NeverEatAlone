"""Test suite for the BaseService class."""

import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from backend.app.services.base_service import BaseService, ServiceError

def test_transaction_context_commits_on_success() -> None:
    """Test that successful operations in transaction context are committed."""
    # Arrange
    session = MagicMock(spec=Session)
    session_factory = MagicMock(return_value=session)
    service = BaseService(session_factory)

    # Act
    with service.in_transaction() as tx_session:
        # Simulate some work
        tx_session.add(MagicMock())

    # Assert
    session.commit.assert_called_once()
    session.rollback.assert_not_called()

def test_transaction_context_rolls_back_on_error() -> None:
    """Test that failed operations in transaction context are rolled back."""
    # Arrange
    session = MagicMock(spec=Session)
    session_factory = MagicMock(return_value=session)
    service = BaseService(session_factory)

    # Act & Assert
    with pytest.raises(ServiceError) as exc_info:
        with service.in_transaction():
            # Simulate work that fails
            raise ValueError("Something went wrong")

    # Verify the error is wrapped properly
    assert isinstance(exc_info.value, ServiceError)
    assert "transaction" in str(exc_info.value)
    assert "Something went wrong" in str(exc_info.value)

    # Verify transaction handling
    session.commit.assert_not_called()
    session.rollback.assert_called_once()

def test_session_lifecycle() -> None:
    """Test that session is properly managed through the context manager."""
    # Arrange
    session = MagicMock(spec=Session)
    session_factory = MagicMock(return_value=session)
    service = BaseService(session_factory)

    # Act
    with service.in_transaction() as tx_session:
        assert tx_session == session  # Session is available inside context

    # Assert
    session_factory.assert_called_once()  # Session was created
    session.close.assert_called_once()    # Session was closed

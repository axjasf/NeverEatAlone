"""Test suite for the BaseService class."""

import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from backend.app.services.base_service import BaseService, ServiceError, TransactionError

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

def test_commit_failure_handling() -> None:
    """Test that commit failures are properly caught and reported."""
    # Arrange
    session = MagicMock(spec=Session)
    session.commit.side_effect = ValueError("Commit failed")
    session_factory = MagicMock(return_value=session)
    service = BaseService(session_factory)

    # Act & Assert
    with pytest.raises(TransactionError) as exc_info:
        with service.in_transaction() as tx_session:
            tx_session.add(MagicMock())  # Some work that should trigger commit

    # Verify error handling
    assert isinstance(exc_info.value, TransactionError)
    assert "commit" in str(exc_info.value)
    assert "Commit failed" in str(exc_info.value)

    # Verify transaction handling
    session.commit.assert_called_once()
    session.rollback.assert_called_once()  # Should attempt rollback after commit failure

def test_rollback_failure_handling() -> None:
    """Test that rollback failures are properly caught and reported."""
    # Arrange
    session = MagicMock(spec=Session)
    session.rollback.side_effect = ValueError("Rollback failed")
    session_factory = MagicMock(return_value=session)
    service = BaseService(session_factory)

    # Act & Assert
    with pytest.raises(TransactionError) as exc_info:
        with service.in_transaction():
            raise ValueError("Operation failed")  # Trigger rollback

    # Verify error handling
    assert isinstance(exc_info.value, TransactionError)
    assert "rollback" in str(exc_info.value)
    assert "Rollback failed" in str(exc_info.value)

    # Verify transaction handling
    session.commit.assert_not_called()
    session.rollback.assert_called_once()

def test_error_includes_timestamp() -> None:
    """Test that service errors include UTC timestamp."""
    # Arrange
    session = MagicMock(spec=Session)
    session_factory = MagicMock(return_value=session)
    service = BaseService(session_factory)
    before_error = datetime.now(timezone.utc)

    # Act
    with pytest.raises(ServiceError) as exc_info:
        with service.in_transaction():
            raise ValueError("Test error")

    # Assert
    error = exc_info.value
    assert hasattr(error, 'timestamp')
    assert isinstance(error.timestamp, datetime)
    assert error.timestamp.tzinfo == timezone.utc
    assert before_error <= error.timestamp <= datetime.now(timezone.utc)
    assert str(error).find(error.timestamp.isoformat()) > -1  # Timestamp in message

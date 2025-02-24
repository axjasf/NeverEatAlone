"""Base service layer implementation."""

import logging
from datetime import datetime, timezone
from contextlib import contextmanager
from typing import Generator, TypeVar, Any
from sqlalchemy.orm import Session

# Type variable for session type
SessionT = TypeVar('SessionT', bound=Session)

class ServiceError(Exception):
    """Base class for service layer errors."""

    def __init__(self, operation: str, original_error: Exception | None = None) -> None:
        """Initialize service error.

        Args:
            operation: The operation that failed
            original_error: The original exception that caused this error
        """
        self.operation = operation
        self.original_error = original_error
        self.timestamp = datetime.now(timezone.utc)
        message = f"Service operation '{operation}' failed at {self.timestamp.isoformat()}"
        if original_error:
            message += f": {str(original_error)}"
        super().__init__(message)

class TransactionError(ServiceError):
    """Error indicating a transaction failure."""
    pass

class ValidationError(ServiceError):
    """Error indicating a validation failure."""
    pass

class NotFoundError(ServiceError):
    """Error indicating a requested entity was not found."""
    pass

class BaseService:
    """Base class for all services providing common functionality."""

    def __init__(self, session_factory: Any) -> None:
        """Initialize the service.

        Args:
            session_factory: Factory function that creates database sessions
        """
        self.session_factory = session_factory
        self.logger = logging.getLogger(self.__class__.__name__)

    @contextmanager
    def in_transaction(self) -> Generator[Session, None, None]:
        """Provide a transactional scope around a series of operations.

        Yields:
            Session: The active database session for this transaction

        Raises:
            ServiceError: If any operation within the transaction fails
            TransactionError: If commit or rollback fails
        """
        session = self.session_factory()
        try:
            yield session
            try:
                session.commit()
            except Exception as e:
                self.logger.error("Failed to commit transaction", exc_info=True)
                try:
                    session.rollback()
                except Exception as rollback_error:
                    self.logger.error("Failed to rollback transaction", exc_info=True)
                    raise TransactionError("rollback", rollback_error) from e
                raise TransactionError("commit", e)
        except Exception as e:
            if not isinstance(e, TransactionError):
                self.logger.error("Transaction failed, rolling back", exc_info=True)
                try:
                    session.rollback()
                except Exception as rollback_error:
                    self.logger.error("Failed to rollback transaction", exc_info=True)
                    raise TransactionError("rollback", rollback_error) from e
                if isinstance(e, ServiceError):
                    raise
                raise ServiceError("transaction", e)
            raise
        finally:
            session.close()

# Base Service Design

## Purpose
Provides foundational patterns for all business services, handling transaction management, error handling, and common service operations in a single-user context.

## Core Features
✅ Implemented:
- Transaction context management
- Basic error handling with UTC timestamps
- Session lifecycle management
- Error type identification
- Nested error causation chain
- Stack trace preservation

⏸️ Parked (Issue #45):
- Structured logging
- Operation timing
- Complex error tracking
- Operation metadata
- Nested transactions

🔄 Future Considerations (Issue #45):
- Error retry patterns
- Complex error scenarios
- Error context enrichment

## Interface

### BaseService
```python
class BaseService:
    def __init__(self, session_factory: Any) -> None:
        """Initialize service with session factory"""
        self.session_factory = session_factory
        self.logger = logging.getLogger(self.__class__.__name__)

    @contextmanager
    def in_transaction(self) -> Generator[Session, None, None]:
        """Provide a transactional scope around a series of operations."""
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

    def handle_error(self, operation: str, error: Exception) -> ServiceError:
        """Standardized error handling with context"""
        self.logger.error(f"{operation} failed: {str(error)}")
        if isinstance(error, ServiceError):
            return error
        return ServiceError(operation=operation, original_error=error)

    def log_operation(self, operation: str, **context):
        """Basic operation logging"""
        self.logger.info(f"Operation: {operation}", extra=context)
```

### Error Types
```python
class ServiceError(Exception):
    """Base class for service layer errors."""
    def __init__(self, operation: str, original_error: Exception | None = None) -> None:
        self.operation = operation
        self.original_error = original_error
        self.timestamp = datetime.now(timezone.utc)

        # Build error message
        error_type = self.__class__.__name__
        formatted_time = self.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")
        message = f"{error_type} in operation '{operation}' at {formatted_time}"

        if original_error:
            # Add context for nested errors
            if isinstance(original_error, ServiceError):
                message += f"\nCaused by: {str(original_error)}"
            else:
                message += f"\nError: {str(original_error)}"

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
```

## Transaction Boundaries

### Operation Level
✅ Implemented:
- Each business operation gets its own transaction
- Automatic rollback on errors
- Proper resource cleanup
- Detailed error context

⏸️ Parked (Issue #45):
- Nested transactions
- Complex transaction patterns

### Multi-Entity Operations
Example (pending implementation):
```python
def create_contact_with_tags(self, data: dict, tags: list[str]) -> Contact:
    with self.in_transaction() as session:
        contact = Contact(**data)
        session.add(contact)
        for tag_name in tags:
            tag = Tag(name=tag_name, entity_id=contact.id)
            session.add(tag)
        return contact
```

## Error Handling

### Core Principles
1. **Clear Context** ✅
   - Error type always included
   - Operation name for quick identification
   - UTC timestamp for error tracking
   - Original error preserved in chain

2. **Error Categories** ✅
   - ServiceError: Base class for all service errors
   - TransactionError: Commit/rollback failures
   - ValidationError: Input validation failures
   - NotFoundError: Entity lookup failures

3. **Error Message Format** ✅
   ```
   {ErrorType} in operation '{operation}' at {YYYY-MM-DD HH:MM:SS UTC}
   [Caused by: {nested_service_error} | Error: {original_error}]
   ```

4. **Nested Error Handling** ✅
   ```
   ServiceError in operation 'outer_op' at 2025-02-24 14:30:00 UTC
   Caused by: ServiceError in operation 'inner_op' at 2025-02-24 14:29:59 UTC
   Error: Inner problem
   ```

5. **Logging Strategy**
✅ Implemented:
   - Error details logged automatically
   - Stack traces preserved
   - Operation context included
   - UTC timestamps for consistency

⏸️ Parked (Issue #45):
   - Structured logging
   - Operation timing
   - Detailed error tracking

## Testing Approach

### Transaction Tests ✅
```python
def test_transaction_context_commits_on_success() -> None:
    """Test that successful operations in transaction context are committed."""
    # Arrange
    session = MagicMock(spec=Session)
    session_factory = MagicMock(return_value=session)
    service = BaseService(session_factory)

    # Act
    with service.in_transaction() as tx_session:
        tx_session.add(MagicMock())

    # Assert
    session.commit.assert_called_once()
    session.rollback.assert_not_called()
```

### Error Handling Tests ✅
```python
def test_nested_service_error_formatting() -> None:
    """Test that nested service errors are properly formatted."""
    # Arrange
    inner_error = ServiceError("inner_op", ValueError("Inner problem"))
    outer_error = ServiceError("outer_op", inner_error)

    # Assert
    error_str = str(outer_error)
    assert "ServiceError in operation 'outer_op'" in error_str
    assert "Caused by: ServiceError in operation 'inner_op'" in error_str
    assert "Error: Inner problem" in error_str
```

### Timestamp Tests ✅
```python
def test_error_includes_timestamp() -> None:
    """Test that service errors include UTC timestamp."""
    # Arrange
    service = BaseService(MagicMock())
    before_error = datetime.now(timezone.utc)

    # Act
    with pytest.raises(ServiceError) as exc_info:
        with service.in_transaction():
            raise ValueError("Test error")

    # Assert
    error = exc_info.value
    assert hasattr(error, 'timestamp')
    assert error.timestamp.tzinfo == timezone.utc
    assert before_error <= error.timestamp <= datetime.now(timezone.utc)
```

## Usage Examples

### Basic Service (Pending Implementation)
```python
class ContactService(BaseService):
    def create_contact(self, data: dict) -> Contact:
        with self.in_transaction() as session:
            try:
                contact = Contact(**data)
                session.add(contact)
                return contact
            except Exception as e:
                raise ServiceError("create_contact", e)
```

### Complex Operation (Pending Implementation)
```python
class NoteService(BaseService):
    def create_note_with_statements(
        self,
        contact_id: UUID,
        content: str,
        statements: list[str]
    ) -> Note:
        with self.in_transaction() as session:
            try:
                contact = session.get(Contact, contact_id)
                if not contact:
                    raise NotFoundError("Contact not found")

                note = Note(contact_id=contact_id, content=content)
                session.add(note)

                for idx, statement_content in enumerate(statements):
                    statement = Statement(
                        note_id=note.id,
                        content=statement_content,
                        sequence_number=idx + 1
                    )
                    session.add(statement)

                return note
            except Exception as e:
                raise ServiceError("create_note_with_statements", e)
```

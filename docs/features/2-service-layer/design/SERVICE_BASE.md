# Base Service Design

## Purpose
Provides foundational patterns for all business services, handling transaction management, error handling, and common service operations in a single-user context.

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
                session.rollback()
                raise TransactionError("commit", e)
        except Exception as e:
            self.logger.error("Transaction failed, rolling back", exc_info=True)
            try:
                session.rollback()
            except Exception as rollback_error:
                self.logger.error("Failed to rollback transaction", exc_info=True)
                raise TransactionError("rollback", rollback_error) from e
            if isinstance(e, ServiceError):
                raise
            raise ServiceError("transaction", e)
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
        message = f"Service operation '{operation}' failed"
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
```

## Transaction Boundaries

### Operation Level
- Each business operation gets its own transaction
- Automatic rollback on errors
- Proper resource cleanup
- Detailed error context

### Multi-Entity Operations
- Single transaction spans multiple repositories
- All-or-nothing semantics
- Example:
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
1. **Clear Context**
   - Operation name always included
   - Original error preserved
   - Stack trace maintained

2. **Error Categories**
   - ServiceError: Base class for all service errors
   - TransactionError: Commit/rollback failures
   - ValidationError: Input validation failures
   - NotFoundError: Entity lookup failures

3. **Logging Strategy**
   - Error details logged automatically
   - Stack traces preserved
   - Operation context included

## Testing Approach

### Unit Tests
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

### Error Handling Tests
```python
def test_transaction_context_rolls_back_on_error() -> None:
    """Test that failed operations in transaction context are rolled back."""
    # Arrange
    session = MagicMock(spec=Session)
    session_factory = MagicMock(return_value=session)
    service = BaseService(session_factory)

    # Act & Assert
    with pytest.raises(ServiceError) as exc_info:
        with service.in_transaction():
            raise ValueError("Something went wrong")

    # Verify error wrapping
    assert isinstance(exc_info.value, ServiceError)
    assert "transaction" in str(exc_info.value)
    assert "Something went wrong" in str(exc_info.value)

    # Verify transaction handling
    session.commit.assert_not_called()
    session.rollback.assert_called_once()
```

## Usage Examples

### Basic Service
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

### Complex Operation
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

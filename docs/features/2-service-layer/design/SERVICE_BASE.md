# Base Service Design

## Purpose
Provides foundational patterns for all business services, handling transaction management, error handling, and common service operations in a single-user context.

## Interface

### BaseService
```python
class BaseService:
    def __init__(self, session_factory: SessionFactory):
        """Initialize service with session factory"""
        self.session_factory = session_factory
        self.logger = logging.getLogger(self.__class__.__name__)

    @contextmanager
    def in_transaction(self):
        """Context manager for transaction handling"""
        with self.session_factory() as session:
            try:
                yield session
                session.commit()
            except Exception as e:
                session.rollback()
                raise self.handle_error("transaction", e)

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
    """Base class for service layer errors"""
    def __init__(self, operation: str, original_error: Exception = None):
        self.operation = operation
        self.original_error = original_error
        super().__init__(f"Service operation '{operation}' failed: {str(original_error)}")

class ValidationError(ServiceError):
    """Validation errors in service operations"""
    pass

class TransactionError(ServiceError):
    """Transaction-related errors"""
    pass

class NotFoundError(ServiceError):
    """Entity not found errors"""
    pass
```

## Transaction Boundaries

### Operation Level
- Each business operation gets its own transaction
- Automatic rollback on errors
- Example:
```python
def create_contact(self, data: dict) -> Contact:
    with self.in_transaction() as session:
        contact = Contact(**data)
        session.add(contact)
        return contact
```

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
   - ValidationError: Input validation failures
   - TransactionError: Database operation failures
   - NotFoundError: Entity lookup failures
   - ServiceError: Generic service layer errors

3. **Logging Strategy**
   - Error details logged automatically
   - Operation context included
   - Stack traces preserved

## Testing Approach

### Unit Tests
```python
def test_transaction_rollback():
    """Test automatic rollback on error"""
    with pytest.raises(ServiceError):
        service.create_contact_with_tags(
            {"name": "John"},
            ["invalid#tag"]  # Will cause validation error
        )
    # Verify nothing was committed
    assert service.get_contact_count() == 0
```

### Integration Tests
```python
def test_multi_entity_transaction():
    """Test all-or-nothing semantics"""
    contact = service.create_contact_with_tags(
        {"name": "John"},
        ["#family", "#friend"]
    )
    assert contact.tags.count() == 2
    # Verify both contact and tags in single transaction
    assert contact.id is not None
    assert all(tag.id is not None for tag in contact.tags)
```

## Examples

### Basic Service
```python
class ContactService(BaseService):
    def __init__(self, session_factory: SessionFactory):
        super().__init__(session_factory)
        self.repository = ContactRepository()

    def create_contact(self, data: dict) -> Contact:
        with self.in_transaction() as session:
            try:
                contact = Contact(**data)
                self.repository.save(contact, session)
                self.log_operation("create_contact", contact_id=contact.id)
                return contact
            except Exception as e:
                raise self.handle_error("create_contact", e)
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
                # Verify contact exists
                contact = self.repository.get_by_id(contact_id, session)
                if not contact:
                    raise NotFoundError("Contact not found")

                # Create note with statements
                note = Note(contact_id=contact_id, content=content)
                self.repository.save(note, session)

                # Add statements in sequence
                for idx, statement_content in enumerate(statements):
                    statement = Statement(
                        note_id=note.id,
                        content=statement_content,
                        sequence_number=idx + 1
                    )
                    self.repository.save(statement, session)

                self.log_operation(
                    "create_note_with_statements",
                    note_id=note.id,
                    statement_count=len(statements)
                )
                return note
            except Exception as e:
                raise self.handle_error("create_note_with_statements", e)
```

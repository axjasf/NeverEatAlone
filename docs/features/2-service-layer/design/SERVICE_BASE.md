# Base Service Design

## Purpose
Provides foundational patterns for all business services, handling transaction management, error handling, and common service operations.

## Interface

### BaseService
```python
class BaseService:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    def in_transaction(self):
        """Context manager for transaction handling"""

    def handle_error(self, operation: str, error: Exception):
        """Standardized error handling with context"""
```

### Transaction Boundaries
- Each business operation gets its own transaction
- Nested transactions not supported initially
- Automatic rollback on errors

### Error Handling
- ServiceError base exception
- Operation context included
- Clear error messages for debugging

## Patterns Used
1. **Session Management**
   - Session per operation
   - Explicit transaction boundaries
   - Automatic cleanup

2. **Error Context**
   - Operation name
   - Input parameters
   - Error chain

3. **Logging**
   - Operation start/end
   - Error conditions
   - Performance data

## Examples
```python
class ContactService(BaseService):
    def create_with_tags(self, contact_data: dict, tags: list[str]):
        with self.in_transaction():
            try:
                contact = Contact(**contact_data)
                self.repository.save(contact)
                for tag in tags:
                    tag_obj = Tag(name=tag, entity_id=contact.id)
                    self.repository.save(tag_obj)
                return contact
            except Exception as e:
                self.handle_error("create_with_tags", e)
```

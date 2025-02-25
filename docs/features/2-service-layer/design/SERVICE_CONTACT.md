# Contact Service Design

## Purpose
Provides business operations for managing contacts and their associated data (tags, notes, interactions) in a consistent and transactional way.

## Core Features

### Contact Management
✅ Planned:
- Create contact with tags
- Update contact details
- Delete contact (with associated data)
- Get contact by ID
- Search contacts by criteria

⏸️ Future Considerations:
- Bulk operations
- Complex search patterns
- Contact merging

### Tag Operations
✅ Planned:
- Add tags to contact
- Remove tags from contact
- Update tag frequencies
- Get contacts by tag

⏸️ Future Considerations:
- Tag statistics
- Tag recommendations
- Automated tag cleanup

### Interaction Tracking
✅ Planned:
- Record interaction with note
- Update last contact timestamp
- Get interaction history

⏸️ Future Considerations:
- Interaction analytics
- Automated interaction suggestions
- Interaction templates

## Interface

### ContactService
```python
class ContactService(BaseService):
    def create_with_tags(
        self,
        contact_data: Dict[str, Any],
        tags: List[str]
    ) -> Contact:
        """Create a new contact with associated tags."""

    def update(
        self,
        contact_id: UUID,
        data: Dict[str, Any]
    ) -> Contact:
        """Update contact details."""

    def delete(self, contact_id: UUID) -> None:
        """Delete a contact and associated data."""

    def get_by_id(self, contact_id: UUID) -> Optional[Contact]:
        """Get a contact by ID."""

    def add_tags(
        self,
        contact_id: UUID,
        tags: List[str]
    ) -> Contact:
        """Add tags to a contact."""

    def remove_tags(
        self,
        contact_id: UUID,
        tags: List[str]
    ) -> Contact:
        """Remove tags from a contact."""

    def record_interaction(
        self,
        contact_id: UUID,
        date: datetime,
        note: Optional[str] = None
    ) -> Contact:
        """Record an interaction with a contact."""
```

## Transaction Boundaries

### Single-Entity Operations
✅ Planned:
- Each operation gets its own transaction
- Automatic rollback on errors
- Proper cleanup of resources

Example:
```python
def update(self, contact_id: UUID, data: Dict[str, Any]) -> Contact:
    with self.in_transaction() as session:
        contact = session.get(Contact, contact_id)
        if not contact:
            raise NotFoundError(f"Contact {contact_id} not found")
        for key, value in data.items():
            setattr(contact, key, value)
        return contact
```

### Multi-Entity Operations
✅ Planned:
- Atomic operations across related entities
- Consistent error handling
- Clear transaction boundaries

Example:
```python
def create_with_tags(
    self,
    contact_data: Dict[str, Any],
    tags: List[str]
) -> Contact:
    with self.in_transaction() as session:
        contact = Contact(**contact_data)
        session.add(contact)
        contact.set_hashtags(tags)
        return contact
```

## Error Handling

### Core Error Types
1. **NotFoundError**
   - Contact doesn't exist
   - Referenced entity missing

2. **ValidationError**
   - Invalid contact data
   - Invalid tag format
   - Future dates in interactions

3. **TransactionError**
   - Database operation failed
   - Rollback failed

### Error Scenarios
✅ Planned:
```python
# Not Found
contact = service.get_by_id(uuid4())
if not contact:
    raise NotFoundError("Contact not found")

# Validation
if interaction_date > datetime.now(UTC):
    raise ValidationError("Cannot record future interactions")

# Transaction
try:
    with self.in_transaction() as session:
        # ... operations ...
except Exception as e:
    raise ServiceError("operation_name", e)
```

## Testing Strategy

### Unit Tests
✅ Planned:
1. **Basic Operations**
   - Create contact with valid data
   - Update existing contact
   - Delete contact and verify cleanup

2. **Tag Operations**
   - Add valid tags
   - Remove existing tags
   - Handle invalid tag formats

3. **Interaction Recording**
   - Record valid interaction
   - Handle future dates
   - Update last contact time

4. **Error Cases**
   - Not found scenarios
   - Validation failures
   - Transaction rollbacks

### Integration Tests
✅ Planned:
1. **Data Persistence**
   - Verify saves across sessions
   - Check relationship handling
   - Test cascade deletes

2. **Transaction Integrity**
   - Verify atomic operations
   - Check rollback effectiveness
   - Test cleanup on errors

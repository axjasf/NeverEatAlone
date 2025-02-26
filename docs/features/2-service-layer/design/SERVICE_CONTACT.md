# Contact Service Design

## Purpose
Provides business operations for managing contacts and their associated data (tags, notes, interactions) in a consistent and transactional way.

## Core Features

### Contact Management
✅ Planned:
- Create contact with tags [FR1.1.1, FR1.1.2]
- Update contact details [FR1.1.3]
- Delete contact (with associated data) [FR1.3.2]
- Get contact by ID [FR1.3.1]
- Search contacts by criteria [FR1.3.3]
- Validate sub-information against template [FR1.2.1, FR1.2.2]

⏸️ Future Considerations:
- Bulk operations
- Complex search patterns
- Contact merging

### Tag Operations
✅ Planned:
- Add tags to contact [FR2.1.1, FR2.1.4]
- Remove tags from contact [FR2.1.3]
- Update tag frequencies [FR2.2.1, FR2.2.4]
- Search contacts by tag [FR1.3.3]
- Track tag frequencies [FR2.2.2, FR2.2.3]

⏸️ Future Considerations:
- Tag statistics
- Tag recommendations
- Automated tag cleanup

### Interaction Tracking
✅ Planned:
- Record interaction with note [FR1.1.4]
- Update last contact timestamp [FR1.1.5]
- Get interaction history [FR2.2.2]
- Track per-tag interactions [FR2.2.5, FR2.2.6]

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
        """Create a new contact with associated tags.

        Requirements: [FR1.1.1, FR1.1.2, FR2.1.1, FR2.1.4]

        Raises:
            ValidationError: If contact_data is invalid
            ServiceError: If creation fails
        """
        self.log_operation("create_with_tags", contact_data=contact_data, tags=tags)
        with self.in_transaction() as session:
            try:
                contact = Contact(**contact_data)
                session.add(contact)
                contact.set_hashtags(tags)
                return contact
            except Exception as e:
                raise self.handle_error("create_with_tags", e)

    def update(
        self,
        contact_id: UUID,
        data: Dict[str, Any]
    ) -> Contact:
        """Update contact details.

        Requirements: [FR1.1.3]

        Raises:
            ValidationError: If data is invalid
            NotFoundError: If contact doesn't exist
            ServiceError: If update fails
        """
        self.log_operation("update", contact_id=contact_id, data=data)
        with self.in_transaction() as session:
            try:
                contact = session.get(Contact, contact_id)
                if not contact:
                    raise NotFoundError(f"Contact {contact_id} not found")
                for key, value in data.items():
                    setattr(contact, key, value)
                return contact
            except Exception as e:
                raise self.handle_error("update", e)

    def delete(self, contact_id: UUID) -> None:
        """Delete a contact and associated data.

        Requirements: [FR1.3.2]
        - Must remove all contact information
        - Must remove all tag associations
        - Must remove all interaction records
        - Must remove all notes
        - Must preserve tag definitions if used by other contacts
        - Must handle non-existent contacts gracefully

        Raises:
            NotFoundError: If contact doesn't exist
            ServiceError: If deletion fails
        """
        self.log_operation("delete", contact_id=contact_id)
        with self.in_transaction() as session:
            try:
                contact = session.get(Contact, contact_id)
                if not contact:
                    raise NotFoundError(f"Contact {contact_id} not found")

                # Clean up related entities
                session.query(Interaction).filter_by(contact_id=contact_id).delete()
                session.query(Note).filter_by(contact_id=contact_id).delete()

                # Remove tag associations but preserve tags
                contact.tags.clear()
                session.delete(contact)
            except Exception as e:
                raise self.handle_error("delete", e)

    def get_by_id(self, contact_id: UUID) -> Optional[Contact]:
        """Get a contact by ID.

        Requirements: [FR1.3.1]

        Raises:
            ValidationError: If contact_id is invalid
            NotFoundError: If contact doesn't exist
        """
        self.log_operation("get_by_id", contact_id=contact_id)
        with self.in_transaction() as session:
            try:
                contact = session.get(Contact, contact_id)
                if not contact:
                    raise NotFoundError(f"Contact {contact_id} not found")
                return contact
            except Exception as e:
                raise self.handle_error("get_by_id", e)

    def search(
        self,
        criteria: Dict[str, Any],
        page: Optional[int] = None,
        page_size: Optional[int] = None
    ) -> List[Contact]:
        """Search contacts by criteria.

        Requirements: [FR1.3.3]

        Raises:
            ValidationError: If criteria or pagination params are invalid
        """
        self.log_operation("search", criteria=criteria, page=page, page_size=page_size)
        with self.in_transaction() as session:
            try:
                # Validate criteria
                if not isinstance(criteria.get('name', ''), str):
                    raise ValidationError("Name criteria must be a string")
                if page is not None and page < 1:
                    raise ValidationError("Page number must be positive")

                # Build query
                query = session.query(Contact)
                # ... query building logic ...

                return query.all()
            except Exception as e:
                raise self.handle_error("search", e)

    def add_tags(
        self,
        contact_id: UUID,
        tags: List[str]
    ) -> Contact:
        """Add tags to a contact.

        Requirements: [FR2.1.1, FR2.1.3, FR2.1.4]
        - Must normalize tags to lowercase
        - Must prevent duplicate tags
        - Must handle non-existent contacts gracefully

        Raises:
            ValidationError: If tags format is invalid
            NotFoundError: If contact doesn't exist
            ServiceError: If tag operation fails
        """
        self.log_operation("add_tags", contact_id=contact_id, tags=tags)
        with self.in_transaction() as session:
            try:
                contact = session.get(Contact, contact_id)
                if not contact:
                    raise NotFoundError(f"Contact {contact_id} not found")

                # Validate and normalize tags
                if not isinstance(tags, list):
                    raise ValidationError("Tags must be a list")
                normalized_tags = [tag.lower() for tag in tags]

                contact.add_hashtags(normalized_tags)
                return contact
            except Exception as e:
                raise self.handle_error("add_tags", e)

    def remove_tags(
        self,
        contact_id: UUID,
        tags: List[str]
    ) -> Contact:
        """Remove tags from a contact.

        Requirements: [FR2.1.3]

        Raises:
            ValidationError: If tags format is invalid
            NotFoundError: If contact doesn't exist
            ServiceError: If tag removal fails
        """
        self.log_operation("remove_tags", contact_id=contact_id, tags=tags)
        with self.in_transaction() as session:
            try:
                contact = session.get(Contact, contact_id)
                if not contact:
                    raise NotFoundError(f"Contact {contact_id} not found")

                # Validate tags
                if not isinstance(tags, list):
                    raise ValidationError("Tags must be a list")

                contact.remove_hashtags(tags)
                return contact
            except Exception as e:
                raise self.handle_error("remove_tags", e)

    def record_interaction(
        self,
        contact_id: UUID,
        date: datetime,
        note: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Contact:
        """Record an interaction with a contact.

        Requirements: [FR1.1.4, FR1.1.5, FR2.2.2, FR2.2.5, FR2.2.6]

        Raises:
            ValidationError: If date is invalid or in future
            NotFoundError: If contact doesn't exist
            ServiceError: If interaction recording fails
        """
        self.log_operation("record_interaction", contact_id=contact_id, date=date, note=note, tags=tags)
        with self.in_transaction() as session:
            try:
                contact = session.get(Contact, contact_id)
                if not contact:
                    raise NotFoundError(f"Contact {contact_id} not found")

                # Validate date
                if date > datetime.now(date.tzinfo):
                    raise ValidationError("Interaction date cannot be in the future")

                interaction = Interaction(
                    contact_id=contact_id,
                    date=date,
                    note=note,
                    tags=tags or []
                )
                session.add(interaction)
                contact.update_last_interaction(date, tags)
                return contact
            except Exception as e:
                raise self.handle_error("record_interaction", e)

    def update_tag_frequency(
        self,
        contact_id: UUID,
        tag_name: str,
        frequency_days: Optional[int]
    ) -> Contact:
        """Update contact-tag frequency settings.

        Requirements: [FR2.2.1, FR2.2.4]

        Raises:
            ValidationError: If frequency_days is negative
            NotFoundError: If contact or tag doesn't exist
            ServiceError: If frequency update fails
        """
        self.log_operation("update_tag_frequency", contact_id=contact_id, tag_name=tag_name, frequency_days=frequency_days)
        with self.in_transaction() as session:
            try:
                contact = session.get(Contact, contact_id)
                if not contact:
                    raise NotFoundError(f"Contact {contact_id} not found")

                # Validate frequency
                if frequency_days is not None and frequency_days < 0:
                    raise ValidationError("Frequency days cannot be negative")

                contact.set_tag_frequency(tag_name, frequency_days)
                return contact
            except Exception as e:
                raise self.handle_error("update_tag_frequency", e)

    def validate_sub_information(
        self,
        contact_id: UUID,
        sub_information: Dict[str, Any]
    ) -> bool:
        """Validate sub_information against current template.

        Requirements: [FR1.2.1, FR1.2.2]

        Raises:
            ValidationError: If sub_information format is invalid
            NotFoundError: If contact doesn't exist
            ServiceError: If validation fails
        """
        self.log_operation("validate_sub_information", contact_id=contact_id, sub_information=sub_information)
        with self.in_transaction() as session:
            try:
                contact = session.get(Contact, contact_id)
                if not contact:
                    raise NotFoundError(f"Contact {contact_id} not found")

                # Get current template
                template = self.get_current_template()

                # Validate against template
                return template.validate(sub_information)
            except Exception as e:
                raise self.handle_error("validate_sub_information", e)
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

Examples:
```python
def delete(self, contact_id: UUID) -> None:
    """Example of cascade delete with proper cleanup."""
    with self.in_transaction() as session:
        contact = session.get(Contact, contact_id)
        if not contact:
            raise NotFoundError(f"Contact {contact_id} not found")

        # Clean up related entities
        session.query(Interaction).filter_by(contact_id=contact_id).delete()
        session.query(Note).filter_by(contact_id=contact_id).delete()

        # Remove tag associations but preserve tags
        contact.tags.clear()
        session.delete(contact)

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
1. **ServiceError**
   - Base error for all service operations
   - Includes operation name and timestamp
   - Preserves original error in chain
   - Example: `ServiceError in operation 'create_contact' at 2025-02-25 10:30:00 UTC`

2. **ValidationError**
   - Invalid contact data format
   - Invalid tag format
   - Invalid search criteria
   - Invalid pagination parameters
   - Example: `ValidationError in operation 'add_tags' at 2025-02-25 10:30:00 UTC`

3. **NotFoundError**
   - Contact doesn't exist
   - Referenced tag doesn't exist
   - Example: `NotFoundError in operation 'get_by_id' at 2025-02-25 10:30:00 UTC`

4. **TransactionError**
   - Database operation failed
   - Rollback failed
   - Example: `TransactionError in operation 'commit' at 2025-02-25 10:30:00 UTC`

### Error Handling Principles
1. **Clear Context**
   - All errors include operation name
   - All errors include UTC timestamp
   - Original error preserved in chain
   - Stack traces logged automatically

2. **Error Categories**
   - Service layer errors inherit from ServiceError
   - Specific error types for common scenarios
   - Consistent error hierarchy

3. **Error Message Format**
   ```
   {ErrorType} in operation '{operation}' at {YYYY-MM-DD HH:MM:SS UTC}
   [Caused by: {nested_service_error} | Error: {original_error}]
   ```

4. **Logging Strategy**
   - Error details logged automatically
   - Stack traces preserved
   - Operation context included
   - UTC timestamps for consistency

### Error Scenarios
```python
# Validation with Context
def validate_contact_data(self, operation: str, data: Dict[str, Any]) -> None:
    """Validate contact data with operation context."""
    try:
        if not data.get('name'):
            raise ValueError("Contact name is required")
        if 'tags' in data and not isinstance(data['tags'], list):
            raise ValueError("Tags must be a list")
    except ValueError as e:
        raise ValidationError(operation, e)

# Not Found with Context
def get_or_404(self, operation: str, contact_id: UUID) -> Contact:
    """Get contact with operation context."""
    contact = self.get_by_id(contact_id)
    if not contact:
        raise NotFoundError(operation, ValueError(f"Contact {contact_id} not found"))
    return contact

# Transaction with Error Chain
def delete_with_cleanup(self, contact_id: UUID) -> None:
    """Example of transaction with error chain."""
    with self.in_transaction() as session:
        try:
            contact = self.get_or_404("delete", contact_id)
            try:
                session.query(Interaction).filter_by(contact_id=contact_id).delete()
                session.query(Note).filter_by(contact_id=contact_id).delete()
                contact.tags.clear()
                session.delete(contact)
            except Exception as e:
                raise ServiceError("delete_cleanup", e)
        except Exception as e:
            if not isinstance(e, ServiceError):
                raise ServiceError("delete", e)
            raise
```

## Testing Strategy

### Unit Tests
✅ Planned:
1. **Basic Operations**
   - Create contact with valid data
   - Update existing contact
   - Delete contact and verify cleanup [FR1.3.2]
     - Verify all contact information removed
     - Verify tag associations removed
     - Verify interaction records removed
     - Verify notes removed
     - Verify tag definitions preserved if used by others
     - Verify graceful handling of non-existent contacts

2. **Retrieval Operations** [FR1.3.1]
   - Get existing contact by ID
     - Verify complete contact information
     - Verify all associated tags included
     - Verify last interaction date included
   - Handle non-existent contact ID
   - Handle invalid UUID format

3. **Search Operations** [FR1.3.3]
   - Search by name
     - Exact match
     - Partial match
     - Case sensitivity
   - Search by tags
     - Single tag
     - Multiple tags
     - Non-existent tags
   - Search by date range
     - Last interaction date
     - Timezone handling
   - Search by custom fields
     - Single field
     - Multiple fields
     - Non-existent fields
   - Search by staleness
     - Single tag staleness
     - Multiple tag staleness
   - Combined criteria
     - Multiple field types
     - Complex combinations
   - Pagination
     - Default page size
     - Custom page size
     - Page navigation
   - Empty results handling
     - No matches
     - Invalid criteria

4. **Tag Operations**
   - Add valid tags
   - Remove existing tags
   - Handle invalid tag formats

5. **Interaction Recording**
   - Record valid interaction
   - Handle future dates
   - Update last contact time

6. **Error Cases**
   - Not found scenarios
   - Validation failures
   - Transaction rollbacks

### Integration Tests
✅ Planned:
1. **Data Persistence**
   - Verify contact deletion cascades properly [FR1.3.2]
   - Verify search results reflect database state [FR1.3.3]
   - Verify retrieval includes all related data [FR1.3.1]

2. **Transaction Integrity**
   - Verify atomic operations
   - Check rollback effectiveness
   - Test cleanup on errors

3. **Search Performance** [FR1.3.3]
   - Verify pagination efficiency
   - Test complex criteria performance
   - Measure large dataset behavior

4. **Error Scenarios**
   - Test non-existent ID handling [FR1.3.1]
   - Verify deletion rollback [FR1.3.2]
   - Test invalid search criteria [FR1.3.3]

### Test Fixtures
✅ Required:
1. **Base Data**
   - Sample contacts with various fields
   - Contacts with multiple tags
   - Contacts with interaction history
   - Contacts with custom fields

2. **Search Scenarios** [FR1.3.3]
   - Contacts with similar names
   - Contacts with overlapping tags
   - Contacts with varied interaction dates
   - Contacts with different staleness states

3. **Relationship Data**
   - Tags used by multiple contacts
   - Contacts sharing tags
   - Complex interaction histories

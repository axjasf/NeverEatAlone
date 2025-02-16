# Interaction Tracking Refactoring

## Executive Summary

This refactoring centralizes all interaction content in the Note entity while maintaining efficient timestamp tracking at both Contact and Tag levels. The key changes are:

1. **Centralization**: All interaction content and history moves to Note entities
2. **Two Note Types**: Notes become either content notes or interaction records
3. **Efficient Tracking**: Contact and Tag models keep timestamps for quick querying
4. **Proper History**: Full interaction history maintained through Notes
5. **Better Validation**: Clear rules for what makes a valid interaction record

Impact: This change simplifies the data model, improves data consistency, and provides better interaction history tracking while maintaining efficient querying for dashboards and reminders.

## Implementation Guide

### Prerequisites
1. Familiarize yourself with the current architecture:
   - Review `docs/development/architecture/model_layer_design.md` for layer separation
   - Review `docs/brd/modules/contact_management/technical/data_model.md` for current model
   - Review `docs/brd/modules/contact_management/requirements/functional.md` for requirements

2. Understand the codebase structure:
   ```
   backend/app/
   ├── models/
   │   ├── domain/     # Business logic
   │   │   ├── tag_model.py
   │   │   ├── note_model.py
   │   │   └── contact_model.py
   │   ├── orm/        # Database mapping
   │   │   ├── tag_orm.py
   │   │   ├── note_orm.py
   │   │   └── contact_orm.py
   │   └── repositories/  # Data access
   │       ├── interfaces.py
   │       ├── sqlalchemy_tag_repository.py
   │       ├── sqlalchemy_note_repository.py
   │       └── sqlalchemy_contact_repository.py
   └── tests/
       ├── models/
       │   └── domain/
       │       ├── test_tag.py
       │       ├── test_note.py
       │       └── test_contact.py
       └── repositories/
           ├── test_tag_repository.py
           ├── test_note_repository.py
           └── test_contact_repository.py
   ```

### Implementation Process
For each phase (Tag → Note → Contact):

1. **Test Review**
   - Review existing tests in corresponding test file
   - Propose new test cases to reviewer
   - Get approval for test changes
   - DO NOT proceed with implementation until tests are approved

2. **Test Implementation (RED)**
   - Implement approved test cases
   - Run tests to verify they fail as expected
   - Show test results to reviewer
   - Get approval to proceed with model changes

3. **Domain Model Changes**
   - Update domain model based on requirements
   - Run tests (should still be RED)
   - Update any domain model dependencies

4. **ORM Model Changes**
   - Update ORM model to match domain changes
   - Add/update any necessary constraints
   - Update any ORM model dependencies

5. **Repository Changes**
   - Update repository implementation
   - Add new query methods as needed
   - Update any dependent repositories

6. **Test Verification (GREEN)**
   - Run tests until they pass
   - Fix any issues
   - Get approval before moving to next phase

### Key Files to Review First

1. **Tag Changes**
   - Current: `backend/app/models/domain/tag_model.py`
   - Tests: `tests/models/domain/test_tag.py`
   - Requirements: FR2.2.1 through FR2.2.6 in functional.md

2. **Note Changes**
   - Current: `backend/app/models/domain/note_model.py`
   - Tests: `tests/models/domain/test_note.py`
   - Requirements: FR3.1.1 through FR3.1.7 in functional.md

3. **Contact Changes**
   - Current: `backend/app/models/domain/contact_model.py`
   - Tests: `tests/models/domain/test_contact.py`
   - Requirements: FR1.1.4 and FR1.1.5 in functional.md

### Common Pitfalls to Avoid

1. **Test Dependencies**
   - Always mock external dependencies in unit tests
   - Use the `@pytest.fixture` for common test setups
   - See existing tests for examples

2. **Validation Rules**
   - All validation happens in domain models
   - ORMs only enforce database constraints
   - See existing validation in models for examples

3. **Repository Pattern**
   - Repositories abstract database operations
   - Domain models should not know about ORMs
   - Follow existing patterns in repository implementations

4. **Integration Testing**
   - Integration tests go in `tests/integration/`
   - They should test complete workflows
   - They use real repositories (no mocks)

### Getting Help

1. **Documentation**
   - Check `docs/development/architecture/model_layer_design.md` for patterns
   - Review `docs/brd/modules/contact_management/` for requirements
   - See `docs/implementation/backend/MODEL_LAYER.md` for implementation details

2. **Example PRs**
   - See PR #XX for similar model changes
   - See PR #YY for test examples
   - See PR #ZZ for repository pattern examples

## 1. Requirements Changes

### 1.1 Core Concept Changes

- All interaction content must be stored in Note entities
- Notes can be either content notes or interaction records (is_interaction flag)
- Contact tracking uses timestamps for efficient querying:
  - Contact level: last_contact_at for general tracking
  - Tag level: last_contact for tag-specific tracking and frequency calculations
- Contact briefing text remains as quick-reference context about the person

### 1.2 Fields to Remove

- Tag.last_contact_notes (move to Note content)
- Any other direct text storage of interaction information

### 1.3 Fields to Keep

- Contact.contact_briefing_text: Quick summary of who the person is
- Tag.last_contact: Timestamp for efficient next-contact calculations
- Tag.frequency_days: For calculating when next contact is due

### 1.4 Updated Requirements

- FR3.1.1: Notes must support two distinct types:
  - Content notes: Actual information about the contact
  - Interaction records: Just tracking that contact happened
- FR3.1.2: Notes must require either content or interaction flag
- FR3.2.1: Contact's last_contact_at must update when creating interaction notes
- FR3.2.2: Contact-tag last_contact dates must update based on note tags
- FR3.2.3: System must support recording interactions without content
- FR3.2.4: System must maintain interaction history with tags
- FR3.2.5: System must support efficient querying of next due contacts

## 2. Implementation Breakdown

### 2.1 Tag Model Changes (Phase 1)

#### Domain Model Changes
- Remove last_contact_notes field (content moves to Notes)
- Keep last_contact timestamp for efficient querying
- Keep frequency_days for due date calculations
- Update validation and constructor
- Ensure frequency tracking works with Note-based updates
- Add methods for calculating next due date
- Consider contact_tags and note_tags relationships

#### ORM Changes
- Remove last_contact_notes column
- Update relationships and constraints
- Add indices for efficient querying:
  ```sql
  CREATE INDEX idx_tags_last_contact ON tags(last_contact) WHERE last_contact IS NOT NULL;
  CREATE INDEX idx_tags_frequency ON tags(frequency_days) WHERE frequency_days IS NOT NULL;
  ```

#### Repository Changes
- Update tag creation/update logic
- Ensure proper handling of last_contact updates
- Update query methods
- Add methods for:
  ```python
  def find_by_frequency(self) -> List[Tag]:
      """Find tags with frequency settings."""

  def find_stale(self) -> List[Tag]:
      """Find tags that are overdue for contact."""
  ```

#### Test Updates
```python
def test_tag_without_notes():
    """Ensure tag works without last_contact_notes field"""
    tag = Tag(entity_id=uuid4(), entity_type=EntityType.CONTACT, name="#test")
    assert not hasattr(tag, 'last_contact_notes')

def test_tag_frequency_validation():
    """Test frequency validation still works"""
    tag = Tag(entity_id=uuid4(), entity_type=EntityType.CONTACT, name="#test")
    tag.set_frequency(30)
    assert tag.frequency_days == 30
    assert tag.last_contact is not None

def test_tag_staleness():
    """Test staleness calculation with new model"""
    tag = Tag(entity_id=uuid4(), entity_type=EntityType.CONTACT, name="#test")
    tag.set_frequency(7)
    tag.update_last_contact(datetime.now() - timedelta(days=8))
    assert tag.is_stale()
```

### 2.2 Note Model Changes (Phase 2)

#### Domain Model Changes
- Add is_interaction flag
- Add interaction_date field
- Ensure proper validation for content/interaction requirements:
  ```python
  if is_interaction and not interaction_date:
      raise ValueError("Interaction notes require a date")
  if not is_interaction and not content:
      raise ValueError("Content notes require content")
  ```
- Update tag handling to trigger contact and tag timestamp updates
- Ensure proper relationship with note_tags junction table

#### ORM Changes
- Add is_interaction and interaction_date columns
- Add constraints for content/interaction validation:
  ```sql
  CONSTRAINT valid_interaction CHECK (
      (is_interaction = FALSE AND interaction_date IS NULL) OR
      (is_interaction = TRUE AND interaction_date IS NOT NULL)
  ),
  CONSTRAINT valid_content CHECK (
      (is_interaction = TRUE) OR
      (is_interaction = FALSE AND content IS NOT NULL)
  )
  ```
- Update relationships with note_tags table
- Add indices:
  ```sql
  CREATE INDEX idx_notes_interaction ON notes(is_interaction, interaction_date);
  CREATE INDEX idx_notes_contact_interaction ON notes(contact_id, is_interaction);
  ```

#### Repository Changes
- Add methods for interaction-specific queries:
  ```python
  def find_interactions(self, contact_id: UUID) -> List[Note]:
      """Find interaction notes for a contact."""

  def find_interactions_by_tag(self, tag_name: str) -> List[Note]:
      """Find interaction notes with specific tag."""
  ```
- Update note creation to handle interaction tracking
- Add validation for interaction dates

#### Test Updates
```python
def test_note_interaction_validation():
    """Test interaction note validation"""
    with pytest.raises(ValueError):
        Note(contact_id=uuid4(), is_interaction=True)  # Missing date

def test_note_content_validation():
    """Test content note validation"""
    with pytest.raises(ValueError):
        Note(contact_id=uuid4(), is_interaction=False)  # Missing content

def test_note_updates_contact():
    """Test note updates contact timestamps"""
    contact = Contact(name="Test")
    note = Note(contact_id=contact.id, is_interaction=True,
                interaction_date=datetime.now())
    assert contact.last_contact_at == note.interaction_date
```

### 2.3 Contact Model Changes (Phase 3)

#### Domain Model Changes
- Rename last_interaction_at to last_contact_at
- Update timestamp update logic to work with Note interactions
- Add interaction history methods
- Update validation and constructor

#### ORM Changes
- Rename last_interaction_at column to last_contact_at
- Update relationships and constraints
- Add indices:
  ```sql
  CREATE INDEX idx_contacts_last_contact ON contacts(last_contact_at);
  ```

#### Repository Changes
- Update contact creation/update logic
- Ensure proper handling of last_contact_at updates
- Add methods for:
  ```python
  def find_by_last_contact(self) -> List[Contact]:
      """Find contacts ordered by last contact date."""

  def find_requiring_contact(self) -> List[Contact]:
      """Find contacts needing contact based on tag frequencies."""
  ```

#### Test Updates
```python
def test_contact_last_contact_rename():
    """Test last_contact_at field rename"""
    contact = Contact(name="Test")
    assert hasattr(contact, 'last_contact_at')
    assert not hasattr(contact, 'last_interaction_at')

def test_contact_interaction_history():
    """Test interaction history through notes"""
    contact = Contact(name="Test")
    note = contact.add_note(content="Test", is_interaction=True)
    assert contact.last_contact_at == note.interaction_date
```

## 3. Testing Strategy

### 3.1 Unit Tests
- Test each model in isolation
- Verify validation rules
- Check edge cases
- Mock dependencies where needed

### 3.2 Integration Tests
```python
def test_complete_interaction_flow():
    """Test complete interaction recording flow"""
    contact = Contact(name="Test")
    tag = contact.add_tag("#test")
    tag.set_frequency(7)

    note = contact.add_note(
        content="Met for coffee",
        is_interaction=True,
        interaction_date=datetime.now()
    )
    note.add_tag("#test")

    assert contact.last_contact_at == note.interaction_date
    assert tag.last_contact == note.interaction_date
    assert not tag.is_stale()

def test_tag_frequency_tracking():
    """Test frequency tracking across system"""
    contact = Contact(name="Test")
    tag = contact.add_tag("#monthly")
    tag.set_frequency(30)

    # Add interaction from 31 days ago
    note = contact.add_note(
        is_interaction=True,
        interaction_date=datetime.now() - timedelta(days=31)
    )
    note.add_tag("#monthly")

    assert tag.is_stale()
    assert contact.needs_contact()
```

## 4. Success Criteria

1. All tests pass
2. Data model is simpler
3. Interaction history is complete
4. Querying remains efficient
5. Clear separation of concerns

## 5. Implementation Order

1. Tag Model Changes
   - Remove last_contact_notes
   - Update tests
   - Verify frequency tracking

2. Note Model Changes
   - Add interaction support
   - Update validation
   - Add contact updates

3. Contact Model Changes
   - Rename timestamp field
   - Update interaction tracking
   - Add history methods

4. Integration Testing
   - Full interaction flow
   - Frequency tracking
   - Query performance

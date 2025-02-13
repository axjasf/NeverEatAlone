# Model Layer Design

## Overview
This document outlines the architecture of the model layer in NeverEatAlone, using a Domain-Driven Design approach with the Repository pattern.

## Architecture

### Layer Structure
```
[Domain Models] → [Repository Interfaces] → [Repository Implementations] → [Database]
     ↑                    ↑                           ↑                        ↑
Business Logic     Persistence Contract      Storage Implementation     Actual Storage
```

### Components

#### 1. Domain Models
Pure Python classes that encapsulate business logic without persistence concerns.

Example (Tag):
```python
class Tag:
    def __init__(self, entity_id: UUID, entity_type: EntityType, name: str):
        if not name.startswith("#"):
            raise ValueError("Tag must start with '#'")
        self.entity_id = entity_id
        self.name = name.lower()
        # ... business logic only ...

    def is_stale(self) -> bool:
        # Pure business logic
        return self._calculate_staleness()
```

#### 2. Repository Interfaces
Define contracts for persistence operations using Protocol classes.

```python
from typing import Protocol, Optional, List

class TagRepository(Protocol):
    def save(self, tag: Tag) -> None: ...
    def find_by_name(self, name: str) -> Optional[Tag]: ...
    def find_by_entity(self, entity_id: UUID) -> List[Tag]: ...
    def delete(self, tag: Tag) -> None: ...

class ContactRepository(Protocol):
    def save(self, contact: Contact) -> None: ...
    def find_by_id(self, id: UUID) -> Optional[Contact]: ...
    def find_by_name(self, name: str) -> List[Contact]: ...
    def delete(self, contact: Contact) -> None: ...
```

#### 3. Repository Implementations
Concrete implementations for different storage backends.

```python
class SQLAlchemyTagRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, tag: Tag) -> None:
        tag_orm = TagORM(
            entity_id=tag.entity_id,
            name=tag.name
        )
        self.session.add(tag_orm)
        self.session.commit()
```

### Design Principles

1. **Separation of Concerns**
   - Domain Models: Business logic only
   - Repositories: Persistence logic only
   - Services: Orchestration and transaction management

2. **Dependency Inversion**
   - High-level modules (domain models) don't depend on low-level modules (database)
   - Both depend on abstractions (repository interfaces)

3. **Single Responsibility**
   - Each class has one reason to change
   - Domain models change for business rules
   - Repositories change for persistence logic

## Implementation Guide

### 1. Domain Models
- Keep models pure Python classes
- Validate in constructors
- Use type hints
- Document with docstrings
- Include only business logic

```python
class Contact:
    def __init__(self, name: str):
        """Create a new contact.

        Args:
            name: The contact's name
        """
        self.name = name
        self.tags: List[Tag] = []

    def add_tag(self, tag: Tag) -> None:
        """Add a tag to this contact."""
        self.tags.append(tag)
```

### 2. Repository Interfaces
- Define clear contracts
- Use Protocol classes
- Include common CRUD operations
- Add domain-specific queries

### 3. SQLAlchemy Implementation
- Create ORM models separately
- Map between domain and ORM models
- Handle transactions
- Implement error handling

```python
class TagORM(Base):
    __tablename__ = "tags"

    id = Column(UUID, primary_key=True)
    entity_id = Column(UUID, nullable=False)
    name = Column(String, nullable=False)
```

## Testing Strategy

### 1. Domain Model Tests
- Pure unit tests
- No database needed
- Fast execution
- Focus on business rules

```python
def test_tag_validation():
    with pytest.raises(ValueError):
        Tag(entity_id=uuid4(), name="invalid")  # Missing #
```

### 2. Repository Tests
- Integration tests
- Test with real database
- Focus on persistence
- Test edge cases

```python
def test_tag_repository(db_session):
    repo = SQLAlchemyTagRepository(db_session)
    tag = Tag(entity_id=uuid4(), name="#test")
    repo.save(tag)

    found = repo.find_by_name("#test")
    assert found is not None
```

## Migration Path

1. **Phase 1: Domain Models**
   - Create pure domain models
   - Move business logic from existing models
   - Add comprehensive tests

2. **Phase 2: Repositories**
   - Define repository interfaces
   - Create SQLAlchemy implementations
   - Add integration tests

3. **Phase 3: Services**
   - Create service layer
   - Move orchestration logic
   - Update API endpoints

## Benefits

1. **Maintainability**
   - Clear separation of concerns
   - Easy to understand components
   - Isolated changes

2. **Testability**
   - Fast unit tests
   - No database for business logic
   - Comprehensive test coverage

3. **Flexibility**
   - Easy to change storage
   - Easy to add caching
   - Easy to add logging

4. **Scalability**
   - Can optimize each layer
   - Can cache at repository level
   - Can distribute components

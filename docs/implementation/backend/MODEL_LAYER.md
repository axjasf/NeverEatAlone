# Model Layer Reference

> For architectural decisions and design patterns, see [Model Layer Design](../../development/architecture/model_layer_design.md)

## Overview

This document serves as a reference for the current implementation of the model layer, describing the available components and their capabilities.

The model layer implements a rich domain model with clean separation between domain logic, persistence, and data transfer objects. It follows Domain-Driven Design principles and the Repository pattern.

## Core Components

### Base Classes

#### BaseModel (Domain)
- Common fields for all domain models:
  - `id`: UUID primary key
  - `created_at`: Creation timestamp (UTC)
  - `updated_at`: Last modification timestamp (UTC)
- Automatic timestamp management
- Foundation for all domain models

#### BaseORMModel (ORM)
- SQLAlchemy declarative base with common fields
- Custom GUID type for UUID compatibility
- Automatic timestamp management
- Foundation for all ORM models

### Domain Models

#### Contact
- Core entity representing a person or organization
- Properties:
  - `name`: Required name field
  - `first_name`: Optional first name
  - `briefing_text`: Optional description
  - `sub_information`: Flexible JSON data structure
  - `notes`: List of associated notes
  - `tags`: List of associated tags
- Methods for note and tag management
- Validation rules for all fields

#### Note
- Represents an interaction or observation about a contact
- Properties:
  - `contact_id`: Reference to parent contact
  - `content`: The note text
  - `statements`: List of detailed statements
  - `tags`: List of associated tags
- Methods for statement and tag management
- Content validation and whitespace handling

#### Statement
- Represents a single, taggable piece of information within a note
- Properties:
  - `content`: The statement text
  - `tags`: List of associated tags
- Content validation
- Tag management methods

#### Tag
- Represents a categorization or reminder
- Properties:
  - `entity_id`: ID of tagged entity
  - `entity_type`: Type of tagged entity (Contact/Note/Statement)
  - `name`: Tag text (starts with #)
  - `frequency_days`: Optional reminder frequency
  - `last_contact`: Last contact timestamp
- Methods for frequency and staleness management
- Validation rules for tag names

### ORM Models

#### ContactORM
- SQLAlchemy model for contacts
- One-to-many relationship with notes
- Many-to-many relationship with tags
- JSON field for sub_information

#### NoteORM
- SQLAlchemy model for notes
- Many-to-one relationship with contacts
- One-to-many relationship with statements
- Many-to-many relationship with tags

#### StatementORM
- SQLAlchemy model for statements
- Many-to-one relationship with notes
- Many-to-many relationship with tags
- Sequence number for ordering

#### TagORM
- SQLAlchemy model for tags
- Many-to-many relationships with contacts, notes, and statements
- Check constraint for valid entity types

### Repository Interfaces

#### ContactRepository
- Interface for contact persistence operations
- Methods:
  - `save(contact: Contact) -> Contact`
  - `find_by_id(contact_id: UUID) -> Optional[Contact]`
  - `find_by_tag(tag_name: str) -> List[Contact]`
  - `find_stale() -> List[Contact]`
  - `delete(contact: Contact) -> None`

#### NoteRepository
- Interface for note persistence operations
- Methods:
  - `save(note: Note) -> Note`
  - `find_by_id(note_id: UUID) -> Optional[Note]`
  - `find_by_contact(contact_id: UUID) -> List[Note]`
  - `find_by_tag(tag_name: str) -> List[Note]`
  - `delete(note: Note) -> None`

#### TagRepository
- Interface for tag persistence operations
- Methods:
  - `save(tag: Tag) -> Tag`
  - `find_by_id(tag_id: UUID) -> Optional[Tag]`
  - `find_by_entity(entity_id: UUID, entity_type: EntityType) -> List[Tag]`
  - `find_by_name(name: str) -> List[Tag]`
  - `find_stale() -> List[Tag]`
  - `delete(tag: Tag) -> None`

## Entity Relationships

### Contact-Note Relationship
- One-to-many: Contact -> Notes
- Cascade delete: Notes are deleted with their contact
- Bidirectional navigation

### Note-Statement Relationship
- One-to-many: Note -> Statements
- Cascade delete: Statements are deleted with their note
- Ordered by sequence number
- Bidirectional navigation

### Tag Relationships
- Many-to-many with all entities (Contact/Note/Statement)
- No cascade delete: Tags exist independently
- Natural key: (entity_id, entity_type, name)

## Tag System

### Tag Structure
- Always starts with '#'
- Case-insensitive (stored lowercase)
- Alphanumeric and underscore characters only
- Unique per entity

### Frequency Tracking
- Optional frequency_days (1-365)
- Automatic last_contact tracking
- Staleness calculation
- Used for contact reminders

## Testing Strategy

### Unit Tests
- Comprehensive domain model tests
- Validation and business rule coverage
- Time-dependent behavior testing

### Integration Tests
- Repository implementation tests
- Database constraint testing
- Transaction management
- Relationship cascade behavior

### Test Configuration
- In-memory SQLite database
- Automatic schema creation
- Transaction rollback after each test
- Comprehensive fixtures

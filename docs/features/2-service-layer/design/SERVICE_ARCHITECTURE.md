# Service Layer Architecture

## Overview
Service layer provides a clean separation between domain logic and API endpoints, handling transaction management and business operations in a single-user context. It coordinates multi-step operations while maintaining data consistency and providing clear error context.

## Key Decisions

1. **Transaction Management**
   - Context: Need to handle multi-step operations (e.g., "create contact with tags")
   - Decision: Simple transaction context per business operation
   - Rationale: Single-user system doesn't need complex transaction patterns

2. **Error Handling**
   - Context: Need clear error context for debugging
   - Decision: Service-specific exceptions with operation context
   - Rationale: Makes debugging easier in development

3. **Layer Separation**
   - Context: Need clean separation of concerns
   - Decision: Services only depend on domain models and repositories
   - Rationale: Keeps business logic separate from data access and API concerns

## Component Structure

1. Base Service Layer
   - Transaction context management
   - Error handling patterns
   - Common service patterns

2. Core Business Services
   - ContactService: Contact management with custom fields
   - NoteService: Note/Interaction management
   - StatementService: Statement sequence management
   - TagService: Polymorphic tag operations

3. Supporting Services
   - TemplateService: Contact field definitions and versioning
   - ReminderService: Recurrence and timezone-aware reminders
   - InteractionService: Interaction tracking and history

4. Cross-Cutting Concerns
   - Basic logging
   - Error tracking
   - Operation context
   - Timezone handling

## Technical Boundaries

### Dependencies
- Domain models (Contact, Note, Statement, Tag, etc.)
- Repository layer
- SQLite backend

### Integration Points
- API layer (upcoming)
- Template versioning system
- Timezone conversion utilities

### Constraints
- Single-user context
- SQLite limitations
- UTC-based storage with timezone context

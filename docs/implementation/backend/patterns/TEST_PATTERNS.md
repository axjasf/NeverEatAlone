# Test Patterns Guide

## Overview
This guide documents the comprehensive test patterns established during the Note BO implementation (CR-2024.02-23). It covers testing strategies across all aspects of a business object, from basic CRUD to complex temporal logic, using the Note BO as our reference implementation.

Key aspects covered:
- Basic patterns: Creation, validation, and state management
- Relationship patterns: Collections, associations, and object graphs
- Complex patterns: Timezone handling, DST, and cross-cutting concerns

The patterns are organized by:
1. Layer (domain, ORM, repository)
2. Category (basic, relationship, temporal)
3. Complexity (common → complex)

Each pattern is demonstrated with concrete examples from the Note BO implementation, showing how to handle everything from simple validation to complex timezone scenarios.

## Test Organization

### 1. Domain Layer Tests
Tests for business logic and invariants.

#### Basic Tests (Common)
1. **Creation Tests**
   ```python
   def test_note_creation():
       """Test creating an entity with required fields."""
   ```
   - Verify required fields
   - Check default values
   - Validate initial state

2. **Validation Tests**
   ```python
   def test_note_content_validation():
       """Test validation rules."""
   ```
   - Input validation
   - Business rules
   - Error cases

3. **Update Tests**
   ```python
   def test_note_update_tracking():
       """Test state changes and tracking."""
   ```
   - State modifications
   - Audit field updates
   - Change tracking

#### Relationship Tests (Common)
1. **Collection Management**
   ```python
   def test_note_statement_management():
       """Test managing child collections."""
   ```
   - Adding items
   - Removing items
   - Ordering
   - Validation

2. **Association Tests**
   ```python
   def test_note_tag_management():
       """Test managing associations."""
   ```
   - Adding associations
   - Removing associations
   - Validation rules

#### Temporal Tests (Complex)
1. **Timezone Handling**
   ```python
   def test_note_timezone_handling():
       """Test timezone-aware operations."""
   ```
   - UTC conversion
   - Timezone preservation
   - Different input timezones

2. **Timezone Edge Cases**
   ```python
   def test_note_timezone_edge_cases():
       """Test timezone edge cases."""
   ```
   - DST transitions
   - Day boundaries
   - Fractional offsets

### 2. ORM Layer Tests
Tests for persistence mapping and constraints.

#### Basic Tests (Common)
1. **Persistence Tests**
   ```python
   def test_note_creation_with_required_fields():
       """Test basic persistence."""
   ```
   - Required fields
   - Default values
   - Constraints

2. **Constraint Tests**
   ```python
   def test_note_requires_contact():
       """Test database constraints."""
   ```
   - Foreign key constraints
   - Unique constraints
   - Not null constraints

#### Relationship Tests (Common)
1. **Collection Persistence**
   ```python
   def test_note_statement_creation():
       """Test persisting collections."""
   ```
   - Save collections
   - Load collections
   - Maintain order

2. **Cascade Operations**
   ```python
   def test_note_statement_deletion():
       """Test cascade operations."""
   ```
   - Cascade delete
   - Orphan handling
   - Relationship cleanup

#### Temporal Tests (Complex)
1. **Timezone Storage**
   ```python
   def test_note_timezone_handling():
       """Test timezone persistence."""
   ```
   - UTC storage
   - Timezone conversion
   - Load/save consistency

2. **Timezone Edge Cases**
   ```python
   def test_note_timezone_edge_cases():
       """Test timezone storage edge cases."""
   ```
   - DST handling
   - Date boundaries
   - Offset preservation

### 3. Repository Layer Tests
Tests for data access patterns and queries.

#### Basic Tests (Common)
1. **CRUD Operations**
   ```python
   def test_note_save_and_find():
       """Test basic CRUD."""
   ```
   - Save
   - Find by ID
   - Update
   - Delete

2. **Query Tests**
   ```python
   def test_note_find_by_contact():
       """Test query operations."""
   ```
   - Find by field
   - Find by relationship
   - Collection queries

#### Relationship Tests (Common)
1. **Graph Loading**
   ```python
   def test_note_with_statements():
       """Test loading object graphs."""
   ```
   - Load relationships
   - Eager/lazy loading
   - Collection handling

2. **Graph Operations**
   ```python
   def test_note_with_statement_tags():
       """Test operations on graphs."""
   ```
   - Save graphs
   - Update graphs
   - Delete graphs

#### Temporal Tests (Complex)
1. **Timezone Queries**
   ```python
   def test_note_timezone_query_handling():
       """Test timezone-aware queries."""
   ```
   - Date range queries
   - Timezone conversion
   - Sorting by date

2. **Timezone Edge Cases**
   ```python
   def test_note_timezone_edge_cases():
       """Test timezone query edge cases."""
   ```
   - DST boundaries
   - Date boundaries
   - Cross-timezone queries

## Best Practices

1. **Test Organization**
   - Group by complexity (basic → complex)
   - Group by feature type
   - Clear test names and docstrings

2. **Test Structure**
   - Arrange: Setup test data
   - Act: Perform operation
   - Assert: Verify results
   - Clean: Cleanup if needed

3. **Timezone Testing**
   - Always use explicit timezones
   - Test multiple timezone inputs
   - Cover DST transitions
   - Test date boundaries

4. **Documentation**
   - Document test purpose
   - List business rules tested
   - Explain complex scenarios
   - Reference related tests

## Common Patterns

1. **Validation Testing**
   - Test empty/null values
   - Test boundary values
   - Test invalid formats
   - Test business rules

2. **Relationship Testing**
   - Test adding/removing
   - Test ordering
   - Test constraints
   - Test cascades

3. **Temporal Testing**
   - Test timezone handling
   - Test date comparisons
   - Test range queries
   - Test edge cases

# Test Patterns Guide

## Overview
This guide documents the comprehensive test patterns established during the Note BO implementation (CR-2024.02-23) and enhanced with patterns from Contact and Template BOs. The patterns progress from basic to complex, and from common to rare use cases.

Test Categories (from common to rare):
1. **Basic Tests** (All Layers)
   - Domain creation and validation
   - ORM persistence
   - Repository CRUD operations

2. **Relationship Tests** (Common)
   - Collection management
   - Association handling
   - Object graph operations

3. **State Management** (Moderate)
   - State transitions
   - Cascading updates
   - Event tracking

4. **Data Structures** (Complex)
   - Nested object validation
   - Complex schema rules
   - Type-specific validation

5. **Temporal Logic** (Complex)
   - Basic time handling
   - Time-based calculations
   - Timezone edge cases

6. **Evolution** (Rare)
   - Schema changes
   - Data migration
   - Version management

Each category is demonstrated with concrete examples from our reference implementations, showing how to handle everything from simple validation to complex scenarios.

The patterns are organized by:
1. Frequency (common → rare)
2. Complexity (basic → complex)
3. Dependencies (foundational → advanced)

## Test Organization

### 1. Basic Tests (Common, All Layers)
1. **Domain Creation & Validation**
   ```python
   def test_note_creation():
       """Test creating an entity with required fields."""
   ```
   - Verify required fields
   - Check default values
   - Validate initial state

2. **ORM Persistence**
   ```python
   def test_note_creation_with_required_fields():
       """Test basic persistence."""
   ```
   - Required fields
   - Default values
   - Constraints

3. **Repository CRUD**
   ```python
   def test_note_save_and_find():
       """Test basic CRUD."""
   ```
   - Save
   - Find by ID
   - Update
   - Delete

### 2. Relationship Tests (Common, All Layers)
1. **Collection Management**
   ```python
   def test_note_statement_management():
       """Test managing child collections."""
   ```
   - Adding/removing items
   - Ordering
   - Validation

2. **Association Management**
   ```python
   def test_note_tag_management():
       """Test managing associations."""
   ```
   - Adding/removing associations
   - Validation rules
   - Relationship constraints

3. **Graph Operations**
   ```python
   def test_note_with_statement_tags():
       """Test operations on object graphs."""
   ```
   - Save/load graphs
   - Cascade operations
   - Graph queries

### 3. State Management Tests (Moderate)
1. **State Transitions**
   ```python
   def test_note_update_tracking():
       """Test state changes and tracking."""
   ```
   - State modifications
   - Audit fields
   - Change tracking

2. **State-Dependent Behavior**
   ```python
   def test_contact_interaction_recording():
       """Test state-dependent behavior."""
   ```
   - Cascading updates
   - State-dependent validation
   - Event sequencing

### 4. Data Structure Tests (Complex)
1. **Nested Objects**
   ```python
   def test_contact_sub_information_validation():
       """Test nested data structure validation."""
   ```
   - Nested validation
   - Schema validation
   - Type checking

2. **Complex Validation Rules**
   ```python
   def test_template_validation_failures():
       """Test validation rule scenarios."""
   ```
   - Type-specific validation
   - Format validation
   - Custom rules

### 5. Temporal Tests (Complex)
1. **Basic Time Handling**
   ```python
   def test_note_timezone_handling():
       """Test timezone-aware operations."""
   ```
   - UTC conversion
   - Timezone preservation
   - Basic queries

2. **Time Calculations**
   ```python
   def test_contact_find_stale():
       """Test frequency-based operations."""
   ```
   - Frequency calculations
   - Schedule validation
   - Period calculations

3. **Timezone Edge Cases**
   ```python
   def test_note_timezone_edge_cases():
       """Test timezone edge cases."""
   ```
   - DST transitions
   - Day boundaries
   - Cross-timezone queries

### 6. Evolution Tests (Rare)
1. **Schema Changes**
   ```python
   def test_template_evolution_add_field():
       """Test schema evolution scenarios."""
   ```
   - Field changes
   - Version management
   - Compatibility

2. **Data Migration**
   ```python
   def test_template_evolution_change_field_type():
       """Test data migration scenarios."""
   ```
   - Data transformation
   - Version transitions
   - Migration validation

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

4. **Data Structure Testing**
   - Test nested structures
   - Validate complex schemas
   - Check default behaviors
   - Verify type constraints

5. **State Management Testing**
   - Test state transitions
   - Verify cascading updates
   - Check history tracking
   - Validate event sequences

6. **Time-Based Testing**
   - Test frequency calculations
   - Verify schedule handling
   - Check period boundaries
   - Test stale detection

7. **Evolution Testing**
   - Test schema changes
   - Verify version management
   - Check data migration
   - Validate compatibility

8. **Validation Rule Testing**
   - Test type-specific rules
   - Verify format constraints
   - Check custom validators
   - Test error scenarios

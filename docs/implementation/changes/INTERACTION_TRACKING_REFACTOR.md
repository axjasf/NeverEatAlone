# Interaction Tracking Refactoring

## Executive Summary

This refactoring centralizes all interaction content in the Note entity while maintaining efficient timestamp tracking at both Contact and Tag levels. The key changes are:

1. **Centralization**: All interaction content and history moves to Note entities
2. **Two Note Types**: Notes become either content notes or interaction records
3. **Efficient Tracking**: Contact and Tag models keep timestamps for quick querying
4. **Proper History**: Full interaction history maintained through Notes
5. **Better Validation**: Clear rules for what makes a valid interaction record

Impact: This change simplifies the data model, improves data consistency, and provides better interaction history tracking while maintaining efficient querying for dashboards and reminders.

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

### 1.2.1 Fields to Keep

- Contact.contact_briefing_text: Quick summary of who the person is
- Tag.last_contact: Timestamp for efficient next-contact calculations
- Tag.frequency_days: For calculating when next contact is due

### 1.3 Updated Requirements

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

### 2.1 Domain Models

#### Contact Model Changes

- Keep contact_briefing_text field as it serves for quick person context
- Keep briefing_text field for AI-generated summaries
- Keep sub_information JSON field for template-specific data
- Rename last_interaction_at to last_contact_at for consistency
- Ensure last_contact_at updates through Note creation
- Update validation and constructor

#### Tag Model Changes

- Remove last_contact_notes field (content moves to Notes)
- Keep last_contact timestamp for efficient querying
- Keep frequency_days for due date calculations
- Update validation and constructor
- Ensure frequency tracking works with Note-based updates
- Add methods for calculating next due date
- Consider contact_tags and note_tags relationships

#### Note Model Changes

- Ensure proper validation for content/interaction requirements:
  - If is_interaction is false, interaction_date must be null
  - If is_interaction is true, interaction_date must not be null
  - If is_interaction is false, content must not be null
- Add interaction_date field (not contact_date)
- Add is_interaction flag
- Update tag handling to trigger contact and tag timestamp updates
- Ensure proper relationship with note_tags junction table

### 2.2 ORM Layer

#### ContactORM Changes

- Rename last_interaction_at column to last_contact_at
- Update relationships and constraints
- Update migrations

#### TagORM Changes

- Remove last_contact_notes column
- Update relationships and constraints
- Update migrations

#### NoteORM Changes

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

### 2.3 Repository Layer

#### ContactRepository Changes

- Update contact creation/update logic
- Ensure proper handling of last_contact_at updates
- Update query methods

#### TagRepository Changes

- Update tag creation/update logic
- Ensure proper handling of last_contact updates
- Update query methods

#### NoteRepository Changes

- Add methods for interaction-specific queries
- Update note creation to handle interaction tracking
- Add validation for interaction dates

### 2.4 Test Updates

#### Domain Model Tests

- Update Contact tests to remove contact_briefing_text
- Update Tag tests to remove last_contact_notes
- Add Note tests for:
  - Content/interaction validation
  - Interaction date handling
  - Tag-based updates
  - Contact timestamp updates

#### Repository Tests

- Update Contact repository tests
- Update Tag repository tests
- Add Note repository tests for:
  - Interaction tracking
  - Contact updates
  - Tag updates

#### Integration Tests

- Test complete interaction flow
- Test timestamp updates
- Test tag-based tracking
- Test content vs interaction notes

## 3. Implementation Order

### Phase 1: Note Model (Core of Interaction Tracking)

1. Write Note Tests (RED)

   ```
   test_note_requires_either_content_or_interaction()
   test_interaction_note_requires_date()
   test_content_note_cannot_have_interaction_date()
   test_interaction_note_updates_contact_timestamp()
   test_interaction_note_updates_tag_timestamps()
   test_note_validation_edge_cases()
   ```

   Commit: "test: add Note model interaction tracking tests"

2. Implement Note Changes (GREEN)
   - Add is_interaction flag
   - Add interaction_date field
   - Implement validation rules
   - Add timestamp update logic
   Commit: "feat: implement Note model interaction tracking"

3. Refactor if needed
   Commit: "refactor: clean up Note model implementation"

### Phase 2: Tag Model (Frequency and Tracking)

1. Write Tag Tests (RED)

   ```
   test_tag_frequency_validation()
   test_tag_last_contact_updates()
   test_tag_next_contact_calculation()
   test_tag_staleness_check()
   ```

   Commit: "test: add Tag model frequency tracking tests"

2. Implement Tag Changes (GREEN)
   - Update timestamp handling
   - Add frequency calculations
   - Add next due date logic
   Commit: "feat: implement Tag model frequency tracking"

3. Refactor if needed
   Commit: "refactor: clean up Tag model implementation"

### Phase 3: Contact Model (Last Contact Tracking)

1. Write Contact Tests (RED)

   ```
   test_contact_last_contact_updates()
   test_contact_briefing_text_validation()
   test_contact_interaction_history()
   ```

   Commit: "test: add Contact model last contact tracking tests"

2. Implement Contact Changes (GREEN)
   - Rename to last_contact_at
   - Implement timestamp updates
   - Update validation
   Commit: "feat: implement Contact model last contact tracking"

3. Refactor if needed
   Commit: "refactor: clean up Contact model implementation"

### Phase 4: Integration Tests

Only after all individual models are tested and working:

1. Write Integration Tests (RED)

   ```
   test_complete_interaction_flow()
   test_frequency_based_tracking()
   test_contact_history_tracking()
   ```

   Commit: "test: add interaction tracking integration tests"

2. Fix Integration Issues (GREEN)
   - Adjust models as needed
   - Ensure proper interaction between objects
   Commit: "feat: implement interaction tracking integration"

3. Final Refactor if needed
   Commit: "refactor: clean up interaction tracking implementation"

Each phase follows:

1. Write failing tests first
2. Show tests failing
3. Implement minimum code to pass
4. Show tests passing
5. Commit
6. Move to next phase

No phase begins until previous phase is complete and all tests are green.

# User Stories - Contact Management

## 1. Basic Contact Management

### As a user, I want to manage contacts and their information
- US1.1: I want to create a new contact with just a name
- US1.2: I want to define a generic JSON template for my contact information
- US1.3: I want to add any kind of personal or biographical information
- US1.4: I want to delete contacts I no longer need
- US1.5: I want to only see filled JSON fields in View Mode
- US1.6: I want to add a briefing text to summarize key points about a contact, which can be AI generated.

### As a user, I want to organize my contacts with tags
- US1.7: I want to add hashtags to my contacts
- US1.8: I want to enable frequency tracking for specific tags
- US1.9: I want to see when I last contacted someone for each frequency-enabled tag
- US1.10: I want to see how stale my contacts are for each frequency-enabled tag

## 2. Notes and Reminders

### As a user, I want to capture information about contacts
- US2.1: I want to add notes about conversations and interactions
- US2.2: I want my notes to be broken down into clear statements
- US2.3: I want to review and edit the extracted statements
- US2.4: I want notes to update last contact dates for relevant tags
- US2.5: I want to tag individual statements for better organization
- US2.6: I want to see related statements by shared tags
- US2.7: I want tags to be preserved when notes are broken into statements

### As a user, I want to manage reminders
- US2.8: I want to set one-off reminders for specific contacts
- US2.9: I want to set recurring reminders (like birthdays)
- US2.10: I want to track completed reminders
- US2.11: I want to see reminders in context with related notes

## 3. Voice and AI Processing

### As a user, I want to use voice for input
- US3.1: I want to record voice notes about a contact
- US3.2: I want AI to transcribe my voice notes accurately
- US3.3: I want AI to extract statements from my notes
- US3.4: I want AI to identify information for JSON fields

### As a user, I want AI to help maintain contact information
- US3.5: I want AI to suggest updates to JSON fields from my statement notes
- US3.6: I want to review and approve AI-suggested updates
- US3.7: I want AI to summarize my notes
- US3.8: I want to see which statements will lead to which JSON updates
- US3.9: I want AI to suggest relevant tags for my statements
- US3.10: I want to see statements grouped by their tags

## 4. Template Management

### As a user, I want to manage information structure
- US4.1: I want to define categories in my JSON template
- US4.2: I want to define fields within categories
- US4.3: I want to modify the template when needed
- US4.4: I want my existing data about a person to be preserved when I update the template
- US4.5: I want to see the template version history

### As a user, I want to manage tag frequencies
- US4.6: I want to enable/disable frequency tracking for any tag
- US4.7: I want to set the expected contact frequency for a tag
- US4.8: I want to see all contacts with a specific tag
- US4.9: I want to see staleness status for frequency-enabled tags

## 5. Search and Organization

### As a user, I want to find and organize contacts
- US5.1: I want to search through all contact information
- US5.2: I want to filter contacts simply by max. one tag (no combinations)
- US5.3: I want to see contact interaction patterns
- US5.4: I want to find overdue contacts by tag
- US5.5: I want to sort contacts by staleness within a tag

## Acceptance Criteria Template

Each user story should include:

1. **Given** (Context)
   - Initial state
   - Relevant preconditions
   - Required setup

2. **When** (Action)
   - User actions
   - System triggers
   - Time-based events

3. **Then** (Outcome)
   - Expected results
   - System state changes
   - User notifications

4. **Additional Considerations**
   - Edge cases
   - Error conditions
   - Performance requirements

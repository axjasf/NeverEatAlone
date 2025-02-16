# Functional Requirements - Contact Management

## 1. Contact Information Structure

### 1.1 Basic Contact Information
- FR1.1.1: System MUST require a name for each contact
- FR1.1.2: System MUST track creation and update timestamps
- FR1.1.3: System MUST support contact briefing text
- FR1.1.4: System MUST track last interaction date at contact level
- FR1.1.5: System MUST track last interaction date per contact-tag combination

### 1.2 Sub-Information Management
- FR1.2.1: System MUST support a single user-defined JSON template with categories and fields
- FR1.2.2: System MUST validate information against the template
- FR1.2.3: System MUST support template evolution with the following constraints:
  - Field removal must preserve historical data
  - Field type changes must maintain data compatibility
- FR1.2.4: System MUST support manual JSON field updates
- FR1.2.5: System MUST only display filled JSON fields in view mode
- FR1.2.6: System MUST support metadata for fields in template including:
  - Field type (date, text, number, etc.)
  - Default reminder text template
  - Display format
  - Data validation rules
- FR1.2.7: System MUST allow creating independent reminders from any field with optional use of template text

## 2. Tag System

### 2.1 Basic Tag Functionality
- FR2.1.1: System MUST support tag creation with # prefix
- FR2.1.2: System MUST normalize tags to lowercase
- FR2.1.3: System MUST prevent duplicate tags per contact
- FR2.1.4: System MUST support assigning multiple tags to contacts
- FR2.1.5: System MUST support tagging notes for context

### 2.2 Contact Frequency Tracking
- FR2.2.1: System MUST support optional contact frequency setting per contact-tag combination
- FR2.2.2: System MUST track last contact date per contact-tag combination
- FR2.2.3: System MUST calculate staleness for each frequency-enabled tag independently
- FR2.2.4: System MUST allow enabling/disabling frequency tracking for any contact-tag combination
- FR2.2.5: System MUST update contact-tag last contact dates only from interaction notes
- FR2.2.6: System MUST update general contact last interaction date from any interaction note

## 3. Note and Interaction System

### 3.1 Note Management
- FR3.1.1: System MUST support two types of notes:
  - Content notes with actual information
  - Pure interaction records without content
- FR3.1.2: System MUST require either content or interaction flag for notes
- FR3.1.3: System MUST allow tagging notes for context
- FR3.1.4: System MUST update relevant contact tracking based on interaction notes
- FR3.1.5: System MUST maintain accurate timestamps for all interactions
- FR3.1.6: System MUST allow filtering notes by type (content vs interaction)
- FR3.1.7: System MUST allow filtering notes by tags

### 3.2 Interaction Tracking
- FR3.2.1: System MUST update contact's last_interaction_at when creating interaction notes
- FR3.2.2: System MUST update contact-tag last_contact dates based on note tags
- FR3.2.3: System MUST support recording interactions without content
- FR3.2.4: System MUST maintain interaction history with tags
- FR3.2.5: System MUST validate interaction dates
- FR3.2.6: System MUST prevent future interaction dates

### 3.3 Information Extraction
- FR3.3.1: System MUST analyze statements for JSON-compatible information
- FR3.3.2: System MUST suggest updates to JSON fields based on statements
- FR3.3.3: System MUST match extracted information to template fields
- FR3.3.4: System MUST require user approval for suggested updates
- FR3.3.5: System MUST show which statements will lead to which JSON updates
- FR3.3.6: System MUST detect potential reminder triggers in notes and suggest creating reminders with field reference
- FR3.3.7: System MUST suggest relevant tags for statements based on content
- FR3.3.8: System MUST maintain tag context when suggesting JSON updates

## 4. Dashboard and Display

### 4.1 Contact Dashboard
- FR4.1.1: System MUST show contacts grouped by tags
- FR4.1.2: System MUST display contact staleness per frequency-enabled tag
- FR4.1.3: System MUST highlight overdue contacts with staleness duration
- FR4.1.4: System MUST show upcoming date-based reminders with related past notes
- FR4.1.5: System MUST provide notifications for overdue contacts and upcoming dates

### 4.2 Information Display
- FR4.2.1: System MUST show only filled JSON fields in view mode
- FR4.2.2: System MUST show notes referencing the same fields as a reminder
- FR4.2.3: System MUST show interaction patterns and frequency
- FR4.2.4: System MUST show tag memberships with last contact dates
- FR4.2.5: System MUST provide a calendar view integrating all types of reminders
- FR4.2.6: System MUST show field metadata including reminder templates when editing template

### 4.3 Management Interface
- FR4.3.1: System MUST provide UI for manual JSON field updates
- FR4.3.2: System MUST provide UI for template definition and modification including field metadata
- FR4.3.3: System MUST provide UI for tag management including frequency settings
- FR4.3.4: System MUST provide UI for creating and editing reminders with template text suggestions

# Functional Requirements - Contact Management

## 1. Contact Information Structure

### 1.1 Basic Contact Information
- FR1.1.1: System MUST require a name for each contact
- FR1.1.2: System MUST track creation and update timestamps
- FR1.1.3: System MUST support contact briefing text

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
- FR2.1.3: System MUST prevent duplicate tags
- FR2.1.4: System MUST support assigning multiple tags to contacts

### 2.2 Reminder Functionality
- FR2.2.1: System MUST support optional contact frequency setting per tag
- FR2.2.2: System MUST track last contact date per contact-tag combination
- FR2.2.3: System MUST calculate staleness for each frequency-enabled tag independently
- FR2.2.4: System MUST allow enabling/disabling frequency tracking for any tag
- FR2.2.5: System MUST maintain reminders independently from their source fields

### 2.3 Tag Management
- FR2.3.1: System MUST support adding/removing tags from contacts
- FR2.3.2: System MUST provide tag-based contact filtering
- FR2.3.3: System MUST display contacts by tag with staleness information when frequency is enabled
- FR2.3.4: System MUST track single frequency setting per frequency-enabled tag

## 3. Note and Interaction System

### 3.1 Note Management
- FR3.1.1: System MUST support note creation with content and date
- FR3.1.2: System MUST allow referencing JSON fields in notes for context
- FR3.1.3: System MUST allow tagging notes for context
- FR3.1.4: System MUST break down notes into statements
- FR3.1.5: System MUST maintain link between notes and statements
- FR3.1.6: System MUST allow editing of statements
- FR3.1.7: System MUST support tagging individual statements
- FR3.1.8: System MUST maintain tag relationships when splitting notes into statements
- FR3.1.9: System MUST allow filtering statements by tags

### 3.2 Voice Processing
- FR3.2.1: System MUST transcribe voice notes to text
- FR3.2.2: System MUST extract individual statements from transcribed text
- FR3.2.3: System MUST summarize notes
- FR3.2.4: System MUST identify key information in statements

### 3.3 Information Extraction
- FR3.3.1: System MUST analyze statements for JSON-compatible information
- FR3.3.2: System MUST suggest updates to JSON fields based on statements
- FR3.3.3: System MUST match extracted information to template fields
- FR3.3.4: System MUST require user approval for suggested updates
- FR3.3.5: System MUST show which statements will lead to which JSON updates
- FR3.3.6: System MUST detect potential reminder triggers in notes and suggest creating reminders with field reference
- FR3.3.7: System MUST suggest relevant tags for statements based on content
- FR3.3.8: System MUST maintain tag context when suggesting JSON updates

### 3.4 Interaction Tracking
- FR3.4.1: System MUST use notes to track all contact interactions
- FR3.4.2: System MUST update relevant contact-tag last contact dates based on notes
- FR3.4.3: System MUST support querying interaction history by tags and fields
- FR3.4.4: System MUST enable rich context searching across notes

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

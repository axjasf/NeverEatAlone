# Functional Requirements - Contact Management

## 1. Contact Information Structure

### 1.1 Basic Contact Information
- FR1.1.1: System MUST require a name for each contact
- FR1.1.2: System MUST track last contact date
- FR1.1.3: System MUST track creation and update timestamps
- FR1.1.4: System MUST support contact briefing text

### 1.2 JSON Information
- FR1.2.1: System MUST support a single user-defined JSON template with categories and fields
- FR1.2.2: System MUST validate information against the template
- FR1.2.3: System MUST allow template modification
- FR1.2.4: System MUST support manual JSON field updates
- FR1.2.5: System MUST only display filled JSON fields in view mode

### 1.3 Organization
- FR1.3.1: System MUST support hashtag assignment
- FR1.3.2: System MUST support organizing contacts into rings
- FR1.3.3: System MUST track ring-specific information
- FR1.3.4: System MUST support multiple rings per contact

## 2. Notes and Reminders

### 2.1 Note Management
- FR2.1.1: System MUST support adding notes to contacts
- FR2.1.2: System MUST break down notes into statements
- FR2.1.3: System MUST maintain link between notes and statements
- FR2.1.4: System MUST allow editing of statements

### 2.2 Reminder System
- FR2.2.1: System MUST support one-off reminders
- FR2.2.2: System MUST support recurring reminders (e.g., birthdays)
- FR2.2.3: System MUST support ring-based reminders (e.g., call every 30 days)
- FR2.2.4: System MUST track reminder completion

## 3. AI Processing

### 3.1 Voice Processing
- FR3.1.1: System MUST transcribe voice notes to text
- FR3.1.2: System MUST extract individual statements from transcribed text
- FR3.1.3: System MUST summarize notes
- FR3.1.4: System MUST identify key information in statements

### 3.2 Information Extraction
- FR3.2.1: System MUST analyze statements for JSON-compatible information
- FR3.2.2: System MUST suggest updates to JSON fields based on statements
- FR3.2.3: System MUST match extracted information to template fields
- FR3.2.4: System MUST require user approval for suggested updates
- FR3.2.5: System MUST show which statements will lead to which JSON updates

## 4. User Interface

### 4.1 Contact Management
- FR4.1.1: System MUST provide UI for manual JSON field updates
- FR4.1.2: System MUST provide UI for template definition and modification
- FR4.1.3: System MUST provide UI for ring management
- FR4.1.4: System MUST provide UI for reminder management

### 4.2 Information Display
- FR4.2.1: System MUST show only filled JSON fields in view mode
- FR4.2.2: System MUST show notes and statements
- FR4.2.3: System MUST show upcoming reminders
- FR4.2.4: System MUST show ring memberships

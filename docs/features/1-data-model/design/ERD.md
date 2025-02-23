# Entity Relationship Diagram

## Overview
This is a Mermaid-based ERD complementing the detailed technical ERD in `erd.drawio`. This version focuses on core entities and relationships for quick reference.

## Core Data Model

```mermaid
erDiagram
    Contact {
        UUID id PK
        string name
        string first_name
        string briefing_text
        json sub_information "Flexible custom fields"
        datetime last_contact UTC
        string contact_briefing_text
        datetime created_at UTC
        datetime updated_at UTC
    }

    Note {
        UUID id PK
        UUID contact_id FK
        string content "Optional for interactions"
        boolean is_interaction
        datetime interaction_date "UTC, Required if is_interaction"
        datetime created_at UTC
        datetime updated_at UTC
    }

    Statement {
        UUID id PK
        UUID note_id FK
        int sequence_number
        string content Required
        datetime created_at UTC
        datetime updated_at UTC
    }

    Tag {
        UUID id PK
        UUID entity_id FK "What it's attached to"
        string entity_type "contact/note/statement"
        string name "Starts with #"
        int frequency_days Optional
        datetime frequency_last_updated UTC
        datetime last_contact UTC
        datetime created_at UTC
        datetime updated_at UTC
    }

    Reminder {
        UUID id PK
        UUID contact_id FK
        UUID note_id FK "Optional"
        string title
        string description Optional
        datetime due_date UTC
        string status "PENDING/COMPLETED"
        datetime completion_date "UTC, Required if completed"
        string due_date_timezone
        string completion_date_timezone
        int recurrence_interval Optional
        string recurrence_unit "DAY/WEEK/MONTH/YEAR"
        datetime recurrence_end_date "UTC, Optional"
        datetime created_at UTC
        datetime updated_at UTC
    }

    TemplateVersion {
        UUID id PK
        int version
        json categories "Field definitions"
        json removed_fields "Tracking changes"
        datetime created_at UTC
        datetime updated_at UTC
    }

    ContactTag {
        UUID contact_id FK
        UUID tag_id FK
    }

    NoteTag {
        UUID note_id FK
        UUID tag_id FK
    }

    StatementTag {
        UUID statement_id FK
        UUID tag_id FK
    }

    Contact ||--o{ Note : "has"
    Note ||--o{ Statement : "contains"
    Contact ||--o{ Reminder : "has"
    Note ||--o{ Reminder : "has"
    Contact ||--o{ ContactTag : "has"
    Note ||--o{ NoteTag : "has"
    Statement ||--o{ StatementTag : "has"
    ContactTag }o--|| Tag : "used_in"
    NoteTag }o--|| Tag : "used_in"
    StatementTag }o--|| Tag : "used_in"
    Contact ||--|| TemplateVersion : "validates_against"
```

## Key Points
- All entities inherit from BaseModel with `id`, `created_at`, and `updated_at` in UTC
- Tags use polymorphic associations through junction tables and `entity_type`
- Statement ordering is maintained through `sequence_number`
- Reminders support flexible recurrence patterns
- Template versioning tracks field definitions and changes
- Notes can be regular notes or interactions (tracked separately)
- All timestamps are stored in UTC, with timezone context where needed

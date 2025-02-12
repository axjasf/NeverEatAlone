# Data Model - Contact Management

## 1. Database Schema

### 1.1 Core Tables

#### Contact
```sql
CREATE TABLE contacts (
    id UUID PRIMARY KEY,
    name VARCHAR NOT NULL,
    first_name VARCHAR,
    sub_information JSON NOT NULL DEFAULT '{}',
    briefing_text TEXT,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

CREATE INDEX idx_contacts_name ON contacts(name);
CREATE INDEX idx_contacts_created ON contacts(created_at DESC);
```

#### Tags
```sql
CREATE TABLE tags (
    entity_id UUID NOT NULL,
    entity_type VARCHAR NOT NULL CHECK (entity_type IN ('contact', 'note', 'statement')),
    name VARCHAR NOT NULL,
    frequency_days INTEGER,
    last_contact TIMESTAMP,
    created_at TIMESTAMP NOT NULL,
    PRIMARY KEY (entity_id, entity_type, name),
    CONSTRAINT fk_entity
        CHECK (
            (entity_type = 'contact' AND EXISTS (SELECT 1 FROM contacts WHERE id = entity_id)) OR
            (entity_type = 'note' AND EXISTS (SELECT 1 FROM notes WHERE id = entity_id)) OR
            (entity_type = 'statement' AND EXISTS (SELECT 1 FROM statements WHERE id = entity_id))
        )
);

CREATE INDEX idx_tags_name ON tags(name);
CREATE INDEX idx_tags_frequency ON tags(frequency_days) WHERE frequency_days IS NOT NULL;
CREATE INDEX idx_tags_last_contact ON tags(last_contact);
CREATE INDEX idx_tags_entity ON tags(entity_type, entity_id);
```

### 1.2 Notes and Statements
```sql
CREATE TABLE notes (
    id UUID PRIMARY KEY,
    contact_id UUID NOT NULL,
    text TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE
);

CREATE TABLE statements (
    id UUID PRIMARY KEY,
    note_id UUID NOT NULL,
    text TEXT NOT NULL,
    suggested_updates JSON,
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE CASCADE
);

CREATE INDEX idx_notes_contact ON notes(contact_id);
CREATE INDEX idx_statements_note ON statements(note_id);
```

### 1.3 Reminders
```sql
CREATE TABLE reminders (
    id UUID PRIMARY KEY,
    contact_id UUID NOT NULL,
    tag_name VARCHAR,
    title TEXT NOT NULL,
    due_date TIMESTAMP NOT NULL,
    recurring_type VARCHAR,  -- null, daily, weekly, monthly, yearly
    recurring_interval INTEGER,
    completed_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE,
    FOREIGN KEY (contact_id, tag_name) REFERENCES tags(contact_id, name)
);

CREATE INDEX idx_reminders_contact ON reminders(contact_id);
CREATE INDEX idx_reminders_tag ON reminders(contact_id, tag_name);
CREATE INDEX idx_reminders_due ON reminders(due_date);
```

### 1.4 Template Management
```sql
CREATE TABLE template_versions (
    id UUID PRIMARY KEY,
    version INTEGER NOT NULL,
    categories JSON NOT NULL,
    created_at TIMESTAMP NOT NULL,
    UNIQUE(version)
);

CREATE INDEX idx_template_versions_version ON template_versions(version DESC);
```

## 2. Object Models

### 2.1 Core Models

#### Contact Model
```python
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel

class Contact(BaseModel):
    """
    Represents a contact in the system.

    Attributes:
        id (UUID): Unique identifier
        name (str): Required full name
        first_name (Optional[str]): Optional first name
        sub_information (Dict[str, Any]): Template-specific data
        briefing_text (Optional[str]): Contact summary (can be AI-generated)
        created_at (datetime): Creation timestamp
        updated_at (datetime): Last update timestamp
    """
    id: UUID
    name: str
    first_name: Optional[str] = None
    sub_information: Dict[str, Any] = {}
    briefing_text: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class Tag(BaseModel):
    """
    Represents a tag associated with an entity (contact, note, or statement).

    Attributes:
        entity_id (UUID): Entity this tag belongs to (contact, note, or statement ID)
        entity_type (str): Type of entity ('contact', 'note', or 'statement')
        name (str): Tag name (starts with #)
        frequency_days (Optional[int]): Days between expected contacts (contacts only)
        last_contact (Optional[datetime]): Last contact date for this tag
        created_at (datetime): When this tag was added
    """
    entity_id: UUID
    entity_type: str
    name: str
    frequency_days: Optional[int] = None
    last_contact: Optional[datetime] = None
    created_at: datetime

class TemplateVersion(BaseModel):
    """
    Represents a version of the contact information template.

    Attributes:
        id (UUID): Unique identifier
        version (int): Sequential version number
        categories (Dict[str, Any]): Template structure with field definitions
        created_at (datetime): When this version was created
    """
    id: UUID
    version: int
    categories: Dict[str, Any]
    created_at: datetime
```

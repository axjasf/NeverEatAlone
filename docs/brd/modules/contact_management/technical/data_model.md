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
    hashtags JSON NOT NULL DEFAULT '[]',
    briefing_text TEXT,
    last_contact TIMESTAMP,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

CREATE INDEX idx_contacts_name ON contacts(name);
CREATE INDEX idx_contacts_created ON contacts(created_at DESC);
CREATE INDEX idx_contacts_last_contact ON contacts(last_contact DESC);
```

#### Template
```sql
CREATE TABLE template (
    categories JSON NOT NULL DEFAULT '{}',
    updated_at TIMESTAMP NOT NULL
);
```

### 1.2 Notes and Statements
```sql
CREATE TABLE notes (
    id UUID PRIMARY KEY,
    contact_id UUID NOT NULL,
    text TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (contact_id) REFERENCES contacts(id)
);

CREATE TABLE statements (
    id UUID PRIMARY KEY,
    note_id UUID NOT NULL,
    text TEXT NOT NULL,
    suggested_updates JSON,
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (note_id) REFERENCES notes(id)
);

CREATE INDEX idx_notes_contact ON notes(contact_id);
CREATE INDEX idx_statements_note ON statements(note_id);
```

### 1.3 Rings and Reminders
```sql
CREATE TABLE rings (
    id UUID PRIMARY KEY,
    name VARCHAR NOT NULL,
    frequency_days INTEGER,
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE contact_rings (
    contact_id UUID NOT NULL,
    ring_id UUID NOT NULL,
    joined_at TIMESTAMP NOT NULL,
    PRIMARY KEY (contact_id, ring_id),
    FOREIGN KEY (contact_id) REFERENCES contacts(id),
    FOREIGN KEY (ring_id) REFERENCES rings(id)
);

CREATE TABLE reminders (
    id UUID PRIMARY KEY,
    contact_id UUID NOT NULL,
    ring_id UUID,
    title TEXT NOT NULL,
    due_date TIMESTAMP NOT NULL,
    recurring_type VARCHAR,  -- null, daily, weekly, monthly, yearly
    recurring_interval INTEGER,
    completed_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (contact_id) REFERENCES contacts(id),
    FOREIGN KEY (ring_id) REFERENCES rings(id)
);

CREATE INDEX idx_contact_rings_contact ON contact_rings(contact_id);
CREATE INDEX idx_contact_rings_ring ON contact_rings(ring_id);
CREATE INDEX idx_reminders_contact ON reminders(contact_id);
CREATE INDEX idx_reminders_ring ON reminders(ring_id);
CREATE INDEX idx_reminders_due ON reminders(due_date);
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
        hashtags (List[str]): Associated hashtags
        briefing_text (Optional[str]): Contact summary
        last_contact (Optional[datetime]): When you last had any contact (call, meeting, email)
        created_at (datetime): Creation timestamp
        updated_at (datetime): Last update timestamp
    """
    id: UUID
    name: str
    first_name: Optional[str] = None
    sub_information: Dict[str, Any] = {}
    hashtags: List[str] = []
    briefing_text: Optional[str] = None
    last_contact: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
```

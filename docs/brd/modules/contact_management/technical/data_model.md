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
    last_interaction_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE INDEX idx_contacts_name ON contacts(name);
CREATE INDEX idx_contacts_created ON contacts(created_at DESC);
CREATE INDEX idx_contacts_last_interaction ON contacts(last_interaction_at DESC);
```

#### Contact Tags
```sql
CREATE TABLE contact_tags (
    contact_id UUID NOT NULL,
    tag_name VARCHAR NOT NULL,
    frequency_days INTEGER,
    last_contact TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    PRIMARY KEY (contact_id, tag_name),
    FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE
);

CREATE INDEX idx_contact_tags_name ON contact_tags(tag_name);
CREATE INDEX idx_contact_tags_frequency ON contact_tags(frequency_days) WHERE frequency_days IS NOT NULL;
CREATE INDEX idx_contact_tags_last_contact ON contact_tags(last_contact);
```

### 1.2 Notes and Statements
```sql
CREATE TABLE notes (
    id UUID PRIMARY KEY,
    contact_id UUID NOT NULL,
    content TEXT,
    is_interaction BOOLEAN NOT NULL DEFAULT FALSE,
    interaction_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE,
    CONSTRAINT valid_interaction CHECK (
        (is_interaction = FALSE AND interaction_date IS NULL) OR
        (is_interaction = TRUE AND interaction_date IS NOT NULL)
    ),
    CONSTRAINT valid_content CHECK (
        (is_interaction = TRUE) OR
        (is_interaction = FALSE AND content IS NOT NULL)
    )
);

CREATE TABLE note_tags (
    note_id UUID NOT NULL,
    tag_name VARCHAR NOT NULL,
    PRIMARY KEY (note_id, tag_name),
    FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE CASCADE
);

CREATE INDEX idx_notes_contact ON notes(contact_id);
CREATE INDEX idx_notes_interaction ON notes(is_interaction, interaction_date);
CREATE INDEX idx_note_tags_name ON note_tags(tag_name);
```

### 1.3 Reminders
```sql
CREATE TABLE reminders (
    id UUID PRIMARY KEY,
    contact_id UUID NOT NULL,
    tag_name VARCHAR,
    title TEXT NOT NULL,
    due_date TIMESTAMP WITH TIME ZONE NOT NULL,
    recurring_type VARCHAR,  -- null, daily, weekly, monthly, yearly
    recurring_interval INTEGER,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
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
        last_interaction_at (Optional[datetime]): Last actual interaction
        tags (List[ContactTag]): Tags with their frequencies and last contacts
        created_at (datetime): Creation timestamp
        updated_at (datetime): Last update timestamp
    """
    id: UUID
    name: str
    first_name: Optional[str] = None
    sub_information: Dict[str, Any] = {}
    briefing_text: Optional[str] = None
    last_interaction_at: Optional[datetime] = None
    tags: List['ContactTag'] = []
    created_at: datetime
    updated_at: datetime

class ContactTag(BaseModel):
    """
    Represents a tag associated with a contact, including frequency settings.

    Attributes:
        contact_id (UUID): The contact this tag belongs to
        name (str): Tag name (starts with #)
        frequency_days (Optional[int]): Days between expected contacts
        last_contact (Optional[datetime]): Last contact date for this tag
        created_at (datetime): When this tag was added
    """
    contact_id: UUID
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

class Note(BaseModel):
    """
    Represents a note about a contact.

    Attributes:
        id (UUID): Unique identifier
        contact_id (UUID): Associated contact
        content (Optional[str]): Note content (required for non-interaction notes)
        is_interaction (bool): Whether this note represents actual contact
        interaction_date (Optional[datetime]): When the interaction occurred
        tags (List[str]): Associated tags
        created_at (datetime): Creation timestamp
    """
    id: UUID
    contact_id: UUID
    content: Optional[str] = None
    is_interaction: bool = False
    interaction_date: Optional[datetime] = None
    tags: List[str] = []
    created_at: datetime
```

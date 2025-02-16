# Technical Architecture - Contact Management

## 1. System Architecture

### 1.1 Component Overview
```mermaid
graph TD
    A[Contact Management API] --> B[Template Engine]
    A --> C[Data Storage]
    A --> D[Search Engine]
    A --> E[Integration Layer]
    A --> F[Interaction Tracking]
    B --> G[Template Repository]
    C --> H[SQLite Database]
    D --> I[Search Index]
    E --> J[External Services]
    F --> K[Contact Tracking]
    F --> L[Topic Tracking]
```

### 1.2 Key Components

1. **Contact Management API**
   - RESTful endpoints
   - GraphQL interface
   - WebSocket notifications
   - Authentication middleware
   - Interaction validation

2. **Template Engine**
   - Template validation
   - Version management
   - Migration tools
   - Custom field types

3. **Data Storage**
   - SQLite with JSON support
   - ACID compliance
   - Optimized queries
   - Caching layer

4. **Search Engine**
   - Full-text search
   - Tag-based search
   - Interaction history search
   - Contact staleness search

5. **Integration Layer**
   - Service adapters
   - Protocol handlers
   - Data transformers
   - Event system

6. **Interaction Tracking**
   - Two-level tracking:
     - Contact level
     - Topic level (tags)
   - Frequency monitoring
   - Staleness calculation
   - Interaction validation

## 2. Data Architecture

### 2.1 Core Entities
```mermaid
erDiagram
    Contact ||--o{ Note : has
    Contact ||--o{ ContactTag : has
    Note ||--o{ NoteTag : has
    ContactTag }|--o{ NoteTag : updates
```

### 2.2 Data Flow

#### 2.2.1 Interaction Recording Flow
```mermaid
sequenceDiagram
    participant U as User
    participant A as API
    participant V as Validator
    participant T as Tracking
    participant D as Database

    U->>A: Record Interaction
    A->>V: Validate Interaction
    V-->>A: Validation Result
    A->>T: Process Interaction
    T->>D: Update Contact Tracking
    T->>D: Update Topic Tracking
    D-->>A: Confirmation
    A->>U: Response
```

#### 2.2.2 Contact Update Flow
```mermaid
sequenceDiagram
    participant U as User
    participant A as API
    participant T as Tracking
    participant D as Database

    U->>A: Update Contact
    A->>T: Check Frequencies
    T->>D: Update Tracking
    D-->>A: Confirmation
    A->>U: Response
```

## 3. Implementation Details

### 3.1 Contact Model
```python
class Contact(BaseModel):
    id: UUID
    name: str
    first_name: Optional[str]
    sub_information: Dict[str, Any]
    tags: List[ContactTag]
    last_interaction_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
```

### 3.2 Note Model
```python
class Note(BaseModel):
    id: UUID
    contact_id: UUID
    content: Optional[str]
    is_interaction: bool
    interaction_date: Optional[datetime]
    tags: List[str]
    created_at: datetime
```

### 3.3 ContactTag Model
```python
class ContactTag(BaseModel):
    contact_id: UUID
    name: str
    frequency_days: Optional[int]
    last_contact: Optional[datetime]
    created_at: datetime
```

### 3.4 Template Model
```python
class Template(BaseModel):
    categories: Dict[str, CategoryDefinition]
    updated_at: datetime
    version: int  # For tracking template evolution
```

### 3.5 Field Definition
```python
class FieldDefinition(BaseModel):
    type: str  # string, number, date, boolean
    description: str
    display_format: Optional[str]
    reminder_template: Optional[str]
    validators: Optional[List[str]]
```

## 4. API Design

### 4.1 REST Endpoints
```plaintext
# Contact Management
POST   /api/contacts              # Create contact
GET    /api/contacts/{id}         # Get contact
PUT    /api/contacts/{id}         # Update contact
DELETE /api/contacts/{id}         # Delete contact
GET    /api/contacts/search       # Search contacts

# Note Management
POST   /api/notes                 # Create note
PUT    /api/notes/{id}            # Update note
GET    /api/notes/search          # Search notes
GET    /api/notes/interactions    # Get interaction notes

# Tag Management
GET    /api/tags                  # List all tags
PUT    /api/tags/{name}          # Update tag
GET    /api/tags/{name}/contacts # List contacts with tag

# Template Management
GET    /api/template             # Get current template
PUT    /api/template             # Update template with version
```

### 4.2 GraphQL Schema
```graphql
type Contact {
    id: ID!
    name: String!
    firstName: String
    subInformation: JSON
    hashtags: [String!]
    briefingText: String
    lastInteractionAt: DateTime
    createdAt: DateTime!
    updatedAt: DateTime!
}

type Note {
    id: ID!
    contactId: ID!
    content: String!
    isInteraction: Boolean!
    interactionDate: DateTime
    tags: [String!]
    createdAt: DateTime!
}

type Query {
    contact(id: ID!): Contact
    contactNotes(
        contactId: ID!
        isInteraction: Boolean
    ): [Note!]!
}

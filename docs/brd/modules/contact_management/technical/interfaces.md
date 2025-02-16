# Interfaces - Contact Management

## 1. REST API

### 1.1 Contact Management

#### Create Contact
```http
POST /api/contacts
Content-Type: application/json
Authorization: Bearer {token}

{
    "name": "string",
    "first_name": "string",
    "sub_information": {},
    "hashtags": ["string"],
    "briefing_text": "string"
}

Response 201:
{
    "id": "uuid",
    "name": "string",
    "first_name": "string",
    "sub_information": {},
    "hashtags": ["string"],
    "briefing_text": "string",
    "last_interaction_at": "datetime?",
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

#### Get Contact
```http
GET /api/contacts/{id}
Authorization: Bearer {token}

Response 200:
{
    "id": "uuid",
    "name": "string",
    "first_name": "string",
    "sub_information": {},
    "hashtags": ["string"],
    "contact_briefing_text": "string",
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

#### Update Contact
```http
PUT /api/contacts/{id}
Content-Type: application/json
Authorization: Bearer {token}

{
    "name": "string",
    "first_name": "string",
    "sub_information": {},
    "hashtags": ["string"],
    "contact_briefing_text": "string"
}

Response 200:
{
    "id": "uuid",
    "name": "string",
    "first_name": "string",
    "sub_information": {},
    "hashtags": ["string"],
    "contact_briefing_text": "string",
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

#### Delete Contact
```http
DELETE /api/contacts/{id}
Authorization: Bearer {token}

Response 204
```

### 1.2 Note Management

#### Create Note
```http
POST /api/notes
Content-Type: application/json
Authorization: Bearer {token}

{
    "contact_id": "uuid",
    "content": "string",
    "is_interaction": "boolean",
    "interaction_date": "datetime?",
    "tags": ["string"]
}

Response 201:
{
    "id": "uuid",
    "contact_id": "uuid",
    "content": "string",
    "is_interaction": "boolean",
    "interaction_date": "datetime?",
    "tags": ["string"],
    "created_at": "datetime"
}
```

#### Update Note
```http
PUT /api/notes/{id}
Content-Type: application/json
Authorization: Bearer {token}

{
    "content": "string",
    "is_interaction": "boolean",
    "interaction_date": "datetime?",
    "tags": ["string"]
}

Response 200:
{
    "id": "uuid",
    "contact_id": "uuid",
    "content": "string",
    "is_interaction": "boolean",
    "interaction_date": "datetime?",
    "tags": ["string"],
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

#### Search Notes
```http
GET /api/notes/search
Authorization: Bearer {token}

Query Parameters:
- contact_id: "uuid?"
- is_interaction: "boolean?"
- from_date: "datetime?"
- to_date: "datetime?"
- tags: "string[]?"
- page: "number?"
- limit: "number?"

Response 200:
{
    "items": [
        {
            "id": "uuid",
            "contact_id": "uuid",
            "content": "string",
            "is_interaction": "boolean",
            "interaction_date": "datetime?",
            "tags": ["string"],
            "created_at": "datetime"
        }
    ],
    "total_count": "number",
    "page": "number",
    "limit": "number"
}
```

#### Get Interaction History
```http
GET /api/notes/interactions
Authorization: Bearer {token}

Query Parameters:
- contact_id: "uuid?"
- tags: "string[]?"
- from_date: "datetime?"
- to_date: "datetime?"
- page: "number?"
- limit: "number?"

Response 200:
{
    "items": [
        {
            "id": "uuid",
            "contact_id": "uuid",
            "content": "string",
            "interaction_date": "datetime",
            "tags": ["string"],
            "created_at": "datetime"
        }
    ],
    "total_count": "number",
    "page": "number",
    "limit": "number"
}
```

### 1.3 Tag Management

#### List Tags
```http
GET /api/tags
Authorization: Bearer {token}

Response 200:
{
    "items": [
        {
            "name": "string",
            "frequency_days": "number?",
            "entity_type": "string",
            "last_contact": "datetime?",
            "created_at": "datetime"
        }
    ],
    "total_count": "number"
}
```

#### Update Tag
```http
PUT /api/tags/{name}
Content-Type: application/json
Authorization: Bearer {token}

{
    "frequency_days": "number?"
}

Response 200:
{
    "name": "string",
    "frequency_days": "number?",
    "entity_type": "string",
    "created_at": "datetime"
}
```

#### List Contacts by Tag
```http
GET /api/tags/{name}/contacts
Authorization: Bearer {token}

Response 200:
{
    "items": [
        {
            "id": "uuid",
            "name": "string",
            "first_name": "string",
            "sub_information": {},
            "hashtags": ["string"],
            "contact_briefing_text": "string",
            "created_at": "datetime",
            "updated_at": "datetime",
            "staleness_days": "number?"
        }
    ],
    "total_count": "number"
}
```

### 1.4 Template Management

#### Get Template
```http
GET /api/template
Authorization: Bearer {token}

Response 200:
{
    "categories": {
        "category_name": {
            "fields": {
                "field_name": {
                    "type": "string",
                    "description": "string",
                    "display_format": "string?",
                    "reminder_template": "string?",
                    "validators": ["string"]
                }
            }
        }
    },
    "version": "number",
    "updated_at": "datetime"
}
```

#### Update Template
```http
PUT /api/template
Content-Type: application/json
Authorization: Bearer {token}

{
    "categories": {
        "category_name": {
            "fields": {
                "field_name": {
                    "type": "string",
                    "description": "string",
                    "display_format": "string?",
                    "reminder_template": "string?",
                    "validators": ["string"]
                }
            }
        }
    }
}

Response 200:
{
    "categories": {
        "category_name": {
            "fields": {
                "field_name": {
                    "type": "string",
                    "description": "string",
                    "display_format": "string?",
                    "reminder_template": "string?",
                    "validators": ["string"]
                }
            }
        }
    },
    "version": "number",
    "updated_at": "datetime"
}
```

## 2. GraphQL API

### 2.1 Schema
```graphql
type Contact {
    id: ID!
    name: String!
    firstName: String
    subInformation: JSON
    hashtags: [String!]
    contactBriefingText: String
    createdAt: DateTime!
    updatedAt: DateTime!
}

type Tag {
    name: String!
    frequencyDays: Int
    entityType: String!
    createdAt: DateTime!
}

type Template {
    categories: JSON!
    version: Int!
    updatedAt: DateTime!
}

type Query {
    contact(id: ID!): Contact
    contacts(
        search: String
        hashtags: [String!]
        page: Int
        pageSize: Int
    ): [Contact!]!
    tags: [Tag!]!
    tagContacts(name: String!): [Contact!]!
    template: Template!
}

type Mutation {
    createContact(input: CreateContactInput!): Contact!
    updateContact(id: ID!, input: UpdateContactInput!): Contact!
    deleteContact(id: ID!): Boolean!
    updateTag(name: String!, input: UpdateTagInput!): Tag!
    updateTemplate(input: UpdateTemplateInput!): Template!
}

input CreateContactInput {
    name: String!
    firstName: String
    subInformation: JSON
    hashtags: [String!]
    contactBriefingText: String
}

input UpdateContactInput {
    name: String
    firstName: String
    subInformation: JSON
    hashtags: [String!]
    contactBriefingText: String
}

input UpdateTagInput {
    frequencyDays: Int
}

input UpdateTemplateInput {
    categories: JSON!
}
```

## 3. Event System

### 3.1 Contact Events
```typescript
interface ContactEvent {
    type: "CREATED" | "UPDATED" | "DELETED";
    contactId: string;
    timestamp: string;
    data: {
        before?: Contact;
        after?: Contact;
    };
}
```

### 3.2 Tag Events
```typescript
interface TagEvent {
    type: "FREQUENCY_ENABLED" | "FREQUENCY_DISABLED" | "FREQUENCY_UPDATED" | "TAGGED" | "UNTAGGED";
    tagName: string;
    timestamp: string;
    entityType: "contact" | "note" | "statement";
    entityId: string;
    data: {
        before?: Tag;
        after?: Tag;
    };
}
```

### 3.3 Template Events
```typescript
interface TemplateEvent {
    type: "UPDATED";
    timestamp: string;
    version: number;
    data: {
        before?: Template;
        after?: Template;
    };
}
```

### 3.4 Statement Events
```typescript
interface StatementEvent {
    type: "CREATED" | "UPDATED";
    statementId: string;
    timestamp: string;
    data: {
        before?: Statement;
        after?: Statement;
    };
}
```

## 4. Voice Processing Interface
```typescript
interface VoiceProcessor {
    processVoiceNote(audioData: Buffer): Promise<{
        text: string;
        statements: string[];
        suggestedUpdates: {
            fieldPath: string;
            value: any;
            sourceStatement: string;
        }[];
    }>;
}
```

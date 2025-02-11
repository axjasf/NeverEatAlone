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
    "last_contact": "datetime"
}

Response 201:
{
    "id": "uuid",
    "name": "string",
    "first_name": "string",
    "sub_information": {},
    "hashtags": ["string"],
    "last_contact": "datetime",
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
    "last_contact": "datetime",
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
    "last_contact": "datetime"
}

Response 200:
{
    "id": "uuid",
    "name": "string",
    "first_name": "string",
    "sub_information": {},
    "hashtags": ["string"],
    "last_contact": "datetime",
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

### 1.2 Template Management

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
                    "description": "string"
                }
            }
        }
    }
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
                    "description": "string"
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
                    "description": "string"
                }
            }
        }
    }
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
    briefingText: String
    lastContact: DateTime
    createdAt: DateTime!
    updatedAt: DateTime!
}

type Template {
    categories: JSON!
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
    template: Template!
}

type Mutation {
    createContact(input: CreateContactInput!): Contact!
    updateContact(id: ID!, input: UpdateContactInput!): Contact!
    deleteContact(id: ID!): Boolean!
    updateTemplate(input: UpdateTemplateInput!): Template!
}

input CreateContactInput {
    name: String!
    firstName: String
    subInformation: JSON
    hashtags: [String!]
    briefingText: String
    lastContact: DateTime
}

input UpdateContactInput {
    name: String
    firstName: String
    subInformation: JSON
    hashtags: [String!]
    briefingText: String
    lastContact: DateTime
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

### 3.2 Template Events
```typescript
interface TemplateEvent {
    type: "UPDATED";
    timestamp: string;
    data: {
        before?: Template;
        after?: Template;
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

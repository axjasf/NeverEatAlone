# Technical Decisions Archive

## 2024.02.13-0

### Database Design
- Using SQLite for testing (in-memory)
- UUID for primary keys
- JSON fields for flexible data (sub_information)
- All fields except name are nullable
- Tags stored in separate table with many-to-many relationship
- Case-insensitive tag storage (lowercase)
- Enhanced tag system to replace rings
- Added reminder capabilities to tags

### Validation Rules
- Name presence and length (1-100 chars)
- Basic type validation (dict for sub_info)
- Tag format validation (must start with #)
- UTC timezone enforcement for dates
- Pydantic field validation for complex rules
- Reminder frequency validation for tags

### API Design
- Clean separation between database models and API schemas
- Consistent error response format
- Proper HTTP status codes (201, 400, 404)
- Proper type conversion between SQLAlchemy and Pydantic
- Comprehensive input validation

## 2024.02.16-1

### Timezone Handling
- All datetime fields are timezone-aware
- Storage in UTC
- Conversion to local time in presentation layer
- Custom UTCDateTime type for SQLAlchemy
- Timezone validation in domain models
- Proper handling in repositories

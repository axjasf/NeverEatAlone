# Testing Guide

This document outlines our testing approach, structure, and common commands for the NeverEatAlone project.

## Test Structure

Our tests are organized into distinct categories, each with its own configuration and purpose:

```
tests/
├── models/              # Model/database tests
│   ├── conftest.py     # Model test configuration
│   └── test_*.py       # Model test files
├── api/                # API endpoint tests
│   ├── conftest.py     # API test configuration
│   └── test_*.py       # API test files
└── conftest.py         # Root test configuration
```

### Model Tests

Model tests verify the behavior of our SQLAlchemy models in isolation from the API layer. They test:
- Model creation and validation
- Relationship behavior
- Business logic
- Database constraints

**Location**: `tests/models/`
**Key Files**:
- `test_contact.py` - Contact model tests
- `test_notes.py` - Note model tests

**Running Model Tests**:
```bash
# Run all model tests
python -m pytest tests/models/

# Run specific model tests
python -m pytest tests/models/test_contact.py
python -m pytest tests/models/test_notes.py

# Run with verbosity
python -m pytest tests/models/test_contact.py -v

# Run specific test function
python -m pytest tests/models/test_contact.py::test_contact_creation_with_required_fields
```

### API Tests

API tests verify the behavior of our FastAPI endpoints. They test:
- Request/response formats
- Input validation
- Error handling
- Business logic integration
- Authentication/authorization

**Location**: `tests/api/`
**Key Files**:
- `test_contact_endpoints.py` - Contact API endpoint tests
- `test_note_endpoints.py` - Note API endpoint tests

**Running API Tests**:
```bash
# Run all API tests
python -m pytest tests/api/

# Run specific API tests
python -m pytest tests/api/test_contact_endpoints.py
python -m pytest tests/api/test_note_endpoints.py

# Run with verbosity
python -m pytest tests/api/test_contact_endpoints.py -v

# Run specific test function
python -m pytest tests/api/test_contact_endpoints.py::test_create_contact_with_minimal_data
```

## Test Configuration

### Model Test Configuration (`tests/models/conftest.py`)
- Sets up in-memory SQLite database
- Provides database session fixture
- Independent of API layer

Key fixtures:
- `engine()` - Creates SQLite test database
- `tables()` - Sets up database tables
- `db_session()` - Provides isolated database session

### API Test Configuration (`tests/api/conftest.py`)
- Builds on model test configuration
- Sets up FastAPI test client
- Manages test database integration

Key fixtures:
- `client()` - Provides FastAPI TestClient
- Inherits database fixtures from model configuration

## Best Practices

1. **Test Independence**
   - Model tests should never depend on API layer
   - Each test should clean up after itself
   - Use fresh database session for each test

2. **Test First Development**
   - Write model tests before implementing models
   - Write API tests before implementing endpoints
   - Use tests to drive design decisions

3. **Test Organization**
   - Keep model and API tests separate
   - One test file per model/endpoint
   - Clear test function names describing what is being tested

4. **Database Handling**
   - Use transactions to rollback changes
   - Don't rely on database state between tests
   - Use fixtures for common setup

## Common Commands

### Running Tests
```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=backend

# Run with output
python -m pytest -v

# Run and stop on first failure
python -m pytest -x

# Run failed tests first
python -m pytest --ff

# Run tests matching pattern
python -m pytest -k "contact"
```

### Debugging Tests
```bash
# Run with debug on failure
python -m pytest --pdb

# Show print output
python -m pytest -s

# Show locals on failure
python -m pytest -l
```

## Example Test Patterns

### Model Test Example
```python
def test_contact_creation_with_required_fields(db_session: Session) -> None:
    """Test creating a contact with only required fields."""
    contact = Contact(name="John Doe")
    db_session.add(contact)
    db_session.commit()

    saved_contact = db_session.get(Contact, contact.id)
    assert saved_contact is not None
    assert saved_contact.name == "John Doe"
```

### API Test Example
```python
def test_create_contact_with_minimal_data(client: TestClient) -> None:
    """Test creating a contact via API with minimal data."""
    response = client.post(
        "/api/contacts",
        json={"name": "John Doe"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "John Doe"
```

## Troubleshooting

Common issues and solutions:

1. **Test Database Issues**
   - Ensure `conftest.py` is properly configured
   - Check transaction rollback in fixtures
   - Verify table creation in `tables` fixture

2. **API Test Failures**
   - Check FastAPI test client setup
   - Verify database session override
   - Ensure proper cleanup between tests

3. **Import Errors**
   - Check Python path configuration
   - Verify circular import prevention
   - Check fixture availability

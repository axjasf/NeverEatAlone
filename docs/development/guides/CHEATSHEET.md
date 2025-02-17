# NeverEatAlone Development Quick Reference

## Daily Development Setup

```bash
# 1. Start in project root
cd C:/Users/D047951/Documents/GitHub/NeverEatAlone

# 2. Activate backend environment
cd backend
.\venv\Scripts\activate

# 3. Verify environment
python -m pytest -v  # Should show contact tests
```

## Test Structure and Independence

```
tests/
├── models/              # Model tests (independent of API)
│   ├── conftest.py     # Database setup only
│   └── test_*.py       # Pure model tests
├── api/                # API tests (builds on model tests)
│   ├── conftest.py     # FastAPI client setup
│   └── test_*.py       # Endpoint tests
└── conftest.py         # Re-exports fixtures
```

Key principles:

- Model tests NEVER depend on API layer
- API tests can use model test fixtures
- Each test type has its own configuration
- Use `tests/models/conftest.py` for database tests
- Use `tests/api/conftest.py` for endpoint tests

## Running Tests

```bash
# From project root (recommended)
python -m pytest -v                              # All tests
python -m pytest tests/api -v                    # Just API tests
python -m pytest tests/models -v                 # Just model tests
python -m pytest tests/api/test_contact_endpoints.py -v  # Specific test file

# Run with print statements visible (useful for debugging)
python -m pytest -v -s

# Debug on failure
python -m pytest --pdb

# Show local variables on failure
python -m pytest -l

# Run specific test function
python -m pytest tests/api/test_contact_endpoints.py -v -k "test_create_contact"

# Run tests matching a pattern
python -m pytest -v -k "test_create or test_update"
```

## Test Database Setup

```python
# In conftest.py:
@pytest.fixture
def db_session():
    """Creates a fresh database for each test"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

# In tests:
def test_something(db_session: Session):
    # Use db_session for database operations
    contact = Contact(name="Test")
    db_session.add(contact)
    db_session.commit()
```

## VS Code Essential Tasks

1. **Switch/Verify Python Environment**:
   - `Ctrl+Shift+P` → "Python: Select Interpreter"
   - Choose: `backend/venv/Scripts/python.exe`

2. **Run/Debug Tests**:
   - Click beaker icon in sidebar
   - Tests are grouped by:
     - `api/` - API endpoint tests
     - `models/` - Database model tests
   - Set breakpoints with F9
   - Debug current test with "Debug Test" button

3. **Test Output Location**:
   - Test results appear in "Python Test Log" output
   - Print statements appear in "Python Test Log" with -s flag
   - Debug output in "Debug Console"

## Manual API Development

```bash
# Start API server for development
cd backend
uvicorn app.main:app --reload

# Test endpoints with curl
# Create contact
curl -X POST http://localhost:8000/api/contacts \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Test Contact\"}"

# Get contact (replace UUID)
curl http://localhost:8000/api/contacts/123e4567-e89b-12d3-a456-426614174000

# Update contact (replace UUID)
curl -X PUT http://localhost:8000/api/contacts/123e4567-e89b-12d3-a456-426614174000 \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Updated Contact\"}"
```

## API Testing Quick Reference

```python
# Test client setup (in conftest.py)
@pytest.fixture
def client(db_session):
    app.dependency_overrides[get_test_db] = lambda: db_session
    with TestClient(app) as test_client:
        yield test_client

# Common test patterns
def test_pattern(client: TestClient, db_session: Session):
    # Create test data
    contact = Contact(name="Test")
    db_session.add(contact)
    db_session.commit()

    # API calls
    response = client.post("/api/contacts", json={"name": "New Contact"})
    response = client.get(f"/api/contacts/{contact.id}")
    response = client.put(f"/api/contacts/{contact.id}", json={"name": "Updated"})

    # Common assertions
    assert response.status_code == HTTPStatus.OK  # or 201, 404, etc.
    data = response.json()
    assert "error" in data  # For error responses
    assert data["name"] == "Test"  # For success responses
```

## Test Data Patterns

```python
# Common test data
VALID_CONTACT = {
    "name": "Test Contact",
    "first_name": "Test",
    "hashtags": ["#test"],
    "sub_information": {"key": "value"}
}

# Timezone test data
TIMEZONE_TEST_DATA = [
    (datetime.now(), "naive datetime"),
    (datetime.now(timezone.utc), "UTC datetime"),
    (datetime.now(timezone(timedelta(hours=1))), "non-UTC timezone"),
]

INVALID_DATA_PATTERNS = [
    ({}, "Field required"),
    ({"name": ""}, "String should have at least 1 character"),
    ({"name": "a" * 101}, "String should have at most 100 characters"),
]

# Use in parametrized tests
@pytest.mark.parametrize("invalid_data,expected_error", INVALID_DATA_PATTERNS)
def test_validation(client, invalid_data, expected_error):
    response = client.post("/api/contacts", json=invalid_data)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert expected_error in response.json()["error"]

# Timezone test pattern
@pytest.mark.parametrize("test_dt,description", TIMEZONE_TEST_DATA)
def test_timezone_handling(client, test_dt, description):
    """Test timezone handling in API endpoints."""
    response = client.post("/api/contacts", json={
        "name": "Test Contact",
        "last_interaction_at": test_dt.isoformat()
    })
    assert response.status_code == 201
    data = response.json()
    saved_dt = datetime.fromisoformat(data["last_interaction_at"])
    assert saved_dt.tzinfo == timezone.utc
```

## Common Issues & Solutions

1. **"Import 'backend' could not be resolved" in VS Code**:

   ```bash
   cd backend
   pip install -e .
   ```

2. **Tests not being discovered**:
   - Ensure you're running pytest from project root
   - Verify you're in the right venv
   - Check test file names start with "test_"
   - Check test functions start with "test_"

3. **Wrong environment active**:

   ```bash
   # Check current Python
   where python  # Should show backend/venv/Scripts/python.exe

   # If wrong, reactivate:
   deactivate  # if needed
   cd backend
   .\venv\Scripts\activate
   ```

4. **Database session issues**:
   - Check if using db_session fixture
   - Verify commit() after changes
   - Use db_session.refresh() after commit
   - Remember to rollback on test failures

5. **Test client issues**:
   - Verify JSON format in requests
   - Check Content-Type header is set
   - Use proper UUID format in URLs
   - Remember to commit db changes before API calls

6. **Timezone-related issues**:
   - Ensure datetime fields include timezone information
   - Use ISO8601 format for datetime strings
   - Check timezone conversion in repository layer
   - Verify UTC storage in database
   - Test with various timezone inputs
   - Remember daylight saving time considerations

## Current Project Structure

```
/backend
  /app
    main.py              # FastAPI contact endpoints
    /models
      contact.py         # Contact model
      base.py           # Base model with common fields
  /tests
    conftest.py         # Test fixtures and setup
    /api
      test_contact_endpoints.py
    /models
      test_contact.py
```

## Git Workflow

```bash
# Before starting work
git checkout feature/contact-management-core
git pull

# Committing changes
git add backend/app/main.py tests/api/test_contact_endpoints.py
git commit -m "feat(api): Add contact creation endpoint"

# Push changes
git push origin feature/contact-management-core
```

## Documentation Update Sequence

### Propagating Functional Changes

When making significant changes to functional requirements, update documentation in this sequence:

1. **Functional Requirements** (`docs/brd/modules/contact_management/requirements/functional.md`)
   - Core requirements and behaviors
   - System capabilities and constraints
   - Create feature branch for changes

2. **Architecture** (`docs/brd/modules/contact_management/technical/architecture.md`)
   - How the system will deliver these requirements
   - Component relationships
   - Data flows

3. **Interfaces** (`docs/brd/modules/contact_management/technical/interfaces.md`)
   - API contracts that implement the architecture
   - Data structures
   - Operations

4. **Non-Functional Requirements** (`docs/brd/modules/contact_management/requirements/non_functional.md`)
   - Performance implications
   - Scalability considerations
   - Security requirements

5. **User Stories** (`docs/brd/modules/contact_management/requirements/user_stories.md`)
   - Concrete usage scenarios
   - Acceptance criteria
   - User interactions

6. **Data Model** (`docs/brd/modules/contact_management/technical/data_model.md`)
   - Database schema
   - Entity relationships
   - Data integrity rules

7. **Implementation Details**
   - Implementation plan (`docs/implementation/IMPLEMENTATION_PLAN.md`)
   - Working notes (`docs/implementation/WORKING_NOTES.md`)
   - Development guides
   - Test plans

### Best Practices for Doc Updates

- Create feature branch for documentation changes
- Update documents in sequence to maintain consistency
- Commit changes per document with clear messages
- Review cross-document dependencies
- Update examples and code snippets to match new requirements

### Implementation Documentation Updates

When working on implementation tasks, update these documents in the following order:

1. **Working Notes** (`docs/implementation/WORKING_NOTES.md`)
   - Update at the start of each coding session
   - Document current focus and decisions
   - Track technical challenges
   - Version format: YYYY.MM.DD-N (e.g., 2024.02.13-1)

2. **Implementation Plan** (`docs/implementation/IMPLEMENTATION_PLAN.md`)
   - Update when sprint goals change
   - Track progress on current tasks
   - Update success criteria
   - Version in sync with Working Notes

3. **History** (`docs/implementation/HISTORY.md`)
   - Update after completing major features
   - Document technical decisions
   - Archive completed work
   - Keep version history

4. **Backlog** (`docs/implementation/BACKLOG.md`)
   - Update when reprioritizing work
   - Add new feature ideas
   - Track future sprints
   - Maintain sprint sequence

5. **Phases** (`docs/implementation/PHASES.md`)
   - Update when changing implementation sequence
   - Track phase dependencies
   - Document phase completion criteria
   - Keep aligned with Implementation Plan

When to Update:

- **Working Notes**: Daily, as you work
- **Implementation Plan**: Start of sprint, major changes
- **History**: After completing features
- **Backlog**: During sprint planning
- **Phases**: When restructuring implementation sequence

Version Number Rules:

- Format: YYYY.MM.DD-N
- Increment N when making multiple updates in one day
- All implementation docs should share same version
- Include version history section in each doc
- Commit message format: "docs: reorganize implementation docs with versioning (YYYY.MM.DD-N)"

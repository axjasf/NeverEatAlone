# NeverEatAlone Development Quick Reference

## Project Structure
```
/
├── backend/              # Backend Python code
│   ├── app/             # Application code
│   │   ├── models/      # Domain and ORM models
│   │   └── repositories/# Data access layer
│   └── tests/           # Test suite
├── docs/                # Documentation
│   ├── brd/            # Business requirements
│   ├── development/    # Development guides
│   └── implementation/ # Implementation details
│       └── changes/    # Change requests
│           ├── 1-backlog/
│           ├── 2-sprint-backlog/
│           ├── 3-in-progress/
│           ├── 4-in-review/
│           └── 5-done/YYYY/MM/
└── scripts/            # Development scripts
```

## Daily Development Setup

```bash
# 1. Start in project root
cd /Users/axeljanssen/Documents/GitHub/NeverEatAlone

# 2. Activate backend environment
cd backend
source venv/bin/activate  # For macOS/Linux
# OR .\venv\Scripts\activate  # For Windows

# 3. Verify environment
python -m pytest -v  # Should show all tests passing
```

## Change Request Management
```bash
# Create new CR
./scripts/cr.sh create "Feature title" "Description" "feature"

# Update CR status
./scripts/cr.sh update <issue-number> "in-progress" "Started implementation"
./scripts/cr.sh update <issue-number> "in-review" "Ready for review"

# Finalize CR
./scripts/cr.sh finalize <issue-number> "CR-YYYY.MM-N"
```

CR Directory Structure:
- `1-backlog/`: New CRs awaiting refinement
- `2-sprint-backlog/`: CRs selected for current sprint
- `3-in-progress/`: CRs being actively worked on
- `4-in-review/`: CRs with open PRs
- `5-done/YYYY/MM/`: Completed CRs by date

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
   - `Cmd+Shift+P` → "Python: Select Interpreter" (macOS)
   - `Ctrl+Shift+P` → "Python: Select Interpreter" (Windows)
   - Choose: `backend/venv/bin/python` (macOS) or `backend/venv/Scripts/python.exe` (Windows)

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
   which python  # macOS/Linux
   where python  # Windows
   # Should show backend/venv/bin/python or backend/venv/Scripts/python.exe

   # If wrong, reactivate:
   deactivate  # if needed
   cd backend
   source venv/bin/activate  # macOS/Linux
   .\venv\Scripts\activate   # Windows
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

## Change Request Process
For creating and managing Change Requests (CRs), refer to:
1. Quick Reference: `docs/implementation/changes/CR_QUICK_REFERENCE.md`
2. Full Process: `docs/implementation/changes/CHANGE_REQUEST_PROCESS.md`
3. Template: `docs/implementation/changes/CHANGE_REQUEST_TEMPLATE.md`

## Documentation Update Flow
When making changes:

1. **Create Change Request**
   ```bash
   ./scripts/cr.sh create "Update feature X" "Description" "feature"
   ```

2. **Update Documentation**
   - Functional Requirements: `docs/brd/modules/*/requirements/`
   - Technical Design: `docs/brd/modules/*/technical/`
   - Implementation Notes: `docs/implementation/`
   - Test Documentation: `docs/development/TESTING.md`

3. **Track Progress**
   ```bash
   ./scripts/cr.sh update <issue-number> "in-progress" "Updated documentation"
   ```

## Documentation Update Sequence
When making significant changes, update documentation in this sequence:

1. **Functional Requirements** (`docs/brd/modules/contact_management/requirements/functional.md`)
   - Core requirements and behaviors
2. **Technical Design** (`docs/brd/modules/contact_management/technical/`)
   - Architecture updates
   - Data model changes
   - Interface modifications
3. **Implementation Notes** (`docs/implementation/`)
   - Update working notes
   - Add implementation details
4. **Test Documentation** (`docs/development/TESTING.md`)
   - Test coverage requirements
   - New test patterns

## Git Workflow with CRs
```bash
# 1. Create CR and branch
./scripts/cr.sh create "New feature" "Description" "feature"

# 2. Work on feature
git checkout feature/<issue-number>-feature-name
# Make changes...
git add .
git commit -m "feat: implement feature"

# 3. Update progress
./scripts/cr.sh update <issue-number> "in-progress" "Implementation complete"

# 4. Create PR
./scripts/cr.sh finalize <issue-number> "CR-YYYY.MM-N"
```

## Project Management
Key files and locations:
- Change Requests: `docs/implementation/changes/`
- Development Journal: `docs/implementation/DEVELOPMENT_JOURNAL.md`
- Implementation Plan: `docs/implementation/IMPLEMENTATION_PLAN.md`
- Test Documentation: `docs/development/TESTING.md`
- Business Requirements: `docs/brd/modules/`

Documentation hierarchy:
1. Business Requirements (BRD)
2. Technical Design
3. Implementation Details
4. Change Requests
5. Test Documentation

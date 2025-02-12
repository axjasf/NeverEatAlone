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

## Running Tests
```bash
# From project root (recommended)
python -m pytest -v                              # All tests
python -m pytest tests/api -v                    # Just API tests
python -m pytest tests/models -v                 # Just model tests
python -m pytest tests/api/test_contact_endpoints.py -v  # Specific test file

# Run with print statements visible (useful for debugging)
python -m pytest -v -s

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

## Test Data Patterns
```python
# Common test data
VALID_CONTACT = {
    "name": "Test Contact",
    "first_name": "Test",
    "hashtags": ["#test"],
    "sub_information": {"key": "value"}
}

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

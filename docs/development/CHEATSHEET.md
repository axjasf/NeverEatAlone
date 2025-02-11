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

## Current API Development
```bash
# Start API server for development
cd backend
uvicorn app.main:app --reload

# Test endpoints with curl
curl -X POST http://localhost:8000/api/contacts -H "Content-Type: application/json" -d "{\"name\":\"Test Contact\"}"
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

3. **Wrong environment active**:
   ```bash
   # Check current Python
   where python  # Should show backend/venv/Scripts/python.exe

   # If wrong, reactivate:
   deactivate  # if needed
   cd backend
   .\venv\Scripts\activate
   ```

## Current Project Structure
```
/backend
  /app
    main.py              # FastAPI contact endpoints
    /models
      contact.py         # Contact model
  /tests
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

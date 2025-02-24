# Development Guide

## Cross-Platform Development

### Path Handling
```python
# ❌ Don't use hardcoded separators
path = "backend\\app\\models"  # Windows-only
path = "backend/app/models"    # Unix-style

# ✅ Use platform-agnostic methods
from pathlib import Path
models_path = Path("backend") / "app" / "models"
```

### Environment Activation
```powershell
# Windows PowerShell
.\venv\Scripts\activate

# Windows Command Prompt
.\venv\Scripts\activate.bat

# Mac/Linux
source venv/bin/activate
```

### Common Cross-Platform Issues
1. **Path Separators**
   - Windows uses backslash (\)
   - Unix uses forward slash (/)
   - Git on Windows may normalize to forward slashes
   - Always use `os.path.join()` or `pathlib.Path` in code

2. **Line Endings**
   - Windows: CRLF (\r\n)
   - Unix: LF (\n)
   - Configure Git: `git config --global core.autocrlf true` on Windows

3. **Shell Commands**
   - Windows PowerShell: semicolon (;) separator
   - Windows CMD: ampersand (&) separator
   - Unix: ampersand (&) or semicolon (;)

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
│   ├── guides/         # Development guides
│   ├── features/       # Feature documentation
│   └── dev-journal/    # Development journals
└── scripts/            # Development scripts
```

## VS Code Integration

### Python Environment
- Use Command Palette (`Cmd+Shift+P` / `Ctrl+Shift+P`)
- Select "Python: Select Interpreter"
- Choose `backend/venv/bin/python` (Mac/Linux) or `backend\venv\Scripts\python.exe` (Windows)

### Testing
- Use Testing sidebar (beaker icon)
- Tests grouped by:
  - `api/` - API endpoint tests
  - `models/` - Database model tests
- Set breakpoints with F9
- Debug current test with "Debug Test" button

### Output Locations
- Test results: "Python Test Log"
- Print statements: Visible with pytest -s flag
- Debug output: "Debug Console"

## Manual API Testing
```bash
# Start API server
cd backend
uvicorn app.main:app --reload

# Test endpoints
curl -X POST http://localhost:8000/api/contacts \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Test Contact\"}"

# Get contact
curl http://localhost:8000/api/contacts/<uuid>

# Update contact
curl -X PUT http://localhost:8000/api/contacts/<uuid> \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Updated Contact\"}"
```

See `quick-start/COMMANDS.md` for common development commands.

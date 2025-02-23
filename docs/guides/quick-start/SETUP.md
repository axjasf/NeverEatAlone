# Quick Setup Guide

## Prerequisites
- Node.js 18.x+
- Python 3.10+
- SQLite 3.x+

## 1. Initial Setup
```bash
# Clone and enter project
git clone <repository-url>
cd NeverEatAlone

# Install pre-commit hooks
pip install pre-commit
pre-commit install
```

## 2. Database Setup
```bash
cd backend
sqlite3 dev.db ".databases"
sqlite3 test.db ".databases"
python init_db.py
```

## 3. Environment Setup
Backend `.env`:
```env
DATABASE_URL=sqlite:///./dev.db
TEST_DATABASE_URL=sqlite:///./test.db
ENVIRONMENT=development
```

Frontend `.env`:
```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENVIRONMENT=development
```

## 4. Install Dependencies
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Frontend
cd frontend
npm install
```

## 5. Start Development
```bash
# Backend (in backend/)
source venv/bin/activate
uvicorn app.main:app --reload

# Frontend (in frontend/)
npm start
```

## Next Steps
- See `quick-start/COMMANDS.md` for common commands
- See `quick-start/WORKFLOW.md` for daily development workflow
- See `detailed/` for in-depth documentation

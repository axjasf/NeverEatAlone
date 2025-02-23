# Common Commands

## Development
```bash
# Start Backend
cd backend
source venv/bin/activate  # or .\venv\Scripts\activate on Windows
uvicorn app.main:app --reload

# Start Frontend
cd frontend
npm start
```

## Testing
```bash
# Backend Tests
cd backend
python -m pytest -v                    # All tests
python -m pytest tests/api -v          # API tests
python -m pytest tests/models -v       # Model tests
python -m pytest -v -s                 # Show prints
python -m pytest --pdb                 # Debug on failure

# Frontend Tests
cd frontend
npm test
npm run test:coverage
```

## Change Requests
```bash
# Create new CR
./scripts/cr.sh create "Title" "Description" "feature"

# Update CR status
./scripts/cr.sh update <issue-number> "in-progress" "Status message"

# Complete CR
./scripts/cr.sh finalize <issue-number> "CR-YYYY.MM-N"
```

## Git Workflow
```bash
# Feature branch
git checkout -b feature/<issue-number>-description

# Commit changes
git add .
git commit -m "type(scope): message (#issue)"

# Update branch
git pull origin main
git push origin feature/<issue-number>-description
```

## Code Quality
```bash
# Backend
cd backend
flake8 .
black .
mypy .

# Frontend
cd frontend
npm run lint
npm run format
```

See `detailed/` directory for comprehensive documentation.

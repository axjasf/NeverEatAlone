# Development Setup Guide

## Prerequisites

- Node.js 18.x or later
- Python 3.10 or later
- SQLite 3.x or later

## Initial Setup

1. **Clone the Repository**
```bash
git clone <repository-url>
cd NeverEatAlone
```

2. **Install Pre-commit Hooks**
```bash
pip install pre-commit
pre-commit install
```

3. **Database Setup**

```bash
# Initialize SQLite database
cd backend
sqlite3 dev.db ".databases"
sqlite3 test.db ".databases"

# Initialize the database schema
python init_db.py
```

4. **Environment Setup**

Create `.env` files for both frontend and backend:

Backend `.env`:
```env
DATABASE_URL=sqlite:///./dev.db
TEST_DATABASE_URL=sqlite:///./test.db
ENVIRONMENT=development
OPENAI_API_KEY=your_api_key_here  # Required for AI features
```

Frontend `.env`:
```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENVIRONMENT=development
```

5. **Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Install development dependencies
```

6. **Frontend Setup**
```bash
cd frontend
npm install
```

7. **SonarCloud Setup**

The project uses SonarCloud for code quality analysis. The analysis is automatically run on pull requests and pushes to main/develop branches.

To view the analysis:
1. Visit [SonarCloud Dashboard](https://sonarcloud.io/project/overview?id=axjasf_NeverEatAlone)
2. Login with your GitHub account
3. You'll see the project's code quality metrics, issues, and analysis history

For local analysis before pushing:
```bash
# Install sonar-scanner
npm install -g sonar-scanner

# Set environment variables
export SONAR_TOKEN=your_sonarcloud_token  # Get this from SonarCloud

# Run analysis
sonar-scanner
```

## Development Workflow

1. **Start the Development Servers**

Backend:
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

Frontend:
```bash
cd frontend
npm start
```

2. **Running Tests**

Backend:
```bash
cd backend
pytest --cov=app --cov-report=html
```

Frontend:
```bash
cd frontend
npm test
npm run test:coverage  # For coverage report
```

3. **Code Quality Checks**

Backend:
```bash
flake8 .
black .
isort .
mypy .
```

Frontend:
```bash
npm run lint
npm run type-check
npm run prettier:write
```

4. **Database Migrations**

```bash
cd backend
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## Code Style Guidelines

1. **TypeScript**
- Strict type checking enabled
- No `any` types allowed
- JSDoc documentation required for all components and functions
- Follow provided `.cursorrules` configuration

2. **Python**
- Follow PEP 8
- Use type hints
- Document all functions and classes
- Maximum line length: 88 characters (Black default)

3. **React**
- Functional components with hooks
- Props validation required
- Follow WCAG 2.1 accessibility standards
- Include error boundaries and loading states

4. **Testing**
- TDD approach required
- Minimum 80% code coverage
- Mock external dependencies
- Include edge cases and error states

## Git Workflow

1. **Branch Naming**
- Feature branches: `feature/description`
- Bug fixes: `fix/description`
- Releases: `release/version`

2. **Commit Messages**
Follow conventional commits:
```
type(scope): description

[optional body]

[optional footer]
```

3. **Pull Requests**
- Create PR against `develop` branch
- Require 2 approvals
- Must pass CI/CD pipeline
- Include tests
- Update documentation

## Troubleshooting

1. **Database Issues**
```bash
# Reset development database
cd backend
rm dev.db
sqlite3 dev.db ".databases"
python init_db.py
```

2. **Frontend Type Issues**
```bash
# Clean and reinstall dependencies
rm -rf node_modules
npm install
npm run type-check
```

3. **Backend Environment Issues**
```bash
# Recreate virtual environment
cd backend
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

4. **SonarQube Issues**
```bash
# Reset SonarQube
docker-compose down -v
docker-compose up -d
```

## Additional Resources

- [Project Documentation](./docs)
- [API Documentation](./backend/docs)
- [Component Library](./frontend/src/components)
- [Test Coverage Reports](./coverage)
- [SonarQube Dashboard](http://localhost:9000) 
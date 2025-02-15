# Environment Variables Configuration

This document describes the environment variables used in the NeverEatAlone application.

## Overview

The application uses environment variables for configuration in different environments:
- Development
- Staging
- Production

## Required Variables

### Backend Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| DATABASE_URL | Database connection string | sqlite:///./dev.db | Yes |
| TEST_DATABASE_URL | Test database connection string | sqlite:///./test.db | Yes |
| ENVIRONMENT | Current environment | development | Yes |
| SECRET_KEY | Secret key for JWT/sessions | - | Yes |
| CORS_ORIGINS | Allowed CORS origins | http://localhost:3000 | Yes |

### Frontend Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| REACT_APP_API_URL | Backend API URL | http://localhost:8000 | Yes |
| REACT_APP_ENVIRONMENT | Current environment | development | Yes |
| REACT_APP_VERSION | Application version | $npm_package_version | No |

### Test Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| PYTEST_ADDOPTS | Additional pytest options | --color=yes | No |
| COVERAGE_THRESHOLD | Minimum coverage percentage | 80 | Yes |

## Environment-Specific Values

### Development
```env
DATABASE_URL=sqlite:///./dev.db
REACT_APP_API_URL=http://localhost:8000
ENVIRONMENT=development
```

### Staging
```env
DATABASE_URL=<staging-db-url>
REACT_APP_API_URL=<staging-api-url>
ENVIRONMENT=staging
```

### Production
```env
DATABASE_URL=<production-db-url>
REACT_APP_API_URL=<production-api-url>
ENVIRONMENT=production
```

## GitHub Actions Configuration

The CI/CD pipeline uses these variables with secure defaults and overrides:

1. **Secrets Required**:
   - SECRET_KEY
   - PROD_API_URL
   - STAGING_API_URL
   - CORS_ORIGINS (optional)

2. **Automatic Environment Detection**:
   - Production: main branch
   - Staging: develop branch
   - Development: all other branches

3. **Security Notes**:
   - Never commit sensitive values to version control
   - Use GitHub Secrets for sensitive data
   - Use defaults only for development environment

## Local Development Setup

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Update values in `.env` as needed

3. For frontend development:
   ```bash
   cd frontend
   cp .env.example .env.local
   ```

4. For backend development:
   ```bash
   cd backend
   cp .env.example .env
   ```

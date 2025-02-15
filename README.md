# NeverEatAlone

A contact management and note-taking application with smart reminders.

## Documentation

Our documentation is organized into the following sections:

### Development
- [Development Guide](docs/development/guides/DEVELOPMENT.md) - Setup and development workflow
- [CI/CD Stabilization Plan](docs/development/ci/CI_STABILIZATION_PLAN.md) - Continuous Integration improvements
- [Environment Setup](docs/environment/ENVIRONMENT.md) - Environment configuration

### Business Requirements
- See [Business Requirements Documentation](docs/brd/)

### Implementation Details
- See [Implementation Documentation](docs/implementation/)

## Project Structure

```
.
├── backend/           # Python FastAPI backend
│   ├── app/          # Application source code
│   ├── tests/        # Test files
│   └── config/       # Configuration files
├── frontend/         # React TypeScript frontend
│   ├── src/         # Application source code
│   └── tests/       # Test files
└── docs/            # Documentation
    ├── development/ # Development guides and CI/CD
    ├── brd/         # Business requirements
    └── implementation/ # Implementation details
```

## Project Status

[![CI/CD Pipeline](https://github.com/axjasf/NeverEatAlone/actions/workflows/main.yml/badge.svg)](https://github.com/axjasf/NeverEatAlone/actions/workflows/main.yml)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=axjasf_NeverEatAlone&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=axjasf_NeverEatAlone)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=axjasf_NeverEatAlone&metric=coverage)](https://sonarcloud.io/summary/new_code?id=axjasf_NeverEatAlone)

## Features

- Contact Management
- Note Taking with AI-powered summaries
- Voice-to-Text using OpenAI Whisper
- Hashtag Organization
- Reminders and Follow-ups
- AI-powered Contact Briefing

## Tech Stack

- **Frontend**: React, TypeScript, Material-UI
- **Backend**: Python, FastAPI, SQLAlchemy
- **Database**: SQLite
- **AI**: OpenAI Whisper API
- **Testing**: Jest, React Testing Library, Pytest
- **CI/CD**: GitHub Actions, SonarCloud

## Getting Started

See [DEVELOPMENT.md](DEVELOPMENT.md) for detailed setup instructions.

### Quick Start

1. Clone the repository
2. Copy `.env.example` to `.env` and configure
3. Follow the [Environment Setup Guide](docs/environment/ENVIRONMENT.md)
4. Follow the [Development Guide](docs/development/guides/DEVELOPMENT.md)

## Contributing

Please read our [Development Guide](docs/development/guides/DEVELOPMENT.md) before contributing.

## License

This project is licensed under the terms of the [LICENSE](LICENSE) file.

## Acknowledgments

- OpenAI for the Whisper API
- All contributors and maintainers

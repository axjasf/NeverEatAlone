# NeverEatAlone

A contact management and note-taking application with AI capabilities.

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
- **Database**: SQLite (Development), PostgreSQL (Production)
- **AI**: OpenAI Whisper API
- **Testing**: Jest, React Testing Library, Pytest
- **CI/CD**: GitHub Actions, SonarCloud

## Getting Started

See [DEVELOPMENT.md](DEVELOPMENT.md) for detailed setup instructions.

### Quick Start

1. Clone the repository:
```bash
git clone <repository-url>
cd NeverEatAlone
```

2. Set up the backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

3. Set up the frontend:
```bash
cd frontend
npm install
```

4. Start the development servers:
```bash
# Terminal 1 (Backend)
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# Terminal 2 (Frontend)
cd frontend
npm start
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- OpenAI for the Whisper API
- All contributors and maintainers

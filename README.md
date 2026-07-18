# AI Website Intelligence Platform

A production-grade open-source platform that transforms websites into structured business intelligence using AI.

## 🎯 Vision

Convert any website URL into structured business intelligence through automated web crawling, content extraction, and AI-powered analysis.

```
Website URL → Validation → Crawler → Parser → Cleaner → Extractor → LLM → Structured JSON
```

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- Docker and Docker Compose
- PostgreSQL 15+
- Redis 7+

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd AI-Website-Intelligence-Platform
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Start services with Docker Compose**
   ```bash
   docker-compose up -d
   ```

6. **Run the application**
   ```bash
   python main.py
   ```

7. **Access the API**
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/api/v1/health

## 🏗️ Architecture

This project follows **Clean Architecture** principles:

```
backend/
├── api/                    # REST API Layer
│   ├── routes/            # FastAPI routes
│   └── models/            # Pydantic models
├── config/                # Configuration Layer
│   ├── settings.py        # Application settings
│   └── logging.py         # Logging configuration
├── core/                  # Core Business Logic
│   ├── domain/            # Domain entities
│   ├── interfaces/        # Business interfaces
│   └── use_cases/         # Business use cases
├── crawler/               # Web crawling module
├── parser/                # HTML parsing module
├── cleaner/               # Content cleaning module
├── extractor/             # Information extraction module
├── llm/                   # LLM integration module
├── database/              # Database layer
└── utils/                 # Utilities
```

## 📖 Documentation

- **[AGENTS.md](AGENTS.md)** - Project goals and philosophy
- **[PRODUCT.md](PRODUCT.md)** - Product vision and requirements
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Technical architecture
- **[ROADMAP.md](ROADMAP.md)** - Development roadmap
- **[docs/DECISIONS.md](docs/DECISIONS.md)** - Engineering decisions
- **[docs/adr/](docs/adr/)** - Architecture Decision Records

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=backend --cov-report=html
```

## 🔧 Development

```bash
# Format code
black backend/

# Lint code
ruff check backend/

# Type check
mypy backend/
```

## 📋 Current Status

**Phase 1: Project Foundation**

- ✅ Milestone 1: Repository Audit
- ✅ Milestone 2: Project Initialization (In Progress)
- ⏳ Milestone 3: Crawler Foundation
- ⏳ Milestone 4: HTML Processing
- ⏳ Milestone 5: Information Extraction
- ⏳ Milestone 6: Technology Detection
- ⏳ Milestone 7: AI Processing
- ⏳ Milestone 8: Database
- ⏳ Milestone 9: REST API
- ⏳ Milestone 10: Testing
- ⏳ Milestone 11: Documentation

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

Built with:
- FastAPI
- PostgreSQL
- SQLAlchemy
- Clean Architecture principles
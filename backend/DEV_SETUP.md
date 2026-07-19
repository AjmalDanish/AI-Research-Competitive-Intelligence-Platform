# Development Environment Setup

This project uses **Poetry** for dependency management and development environment.

## Prerequisites

- Python 3.11 or higher
- Poetry 2.4.1 or higher

## Quick Setup

### 1. Install Poetry (if not installed)

**Windows (PowerShell):**
```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

**Add to PATH:**
```powershell
[Environment]::SetEnvironmentVariable("Path", [Environment]::GetEnvironmentVariable("Path", "User") + ";C:\Users\$env:USERNAME\AppData\Roaming\Python\Scripts", "User")
```

### 2. Install Dependencies

```bash
cd backend
poetry install
```

### 3. Verify Installation

```bash
poetry run black --version
poetry run ruff --version  
poetry run mypy --version
poetry run pytest --version
```

## Development Commands

### Code Formatting
```bash
poetry run black backend/                    # Format all code
poetry run black backend/ --check           # Check formatting without changes
poetry run black backend/crawler/           # Format specific module
```

### Code Linting
```bash
poetry run ruff check backend/              # Check for linting issues
poetry run ruff check backend/ --fix        # Auto-fix linting issues
poetry run ruff check backend/crawler/      # Lint specific module
```

### Type Checking
```bash
poetry run mypy backend/                    # Type checking
poetry run mypy backend/crawler/            # Type checking specific module
```

### Testing
```bash
poetry run pytest tests/                    # Run all tests
poetry run pytest tests/test_crawler.py     # Run specific test file
poetry run pytest tests/ -v                 # Verbose output
poetry run pytest tests/ -x                 # Stop on first failure
poetry run pytest tests/unit/               # Run unit tests only
```

## Quick Quality Check

Run all quality checks at once:
```bash
poetry run black backend/ --check && poetry run ruff check backend/ && poetry run mypy backend/ && poetry run pytest tests/
```

## Project Structure

```
backend/
├── config/          # Configuration management
├── core/            # Domain models and interfaces
├── crawler/         # Web crawling implementations
├── database/        # Database models and connections
├── tests/           # Unit and integration tests
└── pyproject.toml   # Poetry configuration
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp backend/.env.example backend/.env
```

Required environment variables:
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - Application secret key
- `ENVIRONMENT` - Development/Production

## Troubleshooting

### Poetry command not found

Add Poetry to your system PATH:
```powershell
[Environment]::SetEnvironmentVariable("Path", [Environment]::GetEnvironmentVariable("Path", "User") + ";C:\Users\$env:USERNAME\AppData\Roaming\Python\Scripts", "User")
```

### Poetry install fails with build errors

Some packages may require Microsoft Visual C++ Build Tools. For a simpler setup, the project uses a minimal set of pre-built packages.

### Virtual environment issues

Recreate the virtual environment:
```bash
cd backend
poetry env remove --all
poetry install
```

## Workflow Recommendation

1. **Always use `poetry run`** for development commands
2. **Install dependencies** after pulling changes: `poetry install`
3. **Run quality checks** before committing
4. **Test changes** with `poetry run pytest tests/`
5. **Format code** with `poetry run black backend/`

## Additional Resources

- [Poetry Documentation](https://python-poetry.org/docs/)
- [Black Documentation](https://black.readthedocs.io/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [MyPy Documentation](https://mypy.readthedocs.io/)
- [Pytest Documentation](https://docs.pytest.org/)
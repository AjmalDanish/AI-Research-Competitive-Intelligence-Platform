# Contributing to AI Research Competitive Intelligence Platform

Thank you for your interest in contributing to the AI Research Competitive Intelligence Platform! This document provides guidelines and instructions for contributing.

## Code of Conduct

### Our Pledge
We as members, contributors, and leaders pledge to make participation in our community a harassment-free experience for everyone.

### Our Standards
- Use welcoming and inclusive language
- Be respectful of different viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker 24+
- Poetry (for Python)
- npm (for Node.js)

### Development Setup

1. **Fork the repository**
   ```bash
   # Fork on GitHub and clone your fork
   git clone https://github.com/YOUR_USERNAME/AI-Research-Competitive-Intelligence-Platform.git
   cd AI-Research-Competitive-Intelligence-Platform
   ```

2. **Set up the development environment**
   ```bash
   # Backend
   cd backend
   poetry install
   pre-commit install
   
   # Frontend
   cd ../frontend
   npm install
   ```

3. **Start the development servers**
   ```bash
   # Terminal 1 - Backend
   cd backend
   poetry shell
   uvicorn app.main:app --reload
   
   # Terminal 2 - Frontend
   cd frontend
   npm run dev
   ```

## Development Workflow

### Branch Strategy
- `main` - Production-ready code
- `develop` - Integration branch for features
- `feature/*` - New features
- `bugfix/*` - Bug fixes
- `hotfix/*` - Critical production fixes

### Creating a Feature Branch
```bash
git checkout develop
git pull origin develop
git checkout -b feature/your-feature-name
```

### Making Changes

1. **Write clean, documented code**
2. **Follow project coding standards**
3. **Add tests for new functionality**
4. **Update documentation as needed**

### Commit Guidelines

Follow conventional commits format:
```
type(scope): subject

body

footer
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Build process or auxiliary tool changes

**Examples:**
```
feat(competitors): add competitor activity tracking

Add ability to track and analyze competitor activities
including product releases, partnerships, and funding events.

Closes #123
```

```
fix(api): resolve authentication token expiration

Fix JWT token validation to properly handle expiration
times and refresh tokens.

Fixes #456
```

### Running Tests

```bash
# Backend tests
cd backend
poetry run pytest
poetry run pytest --cov=app

# Frontend tests
cd frontend
npm test
npm run test:coverage

# All tests
npm run test:all
```

### Code Quality Checks

```bash
# Backend
cd backend
poetry run ruff check .
poetry run black --check .
poetry run isort --check-only .
poetry run mypy app/

# Frontend
cd frontend
npm run lint
npm run type-check
```

## Pull Request Process

### Before Submitting
1. Update documentation
2. Add/update tests
3. Run all tests and ensure they pass
4. Run code quality checks
5. Update CHANGELOG.md

### Submitting a Pull Request
1. Push your branch to your fork
   ```bash
   git push origin feature/your-feature-name
   ```

2. Create a pull request on GitHub
   - Target: `develop` branch
   - Use descriptive title and description
   - Reference related issues

3. Fill out the PR template
   - Description of changes
   - Testing performed
   - Breaking changes (if any)
   - Documentation updates

### Pull Request Review Process
1. Automated checks must pass
2. Code review by maintainers
3. Address review feedback
4. Approval required for merge

## Coding Standards

### Python (Backend)
- Follow PEP 8 style guide
- Use type hints for all functions
- Write docstrings for all modules, classes, and functions
- Maximum line length: 100 characters
- Use f-strings for string formatting
- Prefer async/await for I/O operations

### JavaScript/TypeScript (Frontend)
- Follow ESLint configuration
- Use TypeScript for type safety
- Write meaningful component and variable names
- Use functional components with hooks
- Follow React best practices

### Documentation
- Use clear, concise language
- Include examples where helpful
- Keep documentation up to date
- Use Markdown formatting

## Testing Guidelines

### Test Coverage
- Aim for 80%+ code coverage
- Test critical paths thoroughly
- Include edge cases and error scenarios

### Test Types
- **Unit tests**: Test individual components/functions
- **Integration tests**: Test component interactions
- **End-to-end tests**: Test complete workflows

### Writing Tests
- Use descriptive test names
- Follow Arrange-Act-Assert pattern
- Mock external dependencies
- Keep tests independent

## Project Structure

```
AI-Research-Competitive-Intelligence-Platform/
├── backend/                 # Python/FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Core functionality
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   └── utils/          # Utilities
│   ├── tests/              # Backend tests
│   └── pyproject.toml      # Python dependencies
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   └── utils/          # Utilities
│   └── package.json        # Node dependencies
├── docs/                   # Documentation
├── .github/                # GitHub workflows
└── docker/                 # Docker configurations
```

## Issue Reporting

### Bug Reports
Include:
- Clear description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Environment details
- Screenshots/logs if applicable

### Feature Requests
Include:
- Clear description of the feature
- Use case and benefits
- Possible implementation approach
- Examples or mockups if helpful

## Questions and Support

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and ideas
- **Documentation**: Check docs/ folder for detailed guides

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project documentation

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to the AI Research Competitive Intelligence Platform!
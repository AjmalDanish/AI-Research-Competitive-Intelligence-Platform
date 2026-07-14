# AI Research Competitive Intelligence Platform

An AI-powered platform for competitive intelligence and research analysis, enabling organizations to track competitors, analyze market trends, and generate actionable insights.

## 🚀 Features

### Core Capabilities
- **Competitor Tracking**: Monitor competitor activities, products, and strategies
- **Market Intelligence**: Real-time market trend analysis and forecasting
- **Research Automation**: Automated data collection and processing
- **AI-Powered Insights**: Machine learning models for predictive analytics
- **Dashboard & Visualization**: Interactive dashboards for data exploration
- **Alert System**: Real-time notifications for important events

### Technical Features
- RESTful API architecture
- Real-time data processing with websockets
- Scalable microservices architecture
- Docker containerization
- CI/CD pipeline with GitHub Actions
- Comprehensive testing coverage

## 🏗️ Architecture

### Backend Services
- **API Gateway**: FastAPI-based REST API
- **Data Collection**: Scrapy-based web scrapers
- **Data Processing**: Pandas/NumPy for data transformation
- **ML Pipeline**: scikit-learn/TensorFlow for predictions
- **Notification Service**: Email/Slack/webhook alerts

### Frontend
- **React 18**: Modern UI with TypeScript
- **Material-UI**: Component library
- **Recharts**: Data visualization
- **WebSocket**: Real-time updates

### Infrastructure
- **Docker**: Container orchestration
- **PostgreSQL**: Primary database
- **Redis**: Caching and session management
- **Elasticsearch**: Full-text search

## 📋 Prerequisites

- Python 3.11+
- Node.js 18+
- Docker 24+
- Docker Compose 2+
- Poetry or uv (Python package manager)

## 🛠️ Installation

### Clone the Repository
```bash
git clone https://github.com/AjmalDanish/AI-Research-Competitive-Intelligence-Platform.git
cd AI-Research-Competitive-Intelligence-Platform
```

### Backend Setup
```bash
cd backend
poetry install
poetry shell
pre-commit install
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Docker Setup
```bash
docker-compose up -d
```

## 🚦 Quick Start

### Using Docker (Recommended)
```bash
docker-compose up -d
```

### Manual Setup
```bash
# Backend
cd backend
poetry install
poetry shell
uvicorn app.main:app --reload

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

### Access the Application
- Frontend: http://localhost:3000
- API Documentation: http://localhost:8000/docs
- Admin Dashboard: http://localhost:8000/admin

## 📚 Documentation

- [API Documentation](docs/API.md)
- [Architecture Overview](docs/ARCHITECTURE.md)
- [Development Guide](docs/DEVELOPMENT.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Contributing Guide](docs/CONTRIBUTING.md)

## 🧪 Testing

### Backend Tests
```bash
cd backend
poetry run pytest
poetry run pytest --cov=app
```

### Frontend Tests
```bash
cd frontend
npm test
npm run test:coverage
```

### Integration Tests
```bash
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

## 🔄 Development Workflow

1. Create a feature branch
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes and test
```bash
poetry run pytest
npm test
```

3. Commit with conventional commits
```bash
git commit -m "feat: add new feature"
```

4. Push and create pull request
```bash
git push origin feature/your-feature-name
```

## 📊 Project Structure

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
├── docker/                 # Docker configurations
└── scripts/                # Utility scripts
```

## 🔧 Configuration

### Environment Variables
Create `.env` files in both backend and frontend directories:

**Backend .env:**
```env
DATABASE_URL=postgresql://user:password@localhost:5432/aicp
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key
API_KEY=your-api-key
```

**Frontend .env:**
```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
```

## 🤝 Contributing

We welcome contributions! Please read our [Contributing Guide](docs/CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Ajmal Danish** - Initial work

## 🙏 Acknowledgments

- OpenAI for AI technologies
- FastAPI community
- React community
- All contributors

## 📞 Support

For support, please open an issue in the GitHub repository.

## 🗺️ Roadmap

- [ ] Phase 1: Core MVP
  - [x] Project setup
  - [ ] API infrastructure
  - [ ] Database models
  - [ ] Basic UI components
  
- [ ] Phase 2: Data Collection
  - [ ] Web scrapers
  - [ ] Data pipelines
  - [ ] Storage optimization
  
- [ ] Phase 3: ML Integration
  - [ ] Prediction models
  - [ ] Trend analysis
  - [ ] Alert system
  
- [ ] Phase 4: Advanced Features
  - [ ] Real-time updates
  - [ ] Advanced visualizations
  - [ ] Export capabilities
  
- [ ] Phase 5: Production Readiness
  - [ ] Performance optimization
  - [ ] Security hardening
  - [ ] Documentation completion

---

**Built with ❤️ for intelligent competitive analysis**
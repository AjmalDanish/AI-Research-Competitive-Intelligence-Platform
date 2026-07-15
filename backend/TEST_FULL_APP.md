# Complete Application Testing Guide

## Step 1: Install Additional Dependencies

```powershell
pip install sqlalchemy aiohttp beautifulsoup4 lxml pandas numpy scikit-learn python-jose passlib bcrypt
```

## Step 2: Create Production Environment File

```powershell
del .env
$envContent = @"
DEBUG=True
ENVIRONMENT=development
API_V1_STR=/api/v1
SECRET_KEY=your-secret-key-change-in-production-min-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
DATABASE_URL=sqlite+aiosqlite:///./aicp.db
REDIS_URL=redis://localhost:6379/0
ELASTICSEARCH_URL=http://localhost:9200
LOG_LEVEL=INFO
RATE_LIMIT_ENABLED=True
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100
"@
Set-Content -Path .env -Value $envContent -Encoding UTF8
```

## Step 3: Test Imports and Services

```powershell
python -c "from app.services.scraping_service import ScrapingConfig; print('Scraping OK')"
python -c "from app.services.data_pipeline import DataPipeline; print('Pipeline OK')"
python -c "from app.services.analytics_service import AnalyticsService; print('Analytics OK')"
```

## Step 4: Test Database Models

```powershell
python -c "from app.models.competitor import Competitor; print('Competitor model OK')"
python -c "from app.models.market import MarketTrend; print('Market model OK')"
python -c "from app.models.user import User; print('User model OK')"
python -c "from app.models.alert import Alert; print('Alert model OK')"
```

## Step 5: Test Core Configuration

```powershell
python -c "from app.core.config import settings; print('Config OK:', settings.PROJECT_NAME)"
python -c "from app.core.security import get_password_hash; print('Security OK')"
python -c "from app.db.session import AsyncSessionLocal; print('Database OK')"
```

## Step 6: Start Full Application Server

```powershell
python -m uvicorn app.main:app --reload --port 8000
```

## Step 7: Test Core API Endpoints

### Health Check
```powershell
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/health
```

### User Management
```powershell
# Register user
curl -X POST "http://localhost:8000/api/v1/auth/register" -H "Content-Type: application/json" -d '{"email":"test@example.com","username":"testuser","password":"testpass123","full_name":"Test User"}'

# List users
curl http://localhost:8000/api/v1/users
```

### Competitors
```powershell
# List competitors
curl http://localhost:8000/api/v1/competitors

# Create competitor
curl -X POST "http://localhost:8000/api/v1/competitors" -H "Content-Type: application/json" -d '{"name":"Test Competitor","website":"https://test.com","industry":"Technology"}'

# Get specific competitor (replace ID with actual ID from previous response)
curl http://localhost:8000/api/v1/competitors/1
```

### Activities
```powershell
# List activities
curl http://localhost:8000/api/v1/activities

# Create activity
curl -X POST "http://localhost:8000/api/v1/activities" -H "Content-Type: application/json" -d '{"competitor_id":1,"activity_type":"product_release","title":"New Product Launch","description":"Test description"}'
```

### Market Intelligence
```powershell
# List market trends
curl http://localhost:8000/api/v1/market/trends

# List market intelligence
curl http://localhost:8000/api/v1/market/intelligence
```

### Alerts
```powershell
# List alerts
curl http://localhost:8000/api/v1/alerts

# Create alert
curl -X POST "http://localhost:8000/api/v1/alerts" -H "Content-Type: application/json" -d '{"user_id":1,"title":"Test Alert","alert_type":"market_trend","message":"Test message","priority":"medium"}'
```

## Step 8: Access Interactive Documentation

Open browser: http://localhost:8000/docs

## Step 9: Run Unit Tests

```powershell
# Run all tests
pytest tests/ -v

# Run specific test files
pytest tests/test_scraping_service.py -v
pytest tests/test_data_pipeline.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=term-missing
```

## Step 10: Test Services Directly

Create test_services.py to test services individually.

## Success Indicators

✅ Server starts without errors
✅ All API endpoints respond
✅ Database models work correctly
✅ Services can be imported and instantiated
✅ Tests pass successfully
✅ Interactive documentation works
✅ JSON responses are correct

## Troubleshooting

If you get import errors, install missing dependencies:
```powershell
pip install pydantic-settings sqlalchemy aiohttp beautifulsoup4 lxml pandas numpy scikit-learn python-jose passlib bcrypt
```

If database errors occur, the SQLite database will be created automatically.

If port 8000 is in use, use:
```powershell
python -m uvicorn app.main:app --reload --port 8001
```
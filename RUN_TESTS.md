# Testing Guide for AI Research Competitive Intelligence Platform

## Step-by-Step Testing Instructions

### Step 1: Verify Python Installation
```bash
python --version
# Should show Python 3.11 or higher
```

### Step 2: Navigate to Backend Directory
```bash
cd D:/project/AI-Research-Competitive-Intelligence-Platform/backend
```

### Step 3: Create Virtual Environment (if using Python directly)
```bash
# Option A: Using venv
python -m venv venv
venv\Scripts\activate

# Option B: Using Poetry (recommended)
# First install Poetry if not already installed:
# pip install poetry
```

### Step 4: Install Dependencies
```bash
# Using Poetry (recommended)
poetry install

# Or using pip directly
pip install -r requirements.txt
```

### Step 5: Create Environment File
```bash
# Copy the example environment file
copy .env.example .env

# Or create manually with minimal settings:
echo DEBUG=True > .env
echo ENVIRONMENT=development >> .env
echo DATABASE_URL=sqlite+aiosqlite:///./test.db >> .env
echo SECRET_KEY=test-secret-key-for-development-only >> .env
```

### Step 6: Run Basic Syntax Check
```bash
python -m py_compile app/main.py
python -m py_compile app/core/config.py
python -m py_compile app/services/scraping_service.py
```

### Step 7: Run Import Tests
```bash
python -c "from app.core.config import settings; print('Config OK:', settings.PROJECT_NAME)"
python -c "from app.services.scraping_service import ScrapingConfig; print('Scraping OK')"
python -c "from app.services.data_pipeline import DataPipeline; print('Pipeline OK')"
python -c "from app.services.analytics_service import AnalyticsService; print('Analytics OK')"
```

### Step 8: Start the FastAPI Server
```bash
# Using Poetry
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using Python directly
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 9: Test API Endpoints
Open another terminal and run:

```bash
# Health check
curl http://localhost:8000/

# Detailed health check
curl http://localhost:8000/health

# API health check
curl http://localhost:8000/api/v1/health

# API documentation (open in browser)
# http://localhost:8000/docs
```

### Step 10: Run Unit Tests
```bash
# Install test dependencies
poetry install --with dev

# Run specific test files
poetry run pytest tests/test_scraping_service.py -v
poetry run pytest tests/test_data_pipeline.py -v

# Run all tests
poetry run pytest tests/ -v

# Run with coverage
poetry run pytest tests/ --cov=app --cov-report=term-missing
```

### Step 11: Test Database Connection
```bash
# The server should automatically create SQLite database
# Check for test.db file in backend directory
dir test.db
```

### Step 12: Test API with Example Requests
```bash
# Register a new user
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "testpass123",
    "full_name": "Test User"
  }'

# List competitors (should return empty list initially)
curl http://localhost:8000/api/v1/competitors

# Create a competitor
curl -X POST "http://localhost:8000/api/v1/competitors" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Competitor",
    "website": "https://testcompetitor.com",
    "industry": "Technology"
  }'

# List competitors again
curl http://localhost:8000/api/v1/competitors
```

## Troubleshooting

### Common Issues:

1. **Module not found errors:**
   ```bash
   # Make sure you're in the backend directory
   cd D:/project/AI-Research-Competitive-Intelligence-Platform/backend
   # Reinstall dependencies
   poetry install
   ```

2. **Import errors:**
   ```bash
   # Set PYTHONPATH to include app directory
   set PYTHONPATH=D:/project/AI-Research-Competitive-Intelligence-Platform/backend
   ```

3. **Database connection errors:**
   ```bash
   # Use SQLite for testing (simpler setup)
   echo DATABASE_URL=sqlite+aiosqlite:///./test.db >> .env
   ```

4. **Port already in use:**
   ```bash
   # Use a different port
   poetry run uvicorn app.main:app --reload --port 8001
   ```

## Success Indicators

✅ **Server starts without errors**
✅ **Health endpoint returns 200 OK**
✅ **API documentation accessible at /docs**
✅ **Tests pass without failures**
✅ **Database creates successfully**
✅ **API endpoints respond correctly**

## Next Steps After Testing

1. ✅ Fix any errors found
2. ✅ Document any issues
3. ✅ Update environment configuration
4. ✅ Test frontend setup
5. ✅ Test Docker services
6. ✅ Run integration tests
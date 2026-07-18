"""
Health Check Endpoint Tests

Test health check endpoints for monitoring and orchestration.
"""

import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestHealthEndpoints:
    """Test health check endpoints."""
    
    def test_general_health_check(self, client):
        """Test general health check endpoint."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "timestamp" in data
        assert "environment" in data
        assert "checks" in data
        
        # Validate status is a string
        assert isinstance(data["status"], str)
        assert data["status"] in ("healthy", "unhealthy", "degraded")
    
    def test_readiness_check(self, client):
        """Test readiness probe endpoint."""
        response = client.get("/api/v1/health/ready")
        
        # Should be 200 (healthy) or 503 (unhealthy)
        assert response.status_code in (200, 503)
        
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "timestamp" in data
        assert "environment" in data
        assert "checks" in data
        
        # If unhealthy, check for database failure
        if response.status_code == 503:
            assert data["status"] == "unhealthy"
    
    def test_liveness_check(self, client):
        """Test liveness probe endpoint."""
        response = client.get("/api/v1/health/live")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "timestamp" in data
        assert "environment" in data
        
        # Liveness check should always be healthy
        assert data["status"] == "healthy"
    
    def test_database_health_check(self, client):
        """Test database health check endpoint."""
        response = client.get("/api/v1/health/db")
        
        # Should be 200 (healthy) or 503 (unhealthy)
        assert response.status_code in (200, 503)
        
        data = response.json()
        assert "status" in data
        assert "checks" in data
        assert "database" in data["checks"]
        
        # Status should match database check
        db_status = data["checks"]["database"]
        assert db_status in ("healthy", "unhealthy")
        
        if response.status_code == 503:
            assert data["status"] == "unhealthy"
            assert db_status == "unhealthy"
    
    def test_health_response_structure(self, client):
        """Test health response has correct structure."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        
        data = response.json()
        
        # Validate required fields
        required_fields = ["status", "version", "timestamp", "environment", "checks"]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
        
        # Validate data types
        assert isinstance(data["status"], str)
        assert isinstance(data["version"], str)
        assert isinstance(data["timestamp"], str)
        assert isinstance(data["environment"], str)
        assert isinstance(data["checks"], dict)
    
    def test_health_version_format(self, client):
        """Test health endpoint returns proper version format."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        
        data = response.json()
        version = data["version"]
        
        # Version should be in semantic versioning format
        assert isinstance(version, str)
        parts = version.split(".")
        assert len(parts) >= 2  # At least major.minor
    
    def test_health_environment(self, client):
        """Test health endpoint returns correct environment."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        
        data = response.json()
        environment = data["environment"]
        
        # Environment should be valid
        assert environment in ("development", "testing", "production")
    
    def test_health_timestamp_format(self, client):
        """Test health endpoint returns proper ISO timestamp."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        
        data = response.json()
        timestamp = data["timestamp"]
        
        # Timestamp should be ISO 8601 format
        assert isinstance(timestamp, str)
        assert "T" in timestamp or ":" in timestamp  # Basic check for timestamp format
"""
Main Application Tests

Test application startup, configuration, and basic functionality.
"""

import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_app_starts():
    """Test that application starts without errors."""
    assert app is not None
    assert app.title == "AI Website Intelligence Platform API"


def test_app_configuration():
    """Test application configuration."""
    from backend.config.settings import get_settings
    
    settings = get_settings()
    
    assert settings.APP_NAME == "AI Website Intelligence Platform"
    assert settings.API_V1_PREFIX == "/api/v1"
    assert settings.APP_VERSION is not None


def test_root_redirect(client):
    """Test root endpoint redirects to docs."""
    response = client.get("/", follow_redirects=False)
    assert response.status_code in (307, 308)  # Temporary or permanent redirect


def test_routes_registered():
    """Test that routes are registered."""
    # Health endpoints should be registered
    # Check if the app has the expected routes
    assert app.routes is not None
    assert len(app.routes) > 0
    
    # Check that we have the health router registered
    # by testing if the health endpoint actually works
    client = TestClient(app)
    response = client.get("/api/v1/health")
    assert response.status_code in (200, 503)  # 200 if healthy, 503 if database not available
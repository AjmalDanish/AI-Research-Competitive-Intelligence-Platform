"""
Security testing suite for production deployment.
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from fastapi import status
from app.main_prod import app
from app.core.security_middleware import (
    InputValidator,
    PasswordSecurity,
    TokenManager,
    SecurityConfig,
    CSRFProtection,
)
from app.core.database_security import (
    SQLInjectionProtection,
    DataValidation,
    DatabaseSecurityManager,
)


class TestInputValidation:
    """Test input validation and sanitization."""

    def test_sanitize_string_basic(self):
        """Test basic string sanitization."""
        validator = InputValidator()

        # Normal input
        assert validator.sanitize_string("Hello World") == "Hello World"

        # Input with spaces
        assert validator.sanitize_string("  Hello World  ") == "Hello World"

        # Input with special characters (allowed)
        assert validator.sanitize_string("Hello@World!") == "Hello@World!"

    def test_sanitize_xss_prevention(self):
        """Test XSS prevention."""
        validator = InputValidator()

        # Script tags
        with pytest.raises(ValueError, match="dangerous content"):
            validator.sanitize_string("<script>alert('xss')</script>")

        # JavaScript protocol
        with pytest.raises(ValueError, match="dangerous content"):
            validator.sanitize_string("javascript:alert('xss')")

        # Event handlers
        with pytest.raises(ValueError, match="dangerous content"):
            validator.sanitize_string("<div onclick='alert(1)'>")

        # Data URLs
        with pytest.raises(ValueError, match="dangerous content"):
            validator.sanitize_string("data:text/html,<script>alert(1)</script>")

    def test_sanitize_length_limits(self):
        """Test length limits."""
        validator = InputValidator()

        # String too long
        long_string = "a" * 1001
        with pytest.raises(ValueError, match="exceeds maximum length"):
            validator.sanitize_string(long_string, max_length=1000)

    def test_sanitize_null_bytes(self):
        """Test null byte removal."""
        validator = InputValidator()

        # Input with null bytes
        result = validator.sanitize_string("Hello\x00World")
        assert result == "HelloWorld"

    def test_validate_email(self):
        """Test email validation."""
        validator = InputValidator()

        # Valid emails
        assert validator.validate_email("test@example.com") == True
        assert validator.validate_email("user.name+tag@example.co.uk") == True

        # Invalid emails
        assert validator.validate_email("invalid") == False
        assert validator.validate_email("@example.com") == False
        assert validator.validate_email("test@") == False

    def test_validate_url(self):
        """Test URL validation."""
        validator = InputValidator()

        # Valid URLs
        assert validator.validate_url("https://example.com") == True
        assert validator.validate_url("http://example.com/path") == True

        # Invalid URLs
        assert validator.validate_url("javascript:alert(1)") == False
        assert validator.validate_url("ftp://example.com") == False


class TestPasswordSecurity:
    """Test password security."""

    def test_password_hashing(self):
        """Test password hashing."""
        security = PasswordSecurity()

        password = "SecurePassword123!"
        hashed = security.hash_password(password)

        # Check format (salt$hash)
        assert "$" in hashed
        assert len(hashed.split("$")) == 2

        # Verify password
        assert security.verify_password(password, hashed) == True
        assert security.verify_password("WrongPassword", hashed) == False

    def test_password_strength_validation(self):
        """Test password strength validation."""
        security = PasswordSecurity()

        # Weak password
        result = security.validate_password_strength("password")
        assert result["valid"] == False
        assert result["strength"] == "weak"
        assert len(result["issues"]) > 0

        # Strong password
        result = security.validate_password_strength("SecurePass123!")
        assert result["valid"] == True
        assert result["strength"] == "strong"
        assert len(result["issues"]) == 0

        # Common password
        result = security.validate_password_strength("123456")
        assert result["valid"] == False
        assert result["score"] == 0


class TestTokenSecurity:
    """Test token security."""

    def test_token_creation_and_verification(self):
        """Test token creation and verification."""
        config = SecurityConfig()
        token_manager = TokenManager(config)

        # Create access token
        data = {"sub": "test_user", "email": "test@example.com"}
        token = token_manager.create_access_token(data)

        # Verify token
        payload = token_manager.verify_token(token)
        assert payload["sub"] == "test_user"
        assert payload["email"] == "test@example.com"
        assert payload["type"] == "access"
        assert "jti" in payload  # JWT ID

    def test_refresh_token_creation(self):
        """Test refresh token creation."""
        config = SecurityConfig()
        token_manager = TokenManager(config)

        # Create refresh token
        data = {"sub": "test_user"}
        token = token_manager.create_refresh_token(data)

        # Verify token
        payload = token_manager.verify_token(token, token_type="refresh")
        assert payload["sub"] == "test_user"
        assert payload["type"] == "refresh"

    def test_invalid_token_type(self):
        """Test invalid token type."""
        config = SecurityConfig()
        token_manager = TokenManager(config)

        # Create access token
        data = {"sub": "test_user"}
        token = token_manager.create_access_token(data)

        # Try to verify as refresh token (should fail)
        with pytest.raises(Exception):
            token_manager.verify_token(token, token_type="refresh")


class TestCSRFProtection:
    """Test CSRF protection."""

    def test_token_generation(self):
        """Test CSRF token generation."""
        csrf = CSRFProtection()

        token1 = csrf.generate_token()
        token2 = csrf.generate_token()

        # Tokens should be unique
        assert token1 != token2

        # Tokens should be URL-safe
        assert "+" not in token1
        assert "/" not in token1
        assert "=" not in token1

    def test_token_verification(self):
        """Test CSRF token verification."""
        csrf = CSRFProtection()

        token = csrf.generate_token()

        # Valid token
        assert csrf.verify_token(token, token) == True

        # Invalid token
        assert csrf.verify_token(token, "wrong_token") == False


class TestSQLInjectionProtection:
    """Test SQL injection protection."""

    def test_basic_sanitization(self):
        """Test basic SQL injection sanitization."""
        protection = SQLInjectionProtection()

        # Normal input
        assert protection.sanitize_input("John Doe") == "John Doe"

        # SQL keywords
        with pytest.raises(ValueError, match="dangerous SQL content"):
            protection.sanitize_input("'; DROP TABLE users; --")

        # UNION attack
        with pytest.raises(ValueError, match="dangerous SQL content"):
            protection.sanitize_input("' OR '1'='1")

    def test_table_name_validation(self):
        """Test table name validation."""
        protection = SQLInjectionProtection()

        # Valid table names
        assert protection.validate_table_name("users") == True
        assert protection.validate_table_name("user_profiles") == True
        assert protection.validate_table_name("_private_table") == True

        # Invalid table names
        assert protection.validate_table_name("users; DROP TABLE") == False
        assert protection.validate_table_name("1table") == False
        assert protection.validate_table_name("table with spaces") == False

    def test_column_name_validation(self):
        """Test column name validation."""
        protection = SQLInjectionProtection()

        # Valid column names
        assert protection.validate_column_name("name") == True
        assert protection.validate_column_name("user_name") == True
        assert protection.validate_column_name("_id") == True

        # Invalid column names
        assert protection.validate_column_name("name; DROP") == False
        assert protection.validate_column_name("1column") == False


class TestDataValidation:
    """Test data validation."""

    def test_email_validation(self):
        """Test email validation."""
        validator = DataValidation()

        assert validator.validate_email("test@example.com") == True
        assert validator.validate_email("invalid") == False
        assert validator.validate_email("@example.com") == False

    def test_phone_validation(self):
        """Test phone validation."""
        validator = DataValidation()

        assert validator.validate_phone("+1 234-567-8900") == True
        assert validator.validate_phone("1234567890") == True
        assert validator.validate_phone("abc") == False

    def test_url_validation(self):
        """Test URL validation."""
        validator = DataValidation()

        assert validator.validate_url("https://example.com") == True
        assert validator.validate_url("http://example.com/path") == True
        assert validator.validate_url("javascript:alert(1)") == False

    def test_ipv4_validation(self):
        """Test IPv4 validation."""
        validator = DataValidation()

        assert validator.validate_ipv4("192.168.1.1") == True
        assert validator.validate_ipv4("255.255.255.255") == True
        assert validator.validate_ipv4("256.1.1.1") == False
        assert validator.validate_ipv4("192.168.1") == False

    def test_username_validation(self):
        """Test username validation."""
        validator = DataValidation()

        assert validator.validate_username("john_doe") == True
        assert validator.validate_username("JohnDoe123") == True
        assert validator.validate_username("ab") == False  # Too short
        assert validator.validate_username("a" * 21) == False  # Too long
        assert validator.validate_username("john@doe") == False  # Invalid character


class TestSecurityEndpoints:
    """Test security endpoints."""

    def test_root_endpoint_security_headers(self):
        """Test security headers on root endpoint."""
        client = TestClient(app)
        response = client.get("/")

        # Check security headers
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("X-Frame-Options") == "DENY"
        assert response.headers.get("X-XSS-Protection") == "1; mode=block"
        assert "Content-Security-Policy" in response.headers

    def test_health_endpoint(self):
        """Test health endpoint."""
        client = TestClient(app)
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "services" in data

    def test_cors_headers(self):
        """Test CORS headers."""
        client = TestClient(app)
        response = client.options("/")

        # Check CORS headers
        assert "access-control-allow-origin" in response.headers


class TestRateLimiting:
    """Test rate limiting."""

    def test_rate_limit_headers(self):
        """Test rate limit headers."""
        client = TestClient(app)
        response = client.get("/")

        # Check rate limit headers
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

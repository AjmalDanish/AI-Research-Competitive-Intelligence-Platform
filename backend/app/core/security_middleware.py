"""
Security utilities and middleware for production deployment.
"""

import os
import secrets
import hashlib
import re
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from functools import wraps
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
import ipaddress
import redis.asyncio as redis
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded


# Security configuration
class SecurityConfig:
    SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

    # Rate limiting
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    RATE_LIMIT_PER_HOUR: int = int(os.getenv("RATE_LIMIT_PER_HOUR", "1000"))

    # IP whitelist
    IP_WHITELIST_ENABLED: bool = os.getenv("IP_WHITELIST_ENABLED", "false").lower() == "true"
    IP_WHITELIST: list = (
        os.getenv("IP_WHITELIST", "").split(",") if os.getenv("IP_WHITELIST") else []
    )

    # CORS
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "*").split(",")
    CORS_ALLOW_CREDENTIALS: bool = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"
    CORS_ALLOW_METHODS: list = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    CORS_ALLOW_HEADERS: list = ["*"]

    # Session security
    SESSION_TIMEOUT_MINUTES: int = int(os.getenv("SESSION_TIMEOUT_MINUTES", "30"))
    MAX_CONCURRENT_SESSIONS: int = int(os.getenv("MAX_CONCURRENT_SESSIONS", "5"))


security = HTTPBearer()

# Rate limiter setup
limiter = Limiter(key_func=get_remote_address)


class InputValidator:
    """Input validation and sanitization."""

    @staticmethod
    def sanitize_string(input_string: str, max_length: int = 1000) -> str:
        """Sanitize string input."""
        if not isinstance(input_string, str):
            raise ValueError("Input must be a string")

        # Remove null bytes
        input_string = input_string.replace("\x00", "")

        # Limit length
        if len(input_string) > max_length:
            raise ValueError(f"Input exceeds maximum length of {max_length}")

        # Basic XSS prevention
        dangerous_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"data:text/html",
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, input_string, re.IGNORECASE):
                raise ValueError("Input contains potentially dangerous content")

        return input_string.strip()

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(pattern, email) is not None

    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL format."""
        pattern = r"^https?://[^\s/$.?#].[^\s]*$"
        return re.match(pattern, url) is not None

    @staticmethod
    def sanitize_html(input_string: str) -> str:
        """Basic HTML sanitization."""
        if not isinstance(input_string, str):
            raise ValueError("Input must be a string")

        # Remove script tags and event handlers
        input_string = re.sub(
            r"<script[^>]*>.*?</script>", "", input_string, flags=re.IGNORECASE | re.DOTALL
        )
        input_string = re.sub(r"on\w+\s*=", "", input_string, flags=re.IGNORECASE)

        return input_string.strip()


class IPWhitelist:
    """IP whitelist management."""

    def __init__(self, enabled: bool = False, whitelist: list = None):
        self.enabled = enabled
        self.whitelist = whitelist or []

    def is_allowed(self, ip_address: str) -> bool:
        """Check if IP address is allowed."""
        if not self.enabled:
            return True

        try:
            ip = ipaddress.ip_address(ip_address)

            for allowed in self.whitelist:
                try:
                    if "/" in allowed:  # CIDR notation
                        if ip in ipaddress.ip_network(allowed):
                            return True
                    else:  # Single IP
                        if ip == ipaddress.ip_address(allowed):
                            return True
                except ValueError:
                    continue

            return False
        except ValueError:
            return False


class TokenManager:
    """JWT token management with enhanced security."""

    def __init__(self, config: SecurityConfig):
        self.config = config

    def create_access_token(
        self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT access token."""
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.config.ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update(
            {
                "exp": expire,
                "iat": datetime.utcnow(),
                "type": "access",
                "jti": secrets.token_urlsafe(16),  # JWT ID for revocation
            }
        )

        encoded_jwt = jwt.encode(to_encode, self.config.SECRET_KEY, algorithm=self.config.ALGORITHM)

        return encoded_jwt

    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create JWT refresh token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.config.REFRESH_TOKEN_EXPIRE_DAYS)

        to_encode.update(
            {
                "exp": expire,
                "iat": datetime.utcnow(),
                "type": "refresh",
                "jti": secrets.token_urlsafe(16),
            }
        )

        encoded_jwt = jwt.encode(to_encode, self.config.SECRET_KEY, algorithm=self.config.ALGORITHM)

        return encoded_jwt

    def verify_token(self, token: str, token_type: str = "access") -> Dict[str, Any]:
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(token, self.config.SECRET_KEY, algorithms=[self.config.ALGORITHM])

            # Check token type
            if payload.get("type") != token_type:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type"
                )

            return payload

        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token: {str(e)}"
            )


class PasswordSecurity:
    """Password security utilities."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using SHA-256 with salt."""
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}${password_hash}"

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        try:
            salt, password_hash = hashed_password.split("$")
            computed_hash = hashlib.sha256((plain_password + salt).encode()).hexdigest()
            return computed_hash == password_hash
        except (ValueError, AttributeError):
            return False

    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, Any]:
        """Validate password strength."""
        issues = []
        score = 0

        # Length check
        if len(password) < 8:
            issues.append("Password must be at least 8 characters long")
        else:
            score += 1

        # Complexity checks
        if not re.search(r"[a-z]", password):
            issues.append("Password must contain lowercase letters")
        else:
            score += 1

        if not re.search(r"[A-Z]", password):
            issues.append("Password must contain uppercase letters")
        else:
            score += 1

        if not re.search(r"\d", password):
            issues.append("Password must contain numbers")
        else:
            score += 1

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            issues.append("Password must contain special characters")
        else:
            score += 1

        # Common password check (simplified)
        common_passwords = ["password", "123456", "qwerty", "admin"]
        if password.lower() in common_passwords:
            issues.append("Password is too common")
            score = 0

        strength = "weak"
        if score >= 4:
            strength = "strong"
        elif score >= 2:
            strength = "medium"

        return {"valid": score >= 3, "strength": strength, "score": score, "issues": issues}


class SecurityHeaders:
    """Security headers for HTTP responses."""

    @staticmethod
    def get_headers() -> Dict[str, str]:
        """Get security headers."""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
        }


class CSRFProtection:
    """CSRF protection utilities."""

    @staticmethod
    def generate_token() -> str:
        """Generate CSRF token."""
        return secrets.token_urlsafe(32)

    @staticmethod
    def verify_token(token: str, stored_token: str) -> bool:
        """Verify CSRF token."""
        return secrets.compare_digest(token, stored_token)


class SecurityMiddleware:
    """Comprehensive security middleware."""

    def __init__(self, config: SecurityConfig):
        self.config = config
        self.input_validator = InputValidator()
        self.ip_whitelist = IPWhitelist(
            enabled=config.IP_WHITELIST_ENABLED, whitelist=config.IP_WHITELIST
        )
        self.token_manager = TokenManager(config)
        self.password_security = PasswordSecurity()
        self.csrf_protection = CSRFProtection()

    async def check_ip_whitelist(self, request: Request) -> bool:
        """Check if IP is whitelisted."""
        client_ip = request.client.host if request.client else "unknown"
        return self.ip_whitelist.is_allowed(client_ip)

    async def validate_request(self, request: Request) -> None:
        """Validate incoming request."""
        # Check IP whitelist
        if not await self.check_ip_whitelist(request):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="IP address not allowed"
            )

        # Validate content type for POST/PUT
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("content-type", "")
            if "application/json" not in content_type and "multipart/form-data" not in content_type:
                raise HTTPException(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    detail="Unsupported content type",
                )


# Initialize security components
security_config = SecurityConfig()
security_middleware = SecurityMiddleware(security_config)
token_manager = TokenManager(security_config)
password_security = PasswordSecurity()

# Export components
__all__ = [
    "SecurityConfig",
    "InputValidator",
    "IPWhitelist",
    "TokenManager",
    "PasswordSecurity",
    "SecurityHeaders",
    "CSRFProtection",
    "SecurityMiddleware",
    "security",
    "limiter",
    "security_config",
    "security_middleware",
    "token_manager",
    "password_security",
]

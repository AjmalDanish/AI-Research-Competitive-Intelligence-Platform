"""
Security utilities for authentication and authorization.

This module provides functions for password hashing, JWT token creation/validation,
and API key authentication.
"""

from datetime import datetime, timedelta
from typing import Optional, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer token security
security = HTTPBearer(auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password
        
    Returns:
        bool: True if passwords match, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password.
    
    Args:
        password: Plain text password
        
    Returns:
        str: Hashed password
    """
    # Truncate password to 72 characters for bcrypt
    if len(password) > 72:
        password = password[:72]
    return pwd_context.hash(password)


def create_access_token(
    subject: str | Any,
    expires_delta: Optional[timedelta] = None,
    additional_claims: Optional[dict] = None
) -> str:
    """
    Create a JWT access token.
    
    Args:
        subject: Token subject (usually user ID)
        expires_delta: Token expiration time delta
        additional_claims: Additional claims to include in token
        
    Returns:
        str: Encoded JWT token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {"exp": expire, "sub": str(subject)}
    if additional_claims:
        to_encode.update(additional_claims)
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and validate a JWT access token.
    
    Args:
        token: JWT token to decode
        
    Returns:
        Optional[dict]: Decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def verify_token(token: str) -> Optional[str]:
    """
    Verify a JWT token and return the subject.
    
    Args:
        token: JWT token to verify
        
    Returns:
        Optional[str]: Subject from token or None if invalid
    """
    payload = decode_access_token(token)
    if payload is None:
        return None
    return payload.get("sub")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Optional[str]:
    """
    Get current user from JWT token.
    
    Args:
        credentials: HTTP Bearer credentials
        
    Returns:
        Optional[str]: Current user ID or None if not authenticated
        
    Raises:
        HTTPException: If token is invalid
    """
    if credentials is None:
        return None
    
    token = credentials.credentials
    user_id = verify_token(token)
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_id


async def require_auth(
    user_id: str = Depends(get_current_user)
) -> str:
    """
    Require authentication for an endpoint.
    
    Args:
        user_id: Current user ID from token
        
    Returns:
        str: User ID
        
    Raises:
        HTTPException: If not authenticated
    """
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    return user_id


def get_api_key(api_key_header: str = None) -> Optional[str]:
    """
    Get and validate API key from headers.
    
    Args:
        api_key_header: API key from request header
        
    Returns:
        Optional[str]: Valid API key or None
    """
    if api_key_header and api_key_header.startswith(settings.SECRET_KEY[:8]):
        return api_key_header
    return None


async def verify_api_key(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Verify API key for endpoint access.
    
    Args:
        credentials: HTTP Bearer credentials
        
    Returns:
        str: Valid API key
        
    Raises:
        HTTPException: If API key is invalid
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    api_key = credentials.credentials
    if not api_key.startswith(settings.SECRET_KEY[:8]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return api_key


class TokenData:
    """Token data model."""
    
    def __init__(self, user_id: Optional[str] = None, scopes: list = None):
        self.user_id = user_id
        self.scopes = scopes or []


def create_refresh_token(subject: str | Any) -> str:
    """
    Create a JWT refresh token.
    
    Args:
        subject: Token subject (usually user ID)
        
    Returns:
        str: Encoded refresh token
    """
    expires_delta = timedelta(days=30)
    return create_access_token(subject, expires_delta, {"type": "refresh"})


def get_current_user_dependency(optional: bool = False):
    """
    Create a dependency for getting the current user.
    
    Args:
        optional: If True, returns None instead of raising exception
        
    Returns:
        Dependency function that returns user_id or None
    """
    async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> Optional[str]:
        """
        Get the current user from JWT token.
        
        Args:
            credentials: HTTP authorization credentials
            
        Returns:
            str: User ID if authenticated
            
        Raises:
            HTTPException: If authentication fails
        """
        if credentials is None:
            if optional:
                return None
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        token = credentials.credentials
        user_id = verify_token(token)
        
        if user_id is None:
            if optional:
                return None
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user_id
    
    return get_current_user
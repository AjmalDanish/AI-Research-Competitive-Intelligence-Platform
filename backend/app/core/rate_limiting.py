"""
Rate limiting middleware for API protection.
"""

from typing import Dict, Optional, Callable
from functools import wraps
from datetime import datetime, timedelta
import redis.asyncio as redis
from fastapi import Request, HTTPException, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import json
import os


class RateLimitConfig:
    """Rate limiting configuration."""

    # Enable/disable rate limiting
    ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"

    # Rate limits (requests per time period)
    PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    PER_HOUR: int = int(os.getenv("RATE_LIMIT_PER_HOUR", "1000"))
    PER_DAY: int = int(os.getenv("RATE_LIMIT_PER_DAY", "10000"))

    # Redis configuration
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REDIS_PREFIX: str = os.getenv("RATE_LIMIT_REDIS_PREFIX", "ratelimit:")

    # Whitelist settings
    WHITELIST_IPS: list = os.getenv("RATE_LIMIT_WHITELIST", "").split(",")
    WHITELIST_USERS: list = os.getenv("RATE_LIMIT_WHITELIST_USERS", "").split(",")

    # Ban settings
    BAN_THRESHOLD: int = int(os.getenv("RATE_LIMIT_BAN_THRESHOLD", "100"))
    BAN_DURATION_MINUTES: int = int(os.getenv("RATE_LIMIT_BAN_DURATION", "60"))


class RateLimiter:
    """Advanced rate limiter with Redis backend."""

    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.redis_client: Optional[redis.Redis] = None
        self.local_cache: Dict[str, Dict] = {}

    async def initialize(self):
        """Initialize Redis connection."""
        if self.config.ENABLED:
            try:
                self.redis_client = await redis.from_url(
                    self.config.REDIS_URL, encoding="utf-8", decode_responses=True
                )
            except Exception as e:
                print(f"Failed to connect to Redis: {e}. Using local cache.")

    async def close(self):
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()

    def _get_key(self, identifier: str, period: str) -> str:
        """Generate Redis key for rate limit."""
        return f"{self.config.REDIS_PREFIX}{period}:{identifier}"

    def _get_period_seconds(self, period: str) -> int:
        """Get period in seconds."""
        periods = {"minute": 60, "hour": 3600, "day": 86400}
        return periods.get(period, 60)

    def _get_limit(self, period: str) -> int:
        """Get limit for period."""
        limits = {
            "minute": self.config.PER_MINUTE,
            "hour": self.config.PER_HOUR,
            "day": self.config.PER_DAY,
        }
        return limits.get(period, self.config.PER_MINUTE)

    async def is_whitelisted(self, identifier: str, is_ip: bool = True) -> bool:
        """Check if identifier is whitelisted."""
        whitelist = self.config.WHITELIST_IPS if is_ip else self.config.WHITELIST_USERS
        return identifier in whitelist

    async def check_rate_limit(
        self, identifier: str, period: str = "minute", is_ip: bool = True
    ) -> Dict[str, any]:
        """
        Check rate limit for identifier.

        Args:
            identifier: IP address or user ID
            period: Time period (minute, hour, day)
            is_ip: Whether identifier is IP address

        Returns:
            Dictionary with limit information
        """
        # Check whitelist
        if await self.is_whitelisted(identifier, is_ip):
            return {
                "allowed": True,
                "remaining": float("inf"),
                "limit": float("inf"),
                "reset": None,
            }

        # Check if banned
        if await self.is_banned(identifier):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Banned for {self.config.BAN_DURATION_MINUTES} minutes.",
            )

        key = self._get_key(identifier, period)
        limit = self._get_limit(period)
        period_seconds = self._get_period_seconds(period)

        try:
            if self.redis_client:
                return await self._check_redis(key, limit, period_seconds)
            else:
                return self._check_local(key, limit, period_seconds)
        except Exception as e:
            print(f"Rate limit check failed: {e}")
            return {
                "allowed": True,
                "remaining": float("inf"),
                "limit": float("inf"),
                "reset": None,
            }

    async def _check_redis(self, key: str, limit: int, period_seconds: int) -> Dict[str, any]:
        """Check rate limit using Redis."""
        pipe = self.redis_client.pipeline()
        now = datetime.utcnow().timestamp()

        # Remove old entries
        pipe.zremrangebyscore(key, 0, now - period_seconds)

        # Count current requests
        pipe.zcard(key)

        # Add current request
        pipe.zadd(key, {str(now): now})

        # Set expiration
        pipe.expire(key, period_seconds + 60)

        results = await pipe.execute()
        current_count = results[1]

        # Check if over limit
        reset_time = now + period_seconds
        if current_count >= limit:
            # Increment ban counter
            await self._increment_ban_counter(key)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Maximum {limit} requests per {period_seconds//60} minutes.",
            )

        return {
            "allowed": True,
            "remaining": limit - current_count - 1,
            "limit": limit,
            "reset": reset_time,
        }

    def _check_local(self, key: str, limit: int, period_seconds: int) -> Dict[str, any]:
        """Check rate limit using local cache (fallback)."""
        now = datetime.utcnow()

        if key not in self.local_cache:
            self.local_cache[key] = {"requests": [], "banned_until": None}

        cache = self.local_cache[key]

        # Check if banned
        if cache["banned_until"] and now < cache["banned_until"]:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Banned until {cache['banned_until']}.",
            )

        # Clean old requests
        cache["requests"] = [
            req_time
            for req_time in cache["requests"]
            if now - req_time < timedelta(seconds=period_seconds)
        ]

        # Check limit
        if len(cache["requests"]) >= limit:
            cache["banned_until"] = now + timedelta(minutes=self.config.BAN_DURATION_MINUTES)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Maximum {limit} requests per {period_seconds//60} minutes.",
            )

        # Add current request
        cache["requests"].append(now)
        reset_time = now + timedelta(seconds=period_seconds)

        return {
            "allowed": True,
            "remaining": limit - len(cache["requests"]),
            "limit": limit,
            "reset": reset_time.timestamp(),
        }

    async def _increment_ban_counter(self, key: str):
        """Increment ban counter for identifier."""
        ban_key = f"{key}:ban_count"
        try:
            current = await self.redis_client.incr(ban_key)
            await self.redis_client.expire(ban_key, 3600)  # 1 hour

            if current >= self.config.BAN_THRESHOLD:
                # Ban the identifier
                ban_until = datetime.utcnow() + timedelta(minutes=self.config.BAN_DURATION_MINUTES)
                await self.redis_client.setex(
                    f"{key}:banned", self.config.BAN_DURATION_MINUTES * 60, "true"
                )
        except Exception as e:
            print(f"Failed to increment ban counter: {e}")

    async def is_banned(self, identifier: str) -> bool:
        """Check if identifier is banned."""
        if not self.redis_client:
            key = f"{self.config.REDIS_PREFIX}{identifier}"
            if key in self.local_cache:
                cache = self.local_cache[key]
                if cache["banned_until"] and datetime.utcnow() < cache["banned_until"]:
                    return True
            return False

        try:
            return (
                await self.redis_client.exists(f"{self.config.REDIS_PREFIX}{identifier}:banned") > 0
            )
        except Exception as e:
            print(f"Failed to check ban status: {e}")
            return False


def rate_limit(period: str = "minute", is_ip: bool = True):
    """
    Decorator for rate limiting endpoints.

    Args:
        period: Time period (minute, hour, day)
        is_ip: Whether to rate limit by IP (False for user ID)
    """

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get request from args
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

            if not request:
                return await func(*args, **kwargs)

            # Get identifier
            if is_ip:
                identifier = get_remote_address(request)
            else:
                # Try to get user ID from request state
                identifier = getattr(request.state, "user_id", get_remote_address(request))

            # Check rate limit
            config = RateLimitConfig()
            limiter = RateLimiter(config)
            await limiter.initialize()

            try:
                result = await limiter.check_rate_limit(identifier, period, is_ip)
                # Add rate limit headers to response
                response = await func(*args, **kwargs)
                if hasattr(response, "headers"):
                    response.headers["X-RateLimit-Limit"] = str(result["limit"])
                    response.headers["X-RateLimit-Remaining"] = str(result["remaining"])
                    if result["reset"]:
                        response.headers["X-RateLimit-Reset"] = str(int(result["reset"]))
                return response
            finally:
                await limiter.close()

        return wrapper

    return decorator


# Initialize global rate limiter
rate_limit_config = RateLimitConfig()
global_rate_limiter = RateLimiter(rate_limit_config)


async def initialize_rate_limiter():
    """Initialize global rate limiter."""
    await global_rate_limiter.initialize()


async def close_rate_limiter():
    """Close global rate limiter."""
    await global_rate_limiter.close()


__all__ = [
    "RateLimitConfig",
    "RateLimiter",
    "rate_limit",
    "global_rate_limiter",
    "initialize_rate_limiter",
    "close_rate_limiter",
]

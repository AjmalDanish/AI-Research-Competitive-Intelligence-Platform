"""
Retry Manager

Exponential backoff retry logic following Clean Architecture.

Purpose:
- Handle transient failures with retries
- Implement exponential backoff strategy
- Support configurable retry policies
- Track retry attempts

Clean Architecture:
- Infrastructure layer
- No business logic
- Pure retry logic
"""

import asyncio
import random
from collections.abc import Awaitable, Callable
from functools import wraps
from typing import Any, TypeVar

from backend.config.logging import get_logger
from backend.crawler.exceptions import (
    CrawlerException,
    NetworkException,
    RateLimitException,
    ServerErrorException,
    TimeoutException,
)

logger = get_logger(__name__)

# Generic type for async function return value
T = TypeVar("T")


class RetryManager:
    """
    Retry manager with exponential backoff.

    This class provides retry logic for handling transient failures
    during crawling operations. It implements exponential backoff
    with configurable parameters.
    """

    # Exception types that should be retried
    RETRYABLE_EXCEPTIONS = (
        TimeoutException,
        NetworkException,
        ServerErrorException,
        RateLimitException,
    )

    # Exception types that should NOT be retried
    NON_RETRYABLE_EXCEPTIONS = (
        ValueError,  # Invalid parameters
        TypeError,  # Type errors
    )

    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: int = 1,
        multiplier: float = 2.0,
        max_delay: int = 10,
        jitter: bool = True,
        jitter_factor: float = 0.1,
    ):
        """
        Initialize retry manager.

        Args:
            max_retries: Maximum number of retry attempts
            initial_delay: Initial delay between retries (seconds)
            multiplier: Multiplier for exponential backoff
            max_delay: Maximum delay between retries (seconds)
            jitter: Whether to add random jitter to delays
            jitter_factor: Amount of jitter to add (0.0-1.0)
        """
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.multiplier = multiplier
        self.max_delay = max_delay
        self.jitter = jitter
        self.jitter_factor = jitter_factor

    def should_retry(self, exception: Exception) -> bool:
        """
        Determine if an exception should trigger a retry.

        Args:
            exception: The exception that occurred

        Returns:
            True if should retry, False otherwise
        """
        # Non-retryable exceptions
        if isinstance(exception, self.NON_RETRYABLE_EXCEPTIONS):
            return False

        # Check for specific crawler exceptions
        if isinstance(exception, CrawlerException):
            # Robots denial should not be retried
            if "RobotsDenied" in exception.__class__.__name__:
                return False

            # Validation errors should not be retried
            if "Validation" in exception.__class__.__name__:
                return False

            # Content length errors should not be retried
            if "ContentLength" in exception.__class__.__name__:
                return False

            # Browser errors might be retryable
            if "Browser" in exception.__class__.__name__:
                return True

            # Redirect errors should not be retried
            if "Redirect" in exception.__class__.__name__:
                return False

        # Retry network errors
        if isinstance(exception, (TimeoutException, NetworkException)):
            return True

        # Retry server errors and rate limits
        if isinstance(exception, (ServerErrorException, RateLimitException)):
            return True

        # Don't retry unknown exceptions
        return False

    def calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay for a retry attempt using exponential backoff.

        Args:
            attempt: Current retry attempt (0-indexed)

        Returns:
            Delay in seconds
        """
        # Calculate exponential delay
        delay = min(
            self.initial_delay * (self.multiplier**attempt),
            self.max_delay,
        )

        # Add jitter if enabled
        if self.jitter:
            jitter_amount = delay * self.jitter_factor
            jitter = random.uniform(-jitter_amount, jitter_amount)
            delay = max(0.1, delay + jitter)  # Ensure minimum delay

        return delay

    async def execute_with_retry(
        self,
        func: Callable[..., Awaitable[T]],
        *args,
        **kwargs,
    ) -> T:
        """
        Execute function with retry logic.

        Args:
            func: Async function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function return value

        Raises:
            Last exception if all retries fail
        """
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                if attempt > 0:
                    logger.info(
                        f"Retry attempt {attempt}/{self.max_retries}",
                        func=func.__name__,
                    )

                return await func(*args, **kwargs)

            except Exception as e:
                last_exception = e

                # Check if we should retry
                if not self.should_retry(e):
                    logger.error(
                        f"Non-retryable exception in {func.__name__}: {type(e).__name__} - {str(e)}"
                    )
                    raise

                # Check if we have more retries
                if attempt >= self.max_retries:
                    logger.error(
                        f"Max retries exceeded for {func.__name__}: {str(e)} (attempts={attempt})"
                    )
                    raise

                # Calculate delay for next retry
                delay = self.calculate_delay(attempt)

                logger.warning(
                    f"Retryable exception in {func.__name__}, retrying in {delay:.2f}s: {str(e)} (attempt={attempt})"
                )

                # Wait before next retry
                await asyncio.sleep(delay)

        # This should never be reached, but just in case
        if last_exception:
            raise last_exception

    def get_retry_stats(self) -> dict[str, Any]:
        """
        Get retry statistics (placeholder for future metrics).

        Returns:
            Dictionary with retry statistics
        """
        return {
            "max_retries": self.max_retries,
            "initial_delay": self.initial_delay,
            "multiplier": self.multiplier,
            "max_delay": self.max_delay,
            "jitter": self.jitter,
        }


def retry_on_failure(
    max_retries: int = 3,
    initial_delay: int = 1,
    multiplier: float = 2.0,
    max_delay: int = 10,
    jitter: bool = True,
):
    """
    Decorator to add retry logic to async functions.

    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay between retries (seconds)
        multiplier: Multiplier for exponential backoff
        max_delay: Maximum delay between retries (seconds)
        jitter: Whether to add random jitter to delays

    Returns:
        Decorator function
    """

    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        """Decorator that wraps function with retry logic."""

        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            """Wrapper function that adds retry logic."""
            retry_manager = RetryManager(
                max_retries=max_retries,
                initial_delay=initial_delay,
                multiplier=multiplier,
                max_delay=max_delay,
                jitter=jitter,
            )

            return await retry_manager.execute_with_retry(func, *args, **kwargs)

        return wrapper

    return decorator


# Export for easy import
__all__ = [
    "RetryManager",
    "retry_on_failure",
]

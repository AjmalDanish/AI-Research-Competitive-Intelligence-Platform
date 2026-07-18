"""
Retry Manager Tests

Unit tests for retry logic with exponential backoff.
"""

import asyncio
import pytest

from backend.crawler.retry import RetryManager, retry_on_failure
from backend.crawler.exceptions import (
    TimeoutException,
    NetworkException,
    ValidationError,
    RobotsDeniedException,
)


class TestRetryManager:
    """Test retry manager logic."""
    
    @pytest.fixture
    def retry_manager(self):
        """Create retry manager instance."""
        return RetryManager(
            max_retries=3,
            initial_delay=1,
            multiplier=2.0,
            max_delay=10,
        )
    
    @pytest.mark.asyncio
    async def test_successful_execution_no_retry(self, retry_manager):
        """Test that successful execution doesn't trigger retries."""
        call_count = 0
        
        async def successful_func():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = await retry_manager.execute_with_retry(successful_func)
        
        assert result == "success"
        assert call_count == 1
    
    @pytest.mark.asyncio
    async def test_retry_on_transient_failure(self, retry_manager):
        """Test that transient failures trigger retries."""
        call_count = 0
        
        async def transient_func():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise TimeoutException("Timeout", url="https://example.com", timeout_seconds=30, operation="test")
            return "success"
        
        result = await retry_manager.execute_with_retry(transient_func)
        
        assert result == "success"
        assert call_count == 2  # Failed once, succeeded on retry
    
    @pytest.mark.asyncio
    async def test_max_retries_exceeded(self, retry_manager):
        """Test that max retries limit is respected."""
        call_count = 0
        
        async def failing_func():
            nonlocal call_count
            call_count += 1
            raise NetworkException("Network error", url="https://example.com")
        
        with pytest.raises(NetworkException):
            await retry_manager.execute_with_retry(failing_func)
        
        # Should have attempted initial + 3 retries = 4 total
        assert call_count == 4
    
    @pytest.mark.asyncio
    async def test_non_retryable_exception(self, retry_manager):
        """Test that non-retryable exceptions are not retried."""
        call_count = 0
        
        async def validation_error_func():
            nonlocal call_count
            call_count += 1
            raise ValidationError("Invalid URL", url="bad-url")
        
        with pytest.raises(ValidationError):
            await retry_manager.execute_with_retry(validation_error_func)
        
        # Should not have retried
        assert call_count == 1
    
    @pytest.mark.asyncio
    async def test_robots_denied_not_retried(self, retry_manager):
        """Test that robots denial exceptions are not retried."""
        call_count = 0
        
        async def robots_denied_func():
            nonlocal call_count
            call_count += 1
            raise RobotsDeniedException(
                "robots.txt denied",
                url="https://example.com",
                user_agent="test",
            )
        
        with pytest.raises(RobotsDeniedException):
            await retry_manager.execute_with_retry(robots_denied_func)
        
        # Should not have retried
        assert call_count == 1
    
    def test_should_retry_transient_errors(self, retry_manager):
        """Test retry decision for transient errors."""
        assert retry_manager.should_retry(TimeoutException("Timeout", url="https://example.com", timeout_seconds=30))
        assert retry_manager.should_retry(NetworkException("Network error", url="https://example.com"))
    
    def test_should_not_retry_permanent_errors(self, retry_manager):
        """Test retry decision for permanent errors."""
        assert not retry_manager.should_retry(ValidationError("Invalid URL", url="bad"))
        assert not retry_manager.should_retry(RobotsDeniedException("Denied", url="https://example.com", user_agent="test"))
        assert not retry_manager.should_retry(ValueError("Bad input"))
    
    def test_calculate_delay_exponential_backoff(self, retry_manager):
        """Test exponential backoff delay calculation."""
        # Disable jitter for predictable testing
        retry_manager.jitter = False
        
        delays = [retry_manager.calculate_delay(attempt) for attempt in range(4)]
        
        # First attempt should have no delay (initial call)
        assert delays[0] >= 0.1  # Minimum delay
        
        # Second attempt should have initial delay
        assert abs(delays[1] - 1.0) < 0.01
        
        # Third attempt should have 2x initial delay
        assert abs(delays[2] - 2.0) < 0.01
        
        # Fourth attempt should have 4x initial delay
        assert abs(delays[3] - 4.0) < 0.01
    
    def test_max_delay_limit(self, retry_manager):
        """Test that max delay is respected."""
        # Even with many attempts, delay should not exceed max_delay
        for attempt in range(100):
            delay = retry_manager.calculate_delay(attempt)
            assert delay <= retry_manager.max_delay + 1.0  # +1.0 for jitter


class TestRetryDecorator:
    """Test retry decorator."""
    
    @pytest.mark.asyncio
    async def test_retry_decorator_on_function(self):
        """Test retry decorator applied to function."""
        call_count = 0
        
        @retry_on_failure(max_retries=2, initial_delay=0.1)
        async def failing_func():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise NetworkException("Network error", url="https://example.com")
            return "success"
        
        result = await failing_func()
        
        assert result == "success"
        assert call_count == 2
    
    @pytest.mark.asyncio
    async def test_retry_decorator_with_different_params(self):
        """Test retry decorator with custom parameters."""
        call_count = 0
        
        @retry_on_failure(max_retries=1, initial_delay=0.05)
        async def failing_func():
            nonlocal call_count
            call_count += 1
            raise NetworkException("Network error", url="https://example.com")
        
        with pytest.raises(NetworkException):
            await failing_func()
        
        # Should have attempted initial + 1 retry = 2 total
        assert call_count == 2
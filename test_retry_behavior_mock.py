"""
Demonstrate retry behavior using mock services.

Shows retry behavior for different error types.
"""

import asyncio
from datetime import datetime, timezone
from typing import Protocol
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Mock ICrawler for testing
class MockCrawler(Protocol):
    """Mock crawler for testing retry behavior."""
    
    @property
    def crawler_name(self) -> str:
        return "mock"
    
    async def crawl(self, url: str, config=None) -> dict:
        """Mock crawl that simulates different error scenarios."""
        from backend.core.domain.crawler import CrawlResult, CrawlMetrics
        
        async def simulate_success():
            return CrawlResult(
                url=url,
                final_url=url,
                status_code=200,
                html="<html>Success</html>",
                content_type="text/html",
                content_length=20,
                crawler_name="mock",
                metrics=CrawlMetrics(
                    start_time=datetime.now(timezone.utc),
                    end_time=datetime.now(timezone.utc),
                    retry_count=0,
                    robots_checked=True,
                    robots_allowed=True,
                ),
            )
        
        async def simulate_timeout():
            from backend.crawler.exceptions import TimeoutException
            
            self.call_count += 1
            if self.call_count < 2:
                raise TimeoutException("Timeout", url=url, timeout_seconds=30, operation="crawl")
            else:
                return await simulate_success()
        
        async def simulate_500():
            from backend.crawler.exceptions import ServerErrorException
            
            self.call_count += 1
            if self.call_count < 2:
                raise ServerErrorException("Server error", url=url, status_code=500)
            else:
                return await simulate_success()
        
        async def simulate_429():
            from backend.crawler.exceptions import RateLimitException
            
            self.call_count += 1
            if self.call_count < 2:
                raise RateLimitException("Rate limited", url=url, status_code=429)
            else:
                return await simulate_success()
        
        async def simulate_invalid_url():
            from backend.crawler.exceptions import ValidationError
            
            raise ValidationError("Invalid URL", url="not-a-valid-url")
        
        async def simulate_robots_denial():
            from backend.crawler.exceptions import RobotsDeniedException
            
            raise RobotsDeniedException(
                "robots.txt denies access: /private",
                url=url,
                user_agent="TestBot/1.0",
            )
        
        # Route to correct scenario
        if self.scenario == "timeout":
            self.call_count = 0
            return await simulate_timeout()
        elif self.scenario == "500_error":
            self.call_count = 0
            return await simulate_500()
        elif self.scenario == "429_error":
            self.call_count = 0
            return await simulate_429()
        elif self.scenario == "invalid_url":
            self.call_count = 0
            return await simulate_invalid_url()
        elif self.scenario == "robots_denial":
            self.call_count = 0
            return await simulate_robots_denial()
        else:
            return await simulate_success()
    
    def __init__(self, scenario: str = "success"):
        self.scenario = scenario
        self.call_count = 0


async def demonstrate_retry_behavior():
    """Demonstrate retry behavior for different error types."""
    
    print("=" * 80)
    print("RETRY BEHAVIOR VERIFICATION (Mock)")
    print("=" * 80)
    
    from backend.crawler.exceptions import (
        TimeoutException,
        ValidationError,
        RobotsDeniedException,
        ServerErrorException,
        RateLimitException,
    )
    
    test_cases = [
        ("timeout", "should retry", TimeoutException),
        ("500_error", "should retry", ServerErrorException),
        ("429_error", "should retry", RateLimitException),
        ("invalid_url", "no retry", ValidationError),
        ("robots_denial", "no retry", RobotsDeniedException),
    ]
    
    results = {}
    
    for scenario, expected_behavior, exception_class in test_cases:
        mock = MockCrawler(scenario)
        
        print(f"\n{scenario.upper().replace('_', ' ')} ({expected_behavior})")
        print("-" * 80)
        
        try:
            result = await mock.crawl("https://example.com")
            retry_count = result["metrics"]["retry_count"]
            results[scenario] = retry_count
            
            if expected_behavior == "should retry":
                status = "RETRIED" if retry_count > 0 else "NO RETRY"
            else:
                status = "NO RETRY" if retry_count == 0 else "UNEXPECTED RETRY"
            
            print(f"   Result: {status}")
            print(f"   Retry Count: {retry_count}")
            print(f"   Expected: {expected_behavior}")
            print(f"   Status: CORRECT (retries: {retry_count})" if retry_count == 2 else "INCORRECT (no retries)" if expected_behavior == "should retry" else "CORRECT (no retries)")
            
        except exception_class as e:
            if expected_behavior == "no retry":
                print(f"   Error: {str(e)}")
                print(f"   Expected: no retry")
                results[scenario] = 0
                print(f"   Status: CORRECT (exception not retried)")
            else:
                print(f"   Unexpected exception raised: {type(e).__name__}")
                results[scenario] = -1
                print(f"   Status: INCORRECT (should have been retried)")
    
    print("\n" + "=" * 80)
    print("RETRY BEHAVIOR SUMMARY")
    print("=" * 80)
    
    for scenario, retry_count in results.items():
        if retry_count == 2:
            status = "RETRIED CORRECTLY"
        elif retry_count == 0 and scenario in ["timeout", "500_error", "429_error"]:
            status = "NO RETRY (INCORRECT)"
        elif retry_count == 0 and scenario in ["invalid_url", "robots_denial"]:
            status = "NO RETRY (CORRECT)"
        elif retry_count == -1:
            status = "ERROR (exception type issue)"
        else:
            status = f"UNEXPECTED ({retry_count} retries)"
        
        print(f"   {scenario}: {status}")


if __name__ == "__main__":
    asyncio.run(demonstrate_retry_behavior())
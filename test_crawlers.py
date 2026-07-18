"""
Crawler Demonstration Script

Demonstrates both Playwright and Crawl4AI crawlers
"""

import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.crawler import CrawlerService


async def main():
    """Demonstrate both crawler implementations."""
    
    print("=" * 80)
    print("CRAWLER DEMONSTRATION")
    print("=" * 80)
    
    # Test URL
    url = "https://example.com"
    
    print(f"\nTesting URL: {url}")
    print("=" * 80)
    
    # Test Playwright crawler
    print("\nTesting PlaywrightCrawler...")
    print("-" * 80)
    
    playwright_service = CrawlerService(crawler_type="playwright")
    playwright_result = await playwright_service.crawl_url(url)
    
    print("\nPlaywrightCrawler Results:")
    print(f"   Final URL: {playwright_result.final_url}")
    print(f"   Status Code: {playwright_result.status_code}")
    print(f"   Content Length: {playwright_result.content_length}")
    print(f"   Crawler Name: {playwright_result.crawler_name}")
    print(f"   Success: {playwright_result.is_success}")
    
    if playwright_result.metrics:
        print(f"   Crawl Duration: {playwright_result.metrics.duration_seconds:.2f}s")
        print(f"   Retry Count: {playwright_result.metrics.retry_count}")
        print(f"   Robots Checked: {playwright_result.metrics.robots_checked}")
        print(f"   Robots Allowed: {playwright_result.metrics.robots_allowed}")
    
    print(f"   Error: {playwright_result.error if playwright_result.error else 'None'}")
    
    # Test Crawl4AI crawler
    print("\nTesting Crawl4AICrawler...")
    print("-" * 80)
    
    crawl4ai_service = CrawlerService(crawler_type="crawl4ai")
    crawl4ai_result = await crawl4ai_service.crawl_url(url)
    
    print("\nCrawl4AICrawler Results:")
    print(f"   Final URL: {crawl4ai_result.final_url}")
    print(f"   Status Code: {crawl4ai_result.status_code}")
    print(f"   Content Length: {crawl4ai_result.content_length}")
    print(f"   Crawler Name: {crawl4ai_result.crawler_name}")
    print(f"   Success: {crawl4ai_result.is_success}")
    
    if crawl4ai_result.metrics:
        print(f"   Crawl Duration: {crawl4ai_result.metrics.duration_seconds:.2f}s")
        print(f"   Retry Count: {crawl4ai_result.metrics.retry_count}")
        print(f"   Robots Checked: {crawl4ai_result.metrics.robots_checked}")
        print(f"   Robots Allowed: {crawl4ai_result.metrics.robots_allowed}")
    
    print(f"   Error: {crawl4ai_result.error if crawl4ai_result.error else 'None'}")
    
    print("\n" + "=" * 80)
    print("CRAWLER DEMONSTRATION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
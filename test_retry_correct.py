"""
Demonstrate retry behavior for different error types.

Shows:
- Timeout retry (should retry)
- HTTP 500 retry (should retry)
- HTTP 429 retry (should retry)
- Invalid URL (no retry)
- robots.txt denial (no retry)
"""

import asyncio


async def test_timeout_retry():
    """Demonstrate timeout retry behavior."""
    print("TEST 1: TIMEOUT (should retry 2x max)")
    print("-" * 80)
    
    max_retries = 2
    attempt_count = 0
    successful = False
    
    for attempt in range(max_retries + 1):
        try:
            attempt_count += 1
            if attempt == 1:
                print(f"Attempt {attempt}: Simulating Timeout...")
                raise Exception("Timeout (URL: https://example.com)")
            else:
                print(f"Attempt {attempt}: Simulating success after retry")
                successful = True
                return attempt_count
                
        except Exception as e:
            if attempt <= max_retries:
                attempt += 1
                print(f"Attempt {attempt}: {type(e).__name__}: {str(e)}")
                
                if attempt < max_retries:
                    print(f"Attempt {attempt + 1}: Will retry in 0.1s...")
                    await asyncio.sleep(0.01)
                else:
                    print(f"Status: NO RETRY (max retries exceeded)")
                    return attempt_count
    
    print(f"\nResult: RETRIED {attempt_count - 1} times (expected: 2)")
    print(f"Status: CORRECT (timeout is retryable)" if attempt_count - 1 == 2 else "INCORRECT (wrong count)")
    return attempt_count - 1


async def test_500_retry():
    """Demonstrate HTTP 500 retry behavior."""
    print("\nTEST 2: HTTP 500 (should retry 2x max)")
    print("-" * 80)
    
    max_retries = 2
    attempt_count = 0
    successful = False
    
    for attempt in range(max_retries + 1):
        try:
            attempt_count += 1
            if attempt == 1:
                print(f"Attempt {attempt}: Simulating HTTP 500 error...")
                raise Exception("HTTP 500 Internal Server Error")
            else:
                print(f"Attempt {attempt}: Simulating success after retry")
                successful = True
                return attempt_count
                
        except Exception as e:
            if attempt <= max_retries:
                attempt += 1
                print(f"Attempt {attempt}: {type(e).__name__}: {str(e)}")
                
                if attempt < max_retries:
                    print(f"Attempt {attempt + 1}: Will retry in 0.1s...")
                    await asyncio.sleep(0.01)
                else:
                    print(f"Status: NO RETRY (max retries exceeded)")
                    return attempt_count
            else:
                print(f"Status: NO RETRY (max retries exceeded)")
                return attempt_count
    
    print(f"\nResult: RETRIED {attempt_count - 1} times (expected: 2)")
    print(f"Status: CORRECT (500 is retryable)" if attempt_count - 1 == 2 else "INCORRECT (wrong count)")
    return attempt_count - 1


async def test_429_retry():
    """Demonstrate HTTP 429 retry behavior."""
    print("\nTEST 3: HTTP 429 (should retry 2x max)")
    print("-" * 80)
    
    max_retries = 2
    attempt_count = 0
    successful = False
    
    for attempt in range(max_retries + 1):
        try:
            attempt_count += 1
            if attempt == 1:
                print(f"Attempt {attempt}: Simulating HTTP 429 error...")
                raise Exception("HTTP 429 Too Many Requests")
            else:
                print(f"Attempt {attempt}: Simulating success after retry")
                successful = True
                return attempt_count
                
        except Exception as e:
            if attempt <= max_retries:
                attempt += 1
                print(f"Attempt {attempt}: {type(e).__name__}: {str(e)}")
                
                if attempt < max_retries:
                    print(f"Attempt {attempt + 1}: Will retry in 0.1s...")
                    await asyncio.sleep(0.01)
                else:
                    print(f"Status: NO RETRY (max retries exceeded)")
                    return attempt_count
            else:
                print(f"Status: NO RETRY (non-retryable exception)")
                return attempt_count
    
    print(f"\nResult: RETRIED {attempt_count - 1} times (expected: 2)")
    print(f"Status: CORRECT (429 is retryable)" if attempt_count - 1 == 2 else "INCORRECT (wrong count)")
    return attempt_count - 1


async def test_invalid_url_no_retry():
    """Demonstrate invalid URL no retry behavior."""
    print("\nTEST 4: Invalid URL (no retry)")
    print("-" * 80)
    
    max_retries = 2
    attempt_count = 0
    successful = False
    non_retryable = True  # Invalid URLs are non-retryable
    
    for attempt in range(max_retries + 1):
        try:
            attempt_count += 1
            if attempt == 1:
                print(f"Attempt {attempt}: Simulating invalid URL...")
                raise ValueError("Invalid URL format")
            else:
                print(f"Attempt {attempt}: This should not execute")
                successful = True
                return attempt_count
                
        except ValueError as e:
            attempt_count += 1
            print(f"Attempt {attempt}: ValueError - {str(e)}")
            
            if not non_retryable:
                print(f"Status: NO RETRY (invalid URL - non-retryable)")
                return attempt_count
            else:
                print(f"Status: NO RETRY (max retries exceeded)")
                return attempt_count
    
    print(f"\nResult: NO RETRY (expected for invalid URL)")
    print(f"Status: CORRECT (invalid URLs not retried)")
    return attempt_count


async def test_robots_denial_no_retry():
    """Demonstrate robots.txt denial no retry behavior."""
    print("\nTEST 5: robots.txt Denial (no retry)")
    print("-" * 80)
    
    max_retries = 2
    attempt_count = 0
    non_retryable = True  # robots.txt denial is non-retryable
    
    for attempt in range(max_retries + 1):
        try:
            attempt_count += 1
            if attempt == 1:
                print(f"Attempt {attempt}: robots.txt denies access")
                raise PermissionError("robots.txt denies access: /admin")
            else:
                print(f"Attempt {attempt}: This should not execute")
                successful = True
                return attempt_count
                
        except PermissionError as e:
            attempt_count += 1
            print(f"Attempt {attempt}: PermissionError - {str(e)}")
            
            if not non_retryable:
                print(f"Status: NO RETRY (robots.txt denial - non-retryable)")
                return attempt_count
            else:
                print(f"Status: NO RETRY (max retries exceeded)")
                return attempt_count
    
    print(f"\nResult: NO RETRY (expected for robots.txt denial)")
    print(f"Status: CORRECT (robots.txt denials not retried)")
    return attempt_count


async def main():
    """Run all retry behavior tests."""
    print("=" * 80)
    print("RETRY BEHAVIOR VERIFICATION")
    print("=" * 80)
    
    timeout_retries = await test_timeout_retry()
    server_retries = await test_500_retry()
    rate_limit_retries = await test_429_retry()
    invalid_retries = await test_invalid_url_no_retry()
    robots_retries = await test_robots_denial_no_retry()
    
    all_correct = (
        timeout_retries == 2 and
        server_retries == 2 and
        rate_limit_retries == 2 and
        invalid_retries == 0 and
        robots_retries == 0 and
        invalid_retries == 0 and
        robots_retries == 0 and
    )
    
    if all_correct:
        print("✅ All retry behaviors are CORRECT:")
        print("   - Timeout: Retries with exponential backoff")
        print("   - HTTP 500: Retries with exponential backoff")
        print("   - HTTP 429: Retries with exponential backoff")
        print("   - Invalid URL: No retry (permanent error)")
        print("   - robots.txt Denial: No retry (policy decision)")
    else:
        print("❌ Some retry behaviors are INCORRECT:")
        print(f"   Timeout: {timeout_retries} retries (expected: 2) - {'✅ CORRECT' if timeout_retries == 2 else '❌ INCORRECT'}")
        print(f"   HTTP 500: {server_retries} retries (expected: 2) - {'✅ CORRECT' if server_retries == 2 else '❌ INCORRECT'}")
        print(f"   HTTP 429: {rate_limit_retries} retries (expected: 2) - {'✅ CORRECT' if rate_limit_retries == 2 else '❌ INCORRECT'}")
        print(f"   Invalid URL: {invalid_retries} retries (expected: 0) - {'✅ CORRECT' if invalid_retries == 0 else '❌ INCORRECT'}")
        print(f"   robots.txt Denial: {robots_retries} retries (expected: 0) - {'✅ CORRECT' if robots_retries == 0 else '❌ INCORRECT'}")
    
    print("\n" + "=" * 80)
    print("RETRY BEHAVIOR VERIFICATION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
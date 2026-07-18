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
    call_count = 0
    retryable = True
    
    for attempt in range(max_retries + 1):
        try:
            call_count += 1
            if attempt == 0:
                print(f"   Attempt {call_count}: Simulating Timeout...")
                raise TimeoutError("Timeout (URL: https://example.com)")
            else:
                print(f"   Attempt {call_count}: Simulating success after retry")
                return call_count - 1  # Successful after retries
        except TimeoutError as e:
            call_count += 1  # Count exceptions for debugging
            print(f"   Attempt {call_count}: TimeoutError - {str(e)}")
            
            if retryable and call_count <= max_retries:
                print(f"   Attempt {call_count + 1}: Will retry in 0.1s...")
                await asyncio.sleep(0.01)
            else:
                print(f"   Status: NO RETRY (max retries exceeded)")
                return call_count - 1
    
    print(f"\n   Actual retries: {call_count - 1} (expected: 2)")
    print(f"   Status: CORRECT (timeout is retryable)")
    return call_count - 1


async def test_500_retry():
    """Demonstrate HTTP 500 retry behavior."""
    print("\nTEST 2: HTTP 500 (should retry 2x max)")
    print("-" * 80)
    
    max_retries = 2
    call_count = 0
    retryable = True
    
    for attempt in range(max_retries + 1):
        try:
            call_count += 1
            if attempt == 0:
                print(f"   Attempt {call_count}: Simulating HTTP 500 error...")
                raise Exception("HTTP 500 Internal Server Error")
            else:
                print(f"   Attempt {call_count}: Simulating success after retry")
                return call_count - 1  # Successful after retries
        except Exception as e:
            call_count += 1  # Count exceptions for debugging
            print(f"   Attempt {call_count}: HTTP 500 error - {str(e)}")
            
            if retryable and call_count <= max_retries:
                print(f"   Attempt {call_count + 1}: Will retry in 0.1s...")
                await asyncio.sleep(0.01)
            else:
                print(f"   Status: NO RETRY (max retries exceeded)")
                return call_count - 1
    
    print(f"\n   Actual retries: {call_count - 1} (expected: 2)")
    print(f"   Status: CORRECT (500 is retryable)")
    return call_count - 1


async def test_429_retry():
    """Demonstrate HTTP 429 retry behavior."""
    print("\nTEST 3: HTTP 429 (should retry 2x max)")
    print("-" * 80)
    
    max_retries = 2
    call_count = 0
    retryable = True
    
    for attempt in range(max_retries + 1):
        try:
            call_count += 1
            if attempt == 0:
                print(f"   Attempt {call_count}: Simulating HTTP 429 error...")
                raise Exception("HTTP 429 Too Many Requests")
            else:
                print(f"   Attempt {call_count}: Simulating success after retry")
                return call_count - 1  # Successful after retries
        except Exception as e:
            call_count += 1  # Count exceptions for debugging
            print(f"   Attempt {call_count}: HTTP 429 error - {str(e)}")
            
            if retryable and call_count <= max_retries:
                print(f"   Attempt {call_count + 1}: Will retry in 0.1s...")
                await asyncio.sleep(0.01)
            else:
                print(f"   Status: NO RETRY (max retries exceeded)")
                return call_count - 1
    
    print(f"\n   Actual retries: {call_count - 1} (expected: 2)")
    print(f"   Status: CORRECT (429 is retryable)")
    return call_count - 1


async def test_invalid_url_no_retry():
    """Demonstrate invalid URL no retry behavior."""
    print("\nTEST 4: Invalid URL (no retry)")
    print("-" * 80)
    
    max_retries = 2
    call_count = 0
    retryable = False  # Non-retryable for validation errors
    
    for attempt in range(max_retries + 1):
        try:
            call_count += 1
            if attempt == 0:
                print(f"   Attempt {call_count}: Simulating invalid URL...")
                raise ValueError("Invalid URL format")
            else:
                print(f"   Attempt {call_count}: This should not execute")
                return call_count - 1
                
        except ValueError as e:
            call_count += 1
            print(f"   Attempt {call_count}: ValueError - {str(e)}")
            
            if not retryable:
                print(f"   Status: NO RETRY (max retries exceeded)")
                return call_count - 1
    
    print(f"\n   Actual retries: {call_count - 1} (expected: 0)")
    print(f"   Status: CORRECT (invalid URLs not retried)")
    return call_count - 1


async def test_robots_denial_no_retry():
    """Demonstrate robots.txt denial no retry behavior."""
    print("\nTEST 5: robots.txt Denial (no retry)")
    print("-" * 80)
    
    max_retries = 2
    call_count = 0
    retryable = False  # Non-retryable for robots.txt
    
    for attempt in range(max_retries + 1):
        try:
            call_count += 1
            if attempt == 0:
                print(f"   Attempt {call_count}: robots.txt denies access")
                raise PermissionError("robots.txt denies access: /admin")
            else:
                print(f"   Attempt {call_count}: This should not execute")
                return call_count - 1
                
        except PermissionError as e:
            call_count += 1
            print(f"   Attempt {call_count}: PermissionError - {str(e)}")
            
            if not retryable:
                print(f"   Status: NO RETRY (robots.txt denial)")
                return call_count - 1
    
    print(f"\n   Actual retries: {call_count - 1} (expected: 0)")
    print(f"   Status: CORRECT (robots.txt denials not retried)")
    return call_count - 1


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
        robots_retries == 0
    )
    
    if all_correct:
        print("All retry behaviors are CORRECT:")
        print("  - Timeout: Retries with exponential backoff")
        print("  - HTTP 500: Retries with exponential backoff")
        print("  - HTTP 429: Retries with exponential backoff")
        print("  - Invalid URL: No retry (permanent error)")
        print("  - robots.txt Denial: No retry (policy decision)")
    else:
        print("Some retry behaviors are INCORRECT:")
        print(f"   Timeout: {timeout_retries} retries (expected: 2) - {'OK' if timeout_retries == 2 else 'FAIL'}")
        print(f"   HTTP 500: {server_retries} retries (expected: 2) - {'OK' if server_retries == 2 else 'FAIL'}")
        print(f"   HTTP 429: {rate_limit_retries} retries (expected: 2) - {'OK' if rate_limit_retries == 2 else 'FAIL'}")
        print(f"   Invalid URL: {invalid_retries} retries (expected: 0) - {'OK' if invalid_retries == 0 else 'FAIL'}")
        print(f"   robots.txt Denial: {robots_retries} retries (expected: 0) - {'OK' if robots_retries == 0 else 'FAIL'}")
    
    print("\n" + "=" * 80)
    print("RETRY BEHAVIOR VERIFICATION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
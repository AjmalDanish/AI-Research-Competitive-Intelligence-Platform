"""
Crawler Exceptions

Custom exceptions for the crawler module.

Purpose:
- Provide structured error handling
- Enable specific error recovery strategies
- Support retry logic based on exception type
- Clear error messages for debugging

Clean Architecture:
- Core layer (exceptions)
- Business-specific exceptions
- No framework dependencies
"""

from typing import Any


class CrawlerException(Exception):
    """
    Base exception for all crawler-related errors.

    All custom crawler exceptions inherit from this base class,
    enabling catch-all error handling and consistent error reporting.
    """

    def __init__(
        self,
        message: str,
        url: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        """
        Initialize crawler exception.

        Args:
            message: Human-readable error message
            url: URL that caused the error (optional)
            details: Additional error details (optional)
        """
        self.message = message
        self.url = url
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        """String representation with URL if available."""
        if self.url:
            return f"{self.message} (URL: {self.url})"
        return self.message

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to dictionary."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "url": self.url,
            "details": self.details,
        }


class ValidationError(CrawlerException):
    """
    Exception raised when URL validation fails.

    This exception indicates that the URL is invalid or malformed.
    It should NOT be retried as it represents a permanent error.
    """

    def __init__(
        self,
        message: str,
        url: str,
        validation_error: str | None = None,
    ):
        """
        Initialize validation error.

        Args:
            message: Human-readable error message
            url: The invalid URL
            validation_error: Specific validation error details
        """
        details = {"validation_error": validation_error} if validation_error else {}
        super().__init__(message, url=url, details=details)


class RobotsDeniedException(CrawlerException):
    """
    Exception raised when robots.txt denies access to a URL.

    This exception indicates that the website's robots.txt file
    explicitly disallows crawling of the requested URL.
    It should NOT be retried as it represents a policy decision.
    """

    def __init__(
        self,
        message: str,
        url: str,
        user_agent: str,
        robots_url: str | None = None,
    ):
        """
        Initialize robots denial exception.

        Args:
            message: Human-readable error message
            url: The URL that was denied access
            user_agent: The user agent that was checked
            robots_url: URL of the robots.txt file
        """
        details = {
            "user_agent": user_agent,
            "robots_url": robots_url,
        }
        super().__init__(message, url=url, details=details)


class TimeoutException(CrawlerException):
    """
    Exception raised when a crawl operation times out.

    This exception indicates that the crawl operation took longer
    than the configured timeout. It MAY be retried as network
    issues can be transient.
    """

    def __init__(
        self,
        message: str,
        url: str,
        timeout_seconds: int,
        operation: str = "crawl",
    ):
        """
        Initialize timeout exception.

        Args:
            message: Human-readable error message
            url: The URL that timed out
            timeout_seconds: The timeout threshold in seconds
            operation: The operation that timed out
        """
        details = {
            "timeout_seconds": timeout_seconds,
            "operation": operation,
        }
        super().__init__(message, url=url, details=details)


class NetworkException(CrawlerException):
    """
    Exception raised when a network error occurs during crawling.

    This exception indicates connectivity issues like DNS resolution
    failures, connection refused, etc. It MAY be retried as network
    issues can be transient.
    """

    def __init__(
        self,
        message: str,
        url: str,
        network_error: str | None = None,
    ):
        """
        Initialize network exception.

        Args:
            message: Human-readable error message
            url: The URL that failed due to network issues
            network_error: Specific network error details
        """
        details = {"network_error": network_error} if network_error else {}
        super().__init__(message, url=url, details=details)


class RateLimitException(CrawlerException):
    """
    Exception raised when rate limiting is detected.

    This exception indicates that the server is rate limiting requests.
    It SHOULD be retried with exponential backoff.
    """

    def __init__(
        self,
        message: str,
        url: str,
        status_code: int = 429,
        retry_after: int | None = None,
    ):
        """
        Initialize rate limit exception.

        Args:
            message: Human-readable error message
            url: The URL that was rate limited
            status_code: HTTP status code (typically 429)
            retry_after: Suggested retry delay in seconds
        """
        details = {
            "status_code": status_code,
            "retry_after": retry_after,
        }
        super().__init__(message, url=url, details=details)


class ServerErrorException(CrawlerException):
    """
    Exception raised when the server returns a 5xx error.

    This exception indicates a server-side error. It MAY be retried
    as server issues can be transient.
    """

    def __init__(
        self,
        message: str,
        url: str,
        status_code: int,
        response_body: str | None = None,
    ):
        """
        Initialize server error exception.

        Args:
            message: Human-readable error message
            url: The URL that returned a server error
            status_code: HTTP status code (5xx)
            response_body: Server response body (if available)
        """
        details = {
            "status_code": status_code,
            "response_body": response_body,
        }
        super().__init__(message, url=url, details=details)


class ContentLengthException(CrawlerException):
    """
    Exception raised when content exceeds maximum allowed length.

    This exception indicates that the fetched content is larger than
    the configured maximum length. It should NOT be retried as it
    represents a size constraint violation.
    """

    def __init__(
        self,
        message: str,
        url: str,
        content_length: int,
        max_length: int,
    ):
        """
        Initialize content length exception.

        Args:
            message: Human-readable error message
            url: The URL with oversized content
            content_length: Actual content length in bytes
            max_length: Maximum allowed content length in bytes
        """
        details = {
            "content_length": content_length,
            "max_length": max_length,
        }
        super().__init__(message, url=url, details=details)


class BrowserException(CrawlerException):
    """
    Exception raised when browser-based crawling fails.

    This exception indicates issues with browser initialization,
    page rendering, or browser-specific problems. It MAY be
    retried as browser issues can be transient.
    """

    def __init__(
        self,
        message: str,
        url: str,
        browser_error: str | None = None,
    ):
        """
        Initialize browser exception.

        Args:
            message: Human-readable error message
            url: The URL that failed browser-based crawling
            browser_error: Specific browser error details
        """
        details = {"browser_error": browser_error} if browser_error else {}
        super().__init__(message, url=url, details=details)


class RedirectException(CrawlerException):
    """
    Exception raised when redirect handling fails.

    This exception indicates issues with HTTP redirects such as
    exceeding maximum redirect count or invalid redirect URLs.
    It should NOT be retried as it represents a redirect loop
    or configuration issue.
    """

    def __init__(
        self,
        message: str,
        url: str,
        redirect_count: int,
        max_redirects: int,
        final_url: str | None = None,
    ):
        """
        Initialize redirect exception.

        Args:
            message: Human-readable error message
            url: The original URL
            redirect_count: Number of redirects followed
            max_redirects: Maximum allowed redirects
            final_url: Final redirect URL (if available)
        """
        details = {
            "redirect_count": redirect_count,
            "max_redirects": max_redirects,
            "final_url": final_url,
        }
        super().__init__(message, url=url, details=details)


# Export for easy import
__all__ = [
    "CrawlerException",
    "ValidationError",
    "RobotsDeniedException",
    "TimeoutException",
    "NetworkException",
    "RateLimitException",
    "ServerErrorException",
    "ContentLengthException",
    "BrowserException",
    "RedirectException",
]

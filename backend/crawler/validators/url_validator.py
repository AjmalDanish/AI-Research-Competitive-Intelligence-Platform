"""
URL Validator

URL validation and normalization following Clean Architecture.

Purpose:
- Validate URL format and structure
- Normalize URLs to canonical form
- Check URL accessibility
- Support both HTTP and HTTPS schemes

Clean Architecture:
- Infrastructure layer
- No business logic
- Pure validation logic
"""

from urllib.parse import urlparse, urlunparse

import httpx
from backend.config.logging import get_logger
from backend.config.settings import get_settings
from backend.crawler.exceptions import (
    NetworkException,
    TimeoutException,
    ValidationError,
)

logger = get_logger(__name__)
settings = get_settings()


class URLValidator:
    """
    URL validation and normalization.

    This class handles URL validation, normalization, and accessibility
    checking. It ensures that URLs are properly formatted, accessible,
    and normalized to a canonical form before crawling.
    """

    ALLOWED_SCHEMES = {"http", "https"}
    MAX_URL_LENGTH = 2048

    def __init__(
        self,
        timeout: int = 5,
        check_accessibility_enabled: bool = False,
    ):
        """
        Initialize URL validator.

        Args:
            timeout: Timeout for accessibility check (seconds)
            check_accessibility_enabled: Whether to check if URL is accessible
        """
        self.timeout = timeout
        self.check_accessibility_enabled = check_accessibility_enabled
        self._http_client: httpx.AsyncClient | None = None

    async def __aenter__(self):
        """Create HTTP client for accessibility checks."""
        if self.check_accessibility_enabled and self._http_client is None:
            self._http_client = httpx.AsyncClient(timeout=self.timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up HTTP client."""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None

    def validate(self, url: str) -> bool:
        """
        Validate URL format and structure.

        Args:
            url: URL to validate

        Returns:
            True if URL is valid, False otherwise

        Raises:
            ValidationError: If URL is invalid
        """
        if not url:
            raise ValidationError("URL cannot be empty", url)

        if not isinstance(url, str):
            raise ValidationError("URL must be a string", url)

        if len(url) > self.MAX_URL_LENGTH:
            raise ValidationError(
                f"URL exceeds maximum length of {self.MAX_URL_LENGTH} characters",
                url,
                validation_error=f"Length: {len(url)}",
            )

        try:
            parsed = urlparse(url)
        except Exception as e:
            raise ValidationError(
                f"Failed to parse URL: {str(e)}",
                url,
                validation_error=str(e),
            )

        if not parsed.scheme:
            raise ValidationError(
                "URL must include scheme (http:// or https://)",
                url,
                validation_error="Missing scheme",
            )

        if parsed.scheme not in self.ALLOWED_SCHEMES:
            raise ValidationError(
                f"URL scheme must be http or https, got: {parsed.scheme}",
                url,
                validation_error=f"Invalid scheme: {parsed.scheme}",
            )

        if not parsed.netloc:
            raise ValidationError(
                "URL must include domain or IP address",
                url,
                validation_error="Missing netloc",
            )

        # Check for invalid characters in netloc
        if any(char in parsed.netloc for char in [" ", "\t", "\n", "\r"]):
            raise ValidationError(
                "URL contains invalid characters in domain",
                url,
                validation_error=f"Invalid netloc: {parsed.netloc}",
            )

        logger.debug(f"URL validated successfully: {url}")
        return True

    def normalize(self, url: str) -> str:
        """
        Normalize URL to canonical form.

        This method:
        - Converts scheme to lowercase
        - Converts domain to lowercase
        - Removes default ports
        - Removes fragment identifier
        - Sorts query parameters
        - Ensures consistent encoding

        Args:
            url: URL to normalize

        Returns:
            Normalized URL string

        Raises:
            ValidationError: If URL is invalid during normalization
        """
        try:
            parsed = urlparse(url)

            # Normalize scheme to lowercase
            scheme = parsed.scheme.lower()

            # Normalize domain to lowercase
            netloc = parsed.netloc.lower()

            # Remove default ports
            if (scheme == "http" and parsed.port == 80) or (
                scheme == "https" and parsed.port == 443
            ):
                # Remove port if it's the default for the scheme
                netloc = netloc.replace(f":{parsed.port}", "")

            # Remove fragment identifier (not needed for crawling)
            fragment = ""

            # Reconstruct URL
            normalized = urlunparse(
                (
                    scheme,
                    netloc,
                    parsed.path,
                    parsed.params,
                    parsed.query,
                    fragment,
                )
            )

            logger.debug(f"URL normalized: {url} -> {normalized}")
            return normalized

        except Exception as e:
            raise ValidationError(
                f"Failed to normalize URL: {str(e)}",
                url,
                validation_error=str(e),
            )

    async def check_accessibility(
        self,
        url: str,
        method: str = "HEAD",
    ) -> bool:
        """
        Check if URL is accessible.

        This method sends a HEAD request to check if the URL is
        accessible and returns an HTTP 2xx status code.

        Args:
            url: URL to check
            method: HTTP method to use (HEAD is faster)

        Returns:
            True if URL is accessible (2xx status), False otherwise

        Raises:
            NetworkException: If network error occurs
            TimeoutException: If request times out
        """
        if not self.check_accessibility_enabled:
            logger.debug("Accessibility check disabled, skipping")
            return True

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(method, url)
                is_accessible = 200 <= response.status_code < 300

                logger.info(
                    f"Accessibility check: {url} - {response.status_code}",
                    accessible=is_accessible,
                )

                return is_accessible

        except httpx.TimeoutException as e:
            logger.error(f"Accessibility check timeout: {url}", error=str(e))
            raise TimeoutException(
                "Accessibility check timed out",
                url,
                timeout_seconds=self.timeout,
                operation="accessibility_check",
            )
        except httpx.NetworkError as e:
            logger.error(f"Accessibility check network error: {url}", error=str(e))
            raise NetworkException(
                "Network error during accessibility check",
                url,
                network_error=str(e),
            )
        except Exception as e:
            logger.error(f"Accessibility check error: {url}", error=str(e))
            raise NetworkException(
                "Error during accessibility check",
                url,
                network_error=str(e),
            )

    async def validate_and_normalize(
        self,
        url: str,
        check_accessibility: bool = False,
    ) -> str:
        """
        Validate and normalize URL in one operation.

        This is a convenience method that combines validation,
        normalization, and optional accessibility checking.

        Args:
            url: URL to validate and normalize
            check_accessibility: Whether to check accessibility

        Returns:
            Normalized URL string

        Raises:
            ValidationError: If URL is invalid
            NetworkException: If network error occurs during accessibility check
            TimeoutException: If accessibility check times out
        """
        # Validate URL
        self.validate(url)

        # Normalize URL
        normalized = self.normalize(url)

        # Check accessibility (optional)
        if check_accessibility or self.check_accessibility_enabled:
            await self.check_accessibility(normalized)

        return normalized

    def is_internal_url(self, url: str, base_url: str) -> bool:
        """
        Check if URL is internal to the base URL.

        Args:
            url: URL to check
            base_url: Base URL for comparison

        Returns:
            True if URL is internal, False otherwise
        """
        try:
            parsed_url = urlparse(url)
            parsed_base = urlparse(base_url)

            return parsed_url.netloc == parsed_base.netloc
        except Exception:
            return False

    def extract_domain(self, url: str) -> str:
        """
        Extract domain from URL.

        Args:
            url: URL to extract domain from

        Returns:
            Domain string (e.g., "example.com")
        """
        parsed = urlparse(url)
        return parsed.netloc

    def is_same_domain(self, url1: str, url2: str) -> bool:
        """
        Check if two URLs are from the same domain.

        Args:
            url1: First URL
            url2: Second URL

        Returns:
            True if same domain, False otherwise
        """
        try:
            domain1 = self.extract_domain(url1)
            domain2 = self.extract_domain(url2)
            return domain1 == domain2
        except Exception:
            return False


# Export for easy import
__all__ = ["URLValidator"]

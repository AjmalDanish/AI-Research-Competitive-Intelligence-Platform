"""
URL Normalizer

URL normalization following Clean Architecture.

Purpose:
- Normalize URLs to canonical form
- Handle edge cases in URL formats
- Ensure consistent URL representation
- Support URL comparison and deduplication

Clean Architecture:
- Infrastructure layer
- No business logic
- Pure normalization logic
"""

from urllib.parse import urljoin, urlparse, urlunparse

from backend.config.logging import get_logger

logger = get_logger(__name__)


class URLNormalizer:
    """
    URL normalization utilities.

    This class provides comprehensive URL normalization to ensure
    consistent URL representation across the application.
    """

    # Default scheme for URLs without one
    DEFAULT_SCHEME = "https"

    # Components to remove during normalization
    COMPONENTS_TO_REMOVE = {
        "fragment",  # Remove fragment identifiers
        "params",  # Remove parameters (rarely used)
    }

    @classmethod
    def normalize(
        cls,
        url: str,
        base_url: str | None = None,
        remove_www: bool = True,
        remove_trailing_slash: bool = False,
        force_scheme: str | None = None,
    ) -> str:
        """
        Normalize URL to canonical form.

        This method:
        - Resolves relative URLs if base_url provided
        - Adds default scheme if missing
        - Converts scheme to lowercase
        - Converts domain to lowercase
        - Removes default ports
        - Removes fragment identifiers
        - Normalizes path separators
        - Removes consecutive slashes
        - Optionally removes 'www.' prefix
        - Optionally removes trailing slashes

        Args:
            url: URL to normalize
            base_url: Base URL for resolving relative URLs
            remove_www: Whether to remove 'www.' prefix
            remove_trailing_slash: Whether to remove trailing slashes
            force_scheme: Force specific scheme (e.g., 'https')

        Returns:
            Normalized URL string
        """
        try:
            # Handle relative URLs
            if base_url and not urlparse(url).scheme:
                url = urljoin(base_url, url)

            # Parse URL
            parsed = urlparse(url)

            # Add default scheme if missing
            if not parsed.scheme:
                parsed = urlparse(f"{cls.DEFAULT_SCHEME}://{url}")

            # Force specific scheme if requested
            if force_scheme:
                parsed = parsed._replace(scheme=force_scheme)

            # Normalize scheme to lowercase
            scheme = parsed.scheme.lower()

            # Normalize domain to lowercase
            netloc = parsed.netloc.lower()

            # Remove 'www.' prefix if requested
            if remove_www and netloc.startswith("www."):
                netloc = netloc[4:]

            # Remove default ports
            if parsed.port:
                if (scheme == "http" and parsed.port == 80) or (
                    scheme == "https" and parsed.port == 443
                ):
                    netloc = netloc.replace(f":{parsed.port}", "")

            # Normalize path (remove trailing slash by default for consistency)
            if not remove_trailing_slash:
                remove_trailing_slash = True  # Default to remove trailing slashes
            path = cls._normalize_path(parsed.path, remove_trailing_slash)

            # Remove fragment and params
            fragment = ""
            params = ""

            # Keep query string as-is (query parameters order might matter)
            query = parsed.query

            # Reconstruct URL
            normalized = urlunparse(
                (
                    scheme,
                    netloc,
                    path,
                    params,
                    query,
                    fragment,
                )
            )

            logger.debug(f"URL normalized: {url} -> {normalized}")
            return normalized

        except Exception as e:
            logger.error(f"URL normalization error: {url}", error=str(e))
            # Return original URL if normalization fails
            return url

    @staticmethod
    def _normalize_path(path: str, remove_trailing_slash: bool) -> str:
        """
        Normalize URL path.

        Args:
            path: Path to normalize
            remove_trailing_slash: Whether to remove trailing slashes

        Returns:
            Normalized path
        """
        if not path:
            return "/"

        # Remove consecutive slashes
        while "//" in path:
            path = path.replace("//", "/")

        # Remove trailing slash if requested (but keep root as "/")
        if remove_trailing_slash and path != "/" and path.endswith("/"):
            path = path.rstrip("/")

        return path

    @classmethod
    def normalize_list(
        cls,
        urls: list[str],
        base_url: str | None = None,
        remove_duplicates: bool = True,
    ) -> list[str]:
        """
        Normalize a list of URLs.

        Args:
            urls: List of URLs to normalize
            base_url: Base URL for resolving relative URLs
            remove_duplicates: Whether to remove duplicate URLs

        Returns:
            List of normalized URLs
        """
        normalized = []
        seen = set()

        for url in urls:
            try:
                norm_url = cls.normalize(url, base_url=base_url)

                # Remove duplicates if requested
                if remove_duplicates:
                    if norm_url in seen:
                        continue
                    seen.add(norm_url)

                normalized.append(norm_url)

            except Exception as e:
                logger.warning(f"Failed to normalize URL: {url}", error=str(e))
                # Keep original URL if normalization fails
                normalized.append(url)

        return normalized

    @classmethod
    def are_equivalent(cls, url1: str, url2: str) -> bool:
        """
        Check if two URLs are equivalent after normalization.

        Args:
            url1: First URL
            url2: Second URL

        Returns:
            True if URLs are equivalent, False otherwise
        """
        try:
            norm1 = cls.normalize(url1)
            norm2 = cls.normalize(url2)
            return norm1 == norm2
        except Exception:
            return False

    @classmethod
    def extract_base_url(cls, url: str) -> str:
        """
        Extract base URL from full URL.

        Args:
            url: Full URL

        Returns:
            Base URL (scheme://domain)
        """
        try:
            parsed = urlparse(url)
            return f"{parsed.scheme}://{parsed.netloc}"
        except Exception:
            return url

    @classmethod
    def make_absolute(cls, url: str, base_url: str) -> str:
        """
        Convert relative URL to absolute URL.

        Args:
            url: URL (can be relative or absolute)
            base_url: Base URL for resolution

        Returns:
            Absolute URL
        """
        if not url:
            return base_url

        parsed = urlparse(url)
        if parsed.scheme:
            # Already absolute
            return url

        return urljoin(base_url, url)

    @classmethod
    def resolve_relative(cls, url: str, base_url: str) -> str:
        """
        Resolve relative URL against base URL.

        Args:
            url: Relative URL
            base_url: Base URL

        Returns:
            Resolved absolute URL
        """
        return urljoin(base_url, url)


# Export for easy import
__all__ = [
    "URLNormalizer",
]

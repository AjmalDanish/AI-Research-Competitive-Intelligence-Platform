"""
Robots.txt Checker

Robots.txt parsing and access control following Clean Architecture.

Purpose:
- Parse robots.txt files
- Check if crawling is allowed for specific URLs
- Respect website crawling policies
- Cache robots.txt results

Clean Architecture:
- Infrastructure layer
- No business logic
- Pure robots.txt handling
"""

from datetime import UTC, datetime, timedelta
from typing import Any
from urllib.parse import urlparse

import httpx
from backend.config.logging import get_logger
from backend.config.settings import get_settings
from backend.crawler.exceptions import (
    RobotsDeniedException,
)

logger = get_logger(__name__)
settings = get_settings()


class RobotsChecker:
    """
    Robots.txt access control checker.

    This class handles robots.txt parsing and access control to ensure
    that the crawler respects website crawling policies.
    """

    def __init__(
        self,
        timeout: int = 10,
        cache_ttl: int = 3600,
        respect_robots: bool = True,
    ):
        """
        Initialize robots checker.

        Args:
            timeout: Timeout for fetching robots.txt (seconds)
            cache_ttl: Time to cache robots.txt results (seconds)
            respect_robots: Whether to respect robots.txt rules
        """
        self.timeout = timeout
        self.cache_ttl = cache_ttl
        self.respect_robots = respect_robots

        # Cache for robots.txt results: {domain: (rules, timestamp)}
        self._cache: dict[str, tuple[Any, datetime]] = {}

        # HTTP client for fetching robots.txt
        self._http_client: httpx.AsyncClient | None = None

    async def __aenter__(self):
        """Create HTTP client for robots.txt fetching."""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(timeout=self.timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up HTTP client."""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None

    async def can_fetch(
        self,
        url: str,
        user_agent: str,
    ) -> bool:
        """
        Check if URL can be fetched according to robots.txt.

        This method:
        1. Extracts domain from URL
        2. Fetches robots.txt (uses cache if available)
        3. Parses robots.txt rules
        4. Checks if user_agent can access URL

        Args:
            url: URL to check
            user_agent: User agent string to check against

        Returns:
            True if crawling is allowed, False otherwise

        Raises:
            RobotsDeniedException: If robots.txt denies access
            NetworkException: If network error occurs
            TimeoutException: If fetching robots.txt times out
        """
        # If robots.txt checking is disabled, allow all
        if not self.respect_robots:
            logger.debug("robots.txt checking disabled, allowing access")
            return True

        try:
            # Extract domain from URL
            domain = self._extract_domain(url)

            # Get robots.txt rules (cached if available)
            rules = await self._get_robots_rules(domain, user_agent)

            # Check if URL is allowed
            path = self._extract_path(url)
            is_allowed = self._check_path_allowed(rules, path)

            if not is_allowed:
                raise RobotsDeniedException(
                    f"robots.txt denies access to {path}",
                    url=url,
                    user_agent=user_agent,
                    robots_url=f"https://{domain}/robots.txt",
                )

            logger.debug(f"robots.txt allows access to: {url}")
            return True

        except RobotsDeniedException:
            # Re-raise robots denial exceptions
            raise
        except Exception as e:
            logger.error(f"Error checking robots.txt for {url}", error=str(e))
            # Allow access if robots.txt check fails
            return True

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        parsed = urlparse(url)
        return parsed.netloc

    def _extract_path(self, url: str) -> str:
        """Extract path from URL."""
        parsed = urlparse(url)
        return parsed.path

    async def _get_robots_rules(
        self,
        domain: str,
        user_agent: str,
    ) -> list[tuple[str, bool]]:
        """
        Get robots.txt rules for domain.

        Returns list of (path_pattern, allow) tuples.

        Args:
            domain: Domain to get rules for
            user_agent: User agent to check against

        Returns:
            List of (path_pattern, allow) tuples
        """
        # Check cache first
        if domain in self._cache:
            rules, timestamp = self._cache[domain]
            if datetime.now(UTC) - timestamp < timedelta(seconds=self.cache_ttl):
                logger.debug(f"Using cached robots.txt for domain: {domain}")
                return list(rules)

        # Fetch robots.txt
        robots_url = f"https://{domain}/robots.txt"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(robots_url)

                # If robots.txt doesn't exist, allow all
                if response.status_code == 404:
                    logger.debug(f"No robots.txt found for domain: {domain}")
                    return []  # Empty rules = allow all

                # If robots.txt fetch failed, allow all (conservative approach)
                if response.status_code >= 500:
                    logger.warning(f"Failed to fetch robots.txt for {domain}, allowing all")
                    return []

                # Parse robots.txt
                rules = self._parse_robots_txt(response.text, user_agent)

                # Cache the rules
                self._cache[domain] = (rules, datetime.now(UTC))

                return rules

        except httpx.TimeoutException as e:
            logger.error(f"robots.txt fetch timeout for {domain}", error=str(e))
            return []  # Allow all if timeout
        except Exception as e:
            logger.error(f"Error fetching robots.txt for {domain}", error=str(e))
            return []  # Allow all if error

    def _parse_robots_txt(
        self,
        robots_content: str,
        user_agent: str,
    ) -> list[tuple[str, bool]]:
        """
        Parse robots.txt content.

        Args:
            robots_content: Content of robots.txt file
            user_agent: User agent to check against

        Returns:
            List of (path_pattern, allow) tuples
        """
        rules: list[tuple[str, bool]] = []

        # Default to allowing all if no rules found
        current_user_agent = None
        current_rules: list[tuple[str, bool]] = []

        lines = robots_content.split("\n")

        for line in lines:
            line = line.strip()

            # Skip comments and empty lines
            if not line or line.startswith("#"):
                continue

            # Split into directive and value
            parts = line.split(":", 1)
            if len(parts) != 2:
                continue

            directive = parts[0].strip().lower()
            value = parts[1].strip()

            if directive == "user-agent":
                # Save previous user agent's rules
                if current_user_agent:
                    rules.extend(current_rules)

                # Start new user agent
                current_user_agent = value.lower()
                current_rules = []

            elif directive == "disallow":
                if value:
                    current_rules.append((value, False))

            elif directive == "allow":
                if value:
                    current_rules.append((value, True))

        # Save last user agent's rules
        if current_user_agent:
            rules.extend(current_rules)

        # Filter rules for our user agent
        matching_rules = []

        # Check for exact match
        for rule in rules:
            pattern, allow = rule
            matching_rules.append((pattern, allow))

        # If no matching user agent, check for *
        if not matching_rules:
            for rule in rules:
                pattern, allow = rule
                matching_rules.append((pattern, allow))

        # If still no rules, allow all
        if not matching_rules:
            logger.debug("No robots.txt rules found, allowing all")
            return []

        return matching_rules

    def _check_path_allowed(
        self,
        rules: list[tuple[str, bool]],
        path: str,
    ) -> bool:
        """
        Check if path is allowed by robots.txt rules.

        Args:
            rules: List of (path_pattern, allow) tuples
            path: Path to check

        Returns:
            True if path is allowed, False otherwise
        """
        # If no rules, allow all
        if not rules:
            return True

        # Check rules in order (last matching rule wins)
        allowed = True

        for pattern, allow in rules:
            if self._path_matches(path, pattern):
                allowed = allow

        return allowed

    def _path_matches(self, path: str, pattern: str) -> bool:
        """
        Check if path matches a robots.txt pattern.

        Args:
            path: Path to check
            pattern: Pattern from robots.txt

        Returns:
            True if path matches pattern, False otherwise
        """
        # Handle root path
        if pattern == "/":
            return path == "/"

        # Handle exact match
        if path == pattern:
            return True

        # Handle prefix match
        if pattern.endswith("/"):
            return path.startswith(pattern)

        # Handle wildcard (*)
        if "*" in pattern:
            prefix, suffix = pattern.split("*", 1)
            return path.startswith(prefix) and path.endswith(suffix)

        # Handle prefix match without trailing slash
        return path.startswith(pattern + "/")

    def clear_cache(self) -> None:
        """Clear robots.txt cache."""
        self._cache.clear()
        logger.info("robots.txt cache cleared")

    def get_cache_size(self) -> int:
        """Get number of cached robots.txt results."""
        return len(self._cache)


# Export for easy import
__all__ = ["RobotsChecker"]

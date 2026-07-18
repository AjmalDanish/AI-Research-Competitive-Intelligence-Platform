"""
Robots Checker Tests

Unit tests for robots.txt handling.
"""

import pytest

from backend.crawler.robots import RobotsChecker
from backend.crawler.exceptions import RobotsDeniedException


class TestRobotsChecker:
    """Test robots.txt checker."""
    
    @pytest.fixture
    def robots_checker(self):
        """Create robots checker instance."""
        return RobotsChecker(
            timeout=10,
            cache_ttl=3600,
            respect_robots=True,
        )
    
    @pytest.mark.asyncio
    async def test_can_fetch_without_respect_robots(self):
        """Test that all URLs are allowed when robots checking disabled."""
        checker = RobotsChecker(
            timeout=10,
            cache_ttl=3600,
            respect_robots=False,  # Disable robots checking
        )
        
        result = await checker.can_fetch(
            "https://example.com/path",
            "test-user-agent",
        )
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_extract_domain(self, robots_checker):
        """Test domain extraction from URLs."""
        test_cases = [
            ("https://example.com/path", "example.com"),
            ("https://sub.example.com/path", "sub.example.com"),
            ("https://example.com:8080/path", "example.com:8080"),
        ]
        
        for url, expected_domain in test_cases:
            domain = robots_checker._extract_domain(url)
            assert domain == expected_domain, f"Expected {expected_domain}, got {domain}"
    
    @pytest.mark.asyncio
    async def test_extract_path(self, robots_checker):
        """Test path extraction from URLs."""
        test_cases = [
            ("https://example.com/path", "/path"),
            ("https://example.com/path?query=value", "/path"),
            ("https://example.com/", "/"),
            ("https://example.com", ""),
        ]
        
        for url, expected_path in test_cases:
            path = robots_checker._extract_path(url)
            assert path == expected_path, f"Expected {expected_path}, got {path}"
    
    def test_parse_robots_txt_basic_rules(self, robots_checker):
        """Test parsing basic robots.txt rules."""
        robots_content = """
User-agent: *
Disallow: /admin
Allow: /public
"""
        
        rules = robots_checker._parse_robots_txt(robots_content, "*")
        
        # Should have rules for /admin (disallow) and /public (allow)
        assert len(rules) == 2
        
        # Check disallow rule
        disallow_rule = next((r for r in rules if r[0] == "/admin"), None)
        assert disallow_rule is not None
        assert disallow_rule[1] is False  # Disallow
        
        # Check allow rule
        allow_rule = next((r for r in rules if r[0] == "/public"), None)
        assert allow_rule is not None
        assert allow_rule[1] is True  # Allow
    
    def test_parse_robots_txt_specific_user_agent(self, robots_checker):
        """Test parsing robots.txt with specific user agent."""
        robots_content = """
User-agent: test-bot
Disallow: /private

User-agent: *
Disallow: /admin
"""
        
        # Check specific user agent
        rules = robots_checker._parse_robots_txt(robots_content, "test-bot")
        assert len(rules) == 2
        
        # Check wildcard user agent
        rules_wildcard = robots_checker._parse_robots_txt(robots_content, "*")
        assert len(rules_wildcard) == 1
    
    def test_check_path_allowed(self, robots_checker):
        """Test path checking against rules."""
        # Allow all paths if no rules
        assert robots_checker._check_path_allowed([], "/any-path")
        
        # Disallow specific path
        rules = [("/admin", False)]
        assert not robots_checker._check_path_allowed(rules, "/admin")
        assert robots_checker._check_path_allowed(rules, "/public")
        
        # Allow specific path
        rules = [("/admin", False), ("/public", True)]
        assert not robots_checker._check_path_allowed(rules, "/admin")
        assert robots_checker._check_path_allowed(rules, "/public")
    
    def test_path_matching(self, robots_checker):
        """Test path pattern matching."""
        # Exact match
        assert robots_checker._path_matches("/admin", "/admin")
        
        # Prefix match
        assert robots_checker._path_matches("/admin/users", "/admin/")
        
        # No match
        assert not robots_checker._path_matches("/public", "/admin/")
        
        # Root path
        assert robots_checker._path_matches("/", "/")
    
    def test_clear_cache(self, robots_checker):
        """Test clearing robots.txt cache."""
        # Add something to cache
        robots_checker._cache["example.com"] = ([], None)
        
        # Should have cache entry
        assert len(robots_checker._cache) > 0
        
        # Clear cache
        robots_checker.clear_cache()
        
        # Cache should be empty
        assert len(robots_checker._cache) == 0
    
    def test_get_cache_size(self, robots_checker):
        """Test getting cache size."""
        # Cache should start empty
        assert robots_checker.get_cache_size() == 0
        
        # Add cache entries
        robots_checker._cache["example1.com"] = ([], None)
        robots_checker._cache["example2.com"] = ([], None)
        
        # Cache should have 2 entries
        assert robots_checker.get_cache_size() == 2
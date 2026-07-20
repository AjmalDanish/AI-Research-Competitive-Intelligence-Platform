"""
Parser service for HTML content extraction.

This module provides the main orchestrator for parsing operations,
offering strategy pattern for selecting appropriate parsers.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime

from backend.core.interfaces.parser import IParser
from backend.core.domain.parser import ParserResult
from backend.parser.implementations.beautifulsoup_parser import BeautifulSoupParser
from backend.parser.implementations.trafilatura_parser import TrafilaturaParser
from backend.config.logging import get_logger

logger = get_logger(__name__)


class ParserService:
    """
    Service for HTML content parsing with strategy pattern.

    Provides parsing capabilities with multiple parser strategies
    and automatic fallback mechanisms.
    """

    def __init__(self, default_parser: str = "beautifulsoup"):
        """
        Initialize parser service.

        Args:
            default_parser: Default parser strategy ("beautifulsoup" or "trafilatura")
        """
        self.default_parser = default_parser
        self.logger = logger

        # Initialize available parsers
        self.parsers: Dict[str, IParser] = {
            "beautifulsoup": BeautifulSoupParser(),
            "trafilatura": TrafilaturaParser(),
        }

        # Validate default parser
        if default_parser not in self.parsers:
            self.logger.warning(f"Unknown default parser '{default_parser}', using 'beautifulsoup'")
            self.default_parser = "beautifulsoup"

    async def parse(
        self,
        html_content: str,
        url: str,
        parser_type: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> ParserResult:
        """
        Parse HTML content with specified or default parser.

        Args:
            html_content: Raw HTML content to parse
            url: Source URL of the content
            parser_type: Optional specific parser type
            options: Optional parsing options

        Returns:
            ParserResult: Structured parsing result
        """
        start_time = datetime.now()

        try:
            # Determine parser to use
            parser_type = parser_type or self.default_parser

            if parser_type not in self.parsers:
                self.logger.warning(
                    f"Unknown parser '{parser_type}', using default '{self.default_parser}'"
                )
                parser_type = self.default_parser

            # Get parser
            parser = self.parsers[parser_type]

            # Add timing info to options
            if not options:
                options = {}
            options["start_time"] = start_time.isoformat()

            # Parse content
            result = await parser.parse(html_content, url, options)

            # Add end time and duration
            end_time = datetime.now()
            duration_ms = int((end_time - start_time).total_seconds() * 1000)

            if result.metrics:
                result.metrics.end_time = end_time.isoformat()
                result.metrics.duration_ms = duration_ms

            # Log results
            if result.success:
                self.logger.info(
                    f"Parsing successful for {url}",
                    parser_type=parser_type,
                    duration_ms=duration_ms,
                    title=result.title,
                )
            else:
                self.logger.error(
                    f"Parsing failed for {url}", parser_type=parser_type, error=result.error
                )

            return result

        except Exception as e:
            self.logger.error(f"Parser service error for {url}", error=str(e))

            return ParserResult(
                url=url,
                html_content=html_content,
                success=False,
                error=f"Parser service error: {str(e)}",
            )

    async def parse_with_fallback(
        self,
        html_content: str,
        url: str,
        preferred_parser: str = "beautifulsoup",
        fallback_parser: str = "trafilatura",
    ) -> ParserResult:
        """
        Parse HTML with automatic fallback to secondary parser.

        Args:
            html_content: Raw HTML content to parse
            url: Source URL of the content
            preferred_parser: Primary parser to try first
            fallback_parser: Secondary parser if primary fails

        Returns:
            ParserResult: Best parsing result from either parser
        """
        # Try preferred parser first
        try:
            self.logger.info(f"Attempting parse with {preferred_parser}")
            result = await self.parse(html_content, url, preferred_parser)

            if result.success:
                return result

            self.logger.warning(
                f"{preferred_parser} parser failed, trying {fallback_parser}", error=result.error
            )

        except Exception as e:
            self.logger.error(f"{preferred_parser} parser exception", error=str(e))

        # Try fallback parser
        try:
            self.logger.info(f"Attempting parse with {fallback_parser}")
            result = await self.parse(html_content, url, fallback_parser)
            return result

        except Exception as e:
            self.logger.error(f"{fallback_parser} parser also failed", error=str(e))

            # Return failed result
            return ParserResult(
                url=url,
                html_content=html_content,
                success=False,
                error=f"All parsers failed. Last error: {str(e)}",
            )

    def can_parse(self, html_content: str, parser_type: Optional[str] = None) -> bool:
        """
        Check if HTML content can be parsed.

        Args:
            html_content: HTML content to check
            parser_type: Optional specific parser type

        Returns:
            bool: True if content can be parsed
        """
        parser_type = parser_type or self.default_parser

        if parser_type not in self.parsers:
            return False

        return self.parsers[parser_type].can_parse(html_content)

    def get_available_parsers(self) -> List[str]:
        """
        Get list of available parser types.

        Returns:
            List[str]: List of available parser names
        """
        return list(self.parsers.keys())

    def get_parser_capabilities(self, parser_type: str) -> Dict[str, Any]:
        """
        Get capabilities of a specific parser.

        Args:
            parser_type: Parser type to query

        Returns:
            Dict[str, Any]: Parser capabilities
        """
        if parser_type not in self.parsers:
            return {"available": False, "capabilities": []}

        parser = self.parsers[parser_type]

        capabilities = {"available": True, "name": parser.parser_name, "features": []}

        # Add feature capabilities based on parser type
        if parser_type == "beautifulsoup":
            capabilities["features"] = [
                "dom_traversal",
                "metadata_extraction",
                "heading_extraction",
                "link_extraction",
                "image_extraction",
                "script_extraction",
                "stylesheet_extraction",
                "language_detection",
            ]
        elif parser_type == "trafilatura":
            capabilities["features"] = [
                "text_extraction",
                "metadata_extraction",
                "language_detection",
                "content_cleaning",
                "article_extraction",
            ]

        return capabilities

    def recommend_parser(self, html_content: str, requirements: Optional[List[str]] = None) -> str:
        """
        Recommend best parser for given content and requirements.

        Args:
            html_content: HTML content to analyze
            requirements: Optional list of required features

        Returns:
            str: Recommended parser type
        """
        if not requirements:
            # Default to BeautifulSoup for comprehensive parsing
            return "beautifulsoup"

        requirements_lower = [r.lower() for r in requirements]

        # Check BeautifulSoup capabilities
        bs_features = [
            "dom_traversal",
            "heading_extraction",
            "link_extraction",
            "image_extraction",
        ]

        if any(req in bs_features for req in requirements_lower):
            return "beautifulsoup"

        # Check Trafilatura capabilities
        tf_features = [
            "text_extraction",
            "content_cleaning",
            "article_extraction",
        ]

        if any(req in tf_features for req in requirements_lower):
            return "trafilatura"

        # Default fallback
        return "beautifulsoup"

    async def batch_parse(
        self, html_contents: List[tuple[str, str]], parser_type: Optional[str] = None
    ) -> List[ParserResult]:
        """
        Parse multiple HTML contents in sequence.

        Args:
            html_contents: List of (html_content, url) tuples
            parser_type: Optional specific parser type for all

        Returns:
            List[ParserResult]: Parsing results for each content
        """
        results = []

        for html_content, url in html_contents:
            try:
                result = await self.parse(html_content, url, parser_type)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Failed to parse {url} in batch", error=str(e))
                results.append(
                    ParserResult(
                        url=url,
                        html_content=html_content,
                        success=False,
                        error=f"Batch parsing error: {str(e)}",
                    )
                )

        # Log batch results
        successful = sum(1 for r in results if r.success)
        self.logger.info(
            f"Batch parsing completed",
            total=len(results),
            successful=successful,
            failed=len(results) - successful,
        )

        return results


# Global parser service instance
parser_service = ParserService()


async def get_parser_service() -> ParserService:
    """
    Get the global parser service instance.

    Returns:
        ParserService: Global parser service
    """
    return parser_service


# Export for easy import
__all__ = [
    "ParserService",
    "parser_service",
    "get_parser_service",
]

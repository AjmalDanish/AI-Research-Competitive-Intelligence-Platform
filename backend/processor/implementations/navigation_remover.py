"""
Navigation and Footer Remover Implementation.

Removes navigation and footer content including:
- Navigation menus
- Breadcrumb navigation
- Footer links
- Sidebar content
- Header navigation
"""

import re
from typing import Any, Dict, List

from backend.core.interfaces.content_processor import IContentProcessor
from backend.core.domain.content_processor import ProcessingStage, ProcessingOptions


class NavigationRemover(IContentProcessor):
    """
    Removes navigation and footer content.

    This processor handles:
    - Navigation menus
    - Footer links
    - Sidebar content
    - Breadcrumb trails
    - Header navigation
    """

    def __init__(self):
        """Initialize navigation/footer remover."""
        self.stage = ProcessingStage.NAVIGATION_FOOTER_REMOVAL

        # Navigation indicators
        self.navigation_indicators = [
            # Navigation menu indicators
            r"Navigation:",
            r"Menu:",
            r"Home.*?About.*?Contact",
            r"Skip to (main )?content",
            # Breadcrumb indicators
            r"Home\s*[>›»]\s*[\w\s]+",
            r"Breadcrumb:",
            r"You are here:",
            # Header navigation
            r"Log in|Sign in|Sign up",
            r"Account|Profile|Settings",
            r"Cart.*?Checkout",
        ]

        # Footer indicators
        self.footer_indicators = [
            # Footer content indicators
            r"©.*?(?=\n|$)",
            r"All rights reserved",
            r"Privacy [Pp]olicy",
            r"Terms of [Ss]ervice",
            r"Contact us",
            r"Social media",
            r"Follow us",
            r"Sitemap",
        ]

    def get_stage(self) -> ProcessingStage:
        """Return the processing stage."""
        return self.stage

    def process(
        self,
        content: str,
        metadata: Dict[str, Any],
        options: ProcessingOptions,
        context: Dict[str, Any],
    ) -> tuple[str, Dict[str, Any]]:
        """
        Remove navigation and footer content.

        Args:
            content: Input content with navigation/footer
            metadata: Content metadata
            options: Processing configuration options
            context: Processing context

        Returns:
            Tuple of (cleaned_content, updated_metadata)
        """
        if self.should_skip_content(content, options):
            return content, metadata

        cleaned_content = content
        removed_sections = []

        # Remove navigation menus if enabled
        if options.remove_navigation_menus:
            cleaned_content, nav_removed = self._remove_navigation(cleaned_content)
            removed_sections.extend(nav_removed)

        # Remove footers if enabled
        if options.remove_footers:
            cleaned_content, footer_removed = self._remove_footers(cleaned_content)
            removed_sections.extend(footer_removed)

        # Remove sidebars if enabled
        if options.remove_sidebars:
            cleaned_content, sidebar_removed = self._remove_sidebars(cleaned_content)
            removed_sections.extend(sidebar_removed)

        # Update metadata
        metadata["navigation_footer_removed"] = True
        metadata["navigation_sections_removed"] = len(removed_sections)

        # Track metrics
        context.setdefault("metrics", {})
        context["metrics"]["navigation_sections_removed"] = len(removed_sections)

        return cleaned_content, metadata

    def validate(
        self, content: str, metadata: Dict[str, Any], options: ProcessingOptions
    ) -> list[str]:
        """
        Validate content for navigation/footer removal.

        Args:
            content: Content to validate
            metadata: Content metadata
            options: Processing configuration options

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        # Check if content would become too short
        estimated_removed = len(self._find_navigation_footer_lines(content))
        if len(content) - estimated_removed < options.minimum_content_length:
            errors.append("Content too short after navigation/footer removal")

        return errors

    def get_processing_metrics(
        self, input_length: int, output_length: int, duration_seconds: float
    ) -> Dict[str, Any]:
        """
        Calculate processing metrics for navigation/footer removal.

        Args:
            input_length: Length of input content
            output_length: Length of output content
            duration_seconds: Processing duration

        Returns:
            Dictionary of processing metrics
        """
        removed = input_length - output_length
        removal_percentage = (removed / input_length * 100) if input_length > 0 else 0

        return {
            "input_length": input_length,
            "output_length": output_length,
            "removed": removed,
            "removal_percentage": removal_percentage,
            "duration_seconds": duration_seconds,
            "sections_removed": removed,
        }

    def _remove_navigation(self, content: str) -> tuple[str, List[str]]:
        """
        Remove navigation menu content.

        Args:
            content: Content with navigation menus

        Returns:
            Tuple of (cleaned_content, removed_sections)
        """
        removed_sections = []
        cleaned_content = content

        for pattern in self.navigation_indicators:
            nav_content = re.findall(
                pattern, cleaned_content, re.IGNORECASE | re.MULTILINE
            )
            if nav_content:
                removed_sections.extend(nav_content)
                cleaned_content = re.sub(
                    pattern, "", cleaned_content, flags=re.IGNORECASE | re.MULTILINE
                )

        return cleaned_content, removed_sections

    def _remove_footers(self, content: str) -> tuple[str, List[str]]:
        """
        Remove footer content.

        Args:
            content: Content with footer content

        Returns:
            Tuple of (cleaned_content, removed_sections)
        """
        removed_sections = []
        cleaned_content = content

        for pattern in self.footer_indicators:
            footer_content = re.findall(
                pattern, cleaned_content, re.IGNORECASE | re.MULTILINE
            )
            if footer_content:
                removed_sections.extend(footer_content)
                cleaned_content = re.sub(
                    pattern, "", cleaned_content, flags=re.IGNORECASE | re.MULTILINE
                )

        return cleaned_content, removed_sections

    def _remove_sidebars(self, content: str) -> tuple[str, List[str]]:
        """
        Remove sidebar content.

        Args:
            content: Content with sidebar content

        Returns:
            Tuple of (cleaned_content, removed_sections)
        """
        # Sidebar indicators (simplified)
        sidebar_patterns = [
            r"Sidebar:.*?(?=\n\n|$)",
            r"Also read:.*?(?=\n\n|$)",
            r"Related posts:.*?(?=\n\n|$)",
        ]

        removed_sections = []
        cleaned_content = content

        for pattern in sidebar_patterns:
            sidebar_content = re.findall(
                pattern, cleaned_content, re.IGNORECASE | re.DOTALL
            )
            if sidebar_content:
                removed_sections.extend(sidebar_content)
                cleaned_content = re.sub(
                    pattern, "", cleaned_content, flags=re.IGNORECASE | re.DOTALL
                )

        return cleaned_content, removed_sections

    def _find_navigation_footer_lines(self, content: str) -> List[str]:
        """
        Find lines that are likely navigation or footer content.

        Args:
            content: Content to analyze

        Returns:
            List of navigation/footer lines
        """
        lines = content.split("\n")
        nav_footer_lines = []

        for line in lines:
            line_lower = line.lower().strip()

            # Check navigation indicators
            for pattern in self.navigation_indicators:
                if re.search(pattern, line_lower):
                    nav_footer_lines.append(line)
                    break

            # Check footer indicators
            for pattern in self.footer_indicators:
                if re.search(pattern, line_lower):
                    nav_footer_lines.append(line)
                    break

        return nav_footer_lines

    def estimate_processing_time(
        self, content_length: int, options: ProcessingOptions
    ) -> float:
        """
        Estimate processing time for navigation/footer removal.

        Args:
            content_length: Length of content to process
            options: Processing configuration options

        Returns:
            Estimated processing time in seconds
        """
        # Navigation/footer removal is moderately fast: 0.001 seconds per character
        return content_length * 0.001

    def get_memory_usage_estimate(self, content_length: int) -> int:
        """
        Estimate memory usage for navigation/footer removal.

        Args:
            content_length: Length of content to process

        Returns:
            Estimated memory usage in bytes
        """
        # Medium memory usage: 3x content size
        return content_length * 3

"""
Boilerplate Remover Implementation.

Removes boilerplate content including:
- Navigation menus
- Footer content
- Copyright notices
- Cookie notices
- Advertisement blocks
- Social media widgets
- Subscription forms
"""

import re
from typing import Any, Dict, List

from backend.core.interfaces.content_processor import IContentProcessor
from backend.core.domain.content_processor import ProcessingStage, ProcessingOptions


class BoilerplateRemover(IContentProcessor):
    """
    Removes boilerplate content from text.

    This processor handles:
    - Common boilerplate patterns
    - Navigation elements
    - Footer content
    - Advertisement indicators
    - Cookie consent notices
    """

    def __init__(self):
        """Initialize boilerplate remover."""
        self.stage = ProcessingStage.BOILERPLATE_REMOVAL

        # Common boilerplate patterns
        self.boilerplate_patterns = [
            # Copyright notices
            r"©\s*\d{4}\s*[A-Za-z\s]+.*?(?=\n|$)",
            r"All rights reserved",
            r"Reproduction prohibited",
            # Cookie notices
            r"Cookies? [Pp]olicy",
            r"We use cookies",
            r"By continuing to use",
            r"Cookie consent",
            # Subscription forms
            r"Subscribe to our",
            r"Sign up for",
            r"Join our newsletter",
            r"Get the latest news",
            # Social media
            r"Follow us on",
            r"Connect with us",
            r"Like us on Facebook",
            r"Follow on Twitter",
            # Privacy policy links
            r"Privacy [Pp]olicy",
            r"Terms of [Ss]ervice",
            r"Terms and [Cc]onditions",
            # Footer indicators
            r"Contact us:",
            r"Email us at:",
            r"Call us at:",
            # Ad indicators
            r"Advertisement",
            r"Sponsored content",
            r"Paid promotion",
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
        Remove boilerplate content.

        Args:
            content: Input content with boilerplate
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

        # Remove comments if enabled
        if options.remove_comments:
            cleaned_content, comments_removed = self._remove_comments(cleaned_content)
            removed_sections.extend(comments_removed)

        # Remove advertisements if enabled
        if options.remove_advertisements:
            cleaned_content, ads_removed = self._remove_advertisements(cleaned_content)
            removed_sections.extend(ads_removed)

        # Remove social media widgets if enabled
        if options.remove_social_media_widgets:
            cleaned_content, social_removed = self._remove_social_media(cleaned_content)
            removed_sections.extend(social_removed)

        # Remove common boilerplate patterns
        cleaned_content, boilerplate_removed = self._remove_boilerplate_patterns(
            cleaned_content
        )
        removed_sections.extend(boilerplate_removed)

        # Update metadata
        metadata["boilerplate_removed"] = True
        metadata["boilerplate_sections_removed"] = len(removed_sections)

        # Track metrics
        context.setdefault("metrics", {})
        context["metrics"]["boilerplate_sections_removed"] = len(removed_sections)

        return cleaned_content, metadata

    def validate(
        self, content: str, metadata: Dict[str, Any], options: ProcessingOptions
    ) -> list[str]:
        """
        Validate content for boilerplate removal.

        Args:
            content: Content to validate
            metadata: Content metadata
            options: Processing configuration options

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        # Check if content would become too short
        estimated_removed = len(self._find_boilerplate_lines(content))
        if len(content) - estimated_removed < options.minimum_content_length:
            errors.append("Content too short after boilerplate removal")

        return errors

    def get_processing_metrics(
        self, input_length: int, output_length: int, duration_seconds: float
    ) -> Dict[str, Any]:
        """
        Calculate processing metrics for boilerplate removal.

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
            "sections_removed": removed,  # Approximation
        }

    def _remove_comments(self, content: str) -> tuple[str, List[str]]:
        """
        Remove HTML and text comments.

        Args:
            content: Content with comments

        Returns:
            Tuple of (cleaned_content, removed_comments)
        """
        # Remove HTML comments
        html_comment_pattern = r"<!--.*?-->"
        comments = re.findall(html_comment_pattern, content, re.DOTALL)
        cleaned_content = re.sub(html_comment_pattern, "", content)

        return cleaned_content, comments

    def _remove_advertisements(self, content: str) -> tuple[str, List[str]]:
        """
        Remove advertisement blocks.

        Args:
            content: Content with advertisements

        Returns:
            Tuple of (cleaned_content, removed_sections)
        """
        # Simple advertisement detection
        ad_patterns = [
            r"Advertisement.*?(?=\n\n|$)",
            r"Sponsored.*?(?=\n\n|$)",
            r"Ad by.*?(?=\n\n|$)",
        ]

        removed_sections = []
        cleaned_content = content

        for pattern in ad_patterns:
            ads = re.findall(pattern, cleaned_content, re.IGNORECASE | re.DOTALL)
            if ads:
                removed_sections.extend(ads)
                cleaned_content = re.sub(
                    pattern, "", cleaned_content, flags=re.IGNORECASE | re.DOTALL
                )

        return cleaned_content, removed_sections

    def _remove_social_media(self, content: str) -> tuple[str, List[str]]:
        """
        Remove social media widget content.

        Args:
            content: Content with social media widgets

        Returns:
            Tuple of (cleaned_content, removed_sections)
        """
        # Social media patterns
        social_patterns = [
            r"Follow us on.*?(?=\n\n|$)",
            r"Connect with us.*?(?=\n\n|$)",
            r"Like.*?share.*?(?=\n\n|$)",
        ]

        removed_sections = []
        cleaned_content = content

        for pattern in social_patterns:
            social_content = re.findall(
                pattern, cleaned_content, re.IGNORECASE | re.DOTALL
            )
            if social_content:
                removed_sections.extend(social_content)
                cleaned_content = re.sub(
                    pattern, "", cleaned_content, flags=re.IGNORECASE | re.DOTALL
                )

        return cleaned_content, removed_sections

    def _remove_boilerplate_patterns(self, content: str) -> tuple[str, List[str]]:
        """
        Remove common boilerplate patterns.

        Args:
            content: Content with boilerplate patterns

        Returns:
            Tuple of (cleaned_content, removed_patterns)
        """
        removed_patterns = []
        cleaned_content = content

        for pattern in self.boilerplate_patterns:
            matches = re.findall(pattern, cleaned_content, re.IGNORECASE | re.MULTILINE)
            if matches:
                removed_patterns.extend(matches)
                cleaned_content = re.sub(
                    pattern, "", cleaned_content, flags=re.IGNORECASE | re.MULTILINE
                )

        return cleaned_content, removed_patterns

    def _find_boilerplate_lines(self, content: str) -> List[str]:
        """
        Find lines that are likely boilerplate.

        Args:
            content: Content to analyze

        Returns:
            List of boilerplate lines
        """
        lines = content.split("\n")
        boilerplate_lines = []

        for line in lines:
            line_lower = line.lower().strip()
            for pattern in self.boilerplate_patterns:
                if re.search(pattern, line_lower):
                    boilerplate_lines.append(line)
                    break

        return boilerplate_lines

    def estimate_processing_time(
        self, content_length: int, options: ProcessingOptions
    ) -> float:
        """
        Estimate processing time for boilerplate removal.

        Args:
            content_length: Length of content to process
            options: Processing configuration options

        Returns:
            Estimated processing time in seconds
        """
        # Boilerplate removal is moderately fast: 0.001 seconds per character
        return content_length * 0.001

    def get_memory_usage_estimate(self, content_length: int) -> int:
        """
        Estimate memory usage for boilerplate removal.

        Args:
            content_length: Length of content to process

        Returns:
            Estimated memory usage in bytes
        """
        # Medium memory usage: 3x content size
        return content_length * 3

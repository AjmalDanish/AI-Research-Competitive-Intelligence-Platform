"""
Duplicate Detector Implementation.

Detects and removes duplicate content including:
- Exact duplicate paragraphs
- Near-duplicate content
- Repeated phrases
"""

from difflib import SequenceMatcher
from typing import Any, Dict, List, Tuple

from backend.core.interfaces.content_processor import IContentProcessor
from backend.core.domain.content_processor import ProcessingStage, ProcessingOptions


class DuplicateDetector(IContentProcessor):
    """
    Detects and removes duplicate content.

    This processor handles:
    - Exact duplicate detection
    - Near-duplicate detection
    - Phrase-level duplicates
    - Content uniqueness scoring
    """

    def __init__(self):
        """Initialize duplicate detector."""
        self.stage = ProcessingStage.DUPLICATE_DETECTION

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
        Detect and remove duplicate content.

        Args:
            content: Input content with potential duplicates
            metadata: Content metadata
            options: Processing configuration options
            context: Processing context

        Returns:
            Tuple of (deduplicated_content, updated_metadata)
        """
        if self.should_skip_content(content, options):
            return content, metadata

        # Split content into paragraphs
        paragraphs = self._split_into_paragraphs(content)

        # Detect duplicates
        duplicates = self._detect_duplicates(paragraphs, options)

        # Remove duplicates
        unique_paragraphs = self._remove_duplicates(paragraphs, duplicates)

        # Reconstruct content
        deduplicated_content = "\n\n".join(unique_paragraphs)

        # Update metadata
        metadata["duplicates_removed"] = len(duplicates)
        metadata["duplicate_content_removed"] = True

        # Track metrics
        context.setdefault("metrics", {})
        context["metrics"]["duplicates_removed"] = len(duplicates)

        return deduplicated_content, metadata

    def validate(
        self, content: str, metadata: Dict[str, Any], options: ProcessingOptions
    ) -> list[str]:
        """
        Validate content for duplicate detection.

        Args:
            content: Content to validate
            metadata: Content metadata
            options: Processing configuration options

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        # Check if content is too short
        if len(content.strip()) < options.min_duplicate_length:
            errors.append("Content too short for duplicate detection")

        # Validate similarity threshold
        if not 0 <= options.similarity_threshold <= 1:
            errors.append(
                f"Invalid similarity threshold: {options.similarity_threshold}"
            )

        return errors

    def get_processing_metrics(
        self, input_length: int, output_length: int, duration_seconds: float
    ) -> Dict[str, Any]:
        """
        Calculate processing metrics for duplicate detection.

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
            "duplicates_detected": input_length - output_length,  # Approximation
        }

    def _split_into_paragraphs(self, content: str) -> List[str]:
        """
        Split content into paragraphs.

        Args:
            content: Content to split

        Returns:
            List of paragraphs
        """
        # Split by double newlines to get paragraphs
        paragraphs = content.split("\n\n")
        return [p.strip() for p in paragraphs if p.strip()]

    def _detect_duplicates(
        self, paragraphs: List[str], options: ProcessingOptions
    ) -> List[Tuple[int, int]]:
        """
        Detect duplicate paragraphs.

        Args:
            paragraphs: List of paragraphs to check
            options: Processing configuration options

        Returns:
            List of tuples (original_index, duplicate_index)
        """
        duplicates = []

        for i, para1 in enumerate(paragraphs):
            # Skip short paragraphs
            if len(para1) < options.min_duplicate_length:
                continue

            for j, para2 in enumerate(paragraphs[i + 1 :], i + 1):
                # Skip short paragraphs
                if len(para2) < options.min_duplicate_length:
                    continue

                # Check for exact match
                if para1 == para2:
                    duplicates.append((i, j))
                else:
                    # Check for near-duplicate
                    similarity = self._calculate_similarity(para1, para2)
                    if similarity >= options.similarity_threshold:
                        duplicates.append((i, j))

        return duplicates

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two text strings.

        Args:
            text1: First text string
            text2: Second text string

        Returns:
            Similarity score between 0.0 and 1.0
        """
        return SequenceMatcher(None, text1, text2).ratio()

    def _remove_duplicates(
        self, paragraphs: List[str], duplicates: List[Tuple[int, int]]
    ) -> List[str]:
        """
        Remove duplicate paragraphs, keeping the first occurrence.

        Args:
            paragraphs: List of all paragraphs
            duplicates: List of duplicate indices

        Returns:
            List of unique paragraphs
        """
        # Collect indices to remove (keep first occurrence)
        indices_to_remove = set()
        for original, duplicate in duplicates:
            indices_to_remove.add(duplicate)

        # Return paragraphs not marked for removal
        unique_paragraphs = [
            para for i, para in enumerate(paragraphs) if i not in indices_to_remove
        ]

        return unique_paragraphs

    def estimate_processing_time(
        self, content_length: int, options: ProcessingOptions
    ) -> float:
        """
        Estimate processing time for duplicate detection.

        Args:
            content_length: Length of content to process
            options: Processing configuration options

        Returns:
            Estimated processing time in seconds
        """
        # Duplicate detection is computationally intensive: 0.005 seconds per character
        return content_length * 0.005

    def get_memory_usage_estimate(self, content_length: int) -> int:
        """
        Estimate memory usage for duplicate detection.

        Args:
            content_length: Length of content to process

        Returns:
            Estimated memory usage in bytes
        """
        # High memory usage due to comparison matrix: 5x content size
        return content_length * 5

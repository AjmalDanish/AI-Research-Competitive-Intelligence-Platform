"""
Paragraph Reconstructor Implementation.

Reconstructs and normalizes paragraphs including:
- Paragraph boundary detection
- Paragraph quality assessment
- Paragraph merging and splitting
- Paragraph metadata extraction
"""

import re
from typing import Any, Dict, List

from backend.core.interfaces.content_processor import IContentProcessor
from backend.core.domain.content_processor import ProcessingStage, ProcessingOptions


class ParagraphReconstructor(IContentProcessor):
    """
    Reconstructs and normalizes paragraph structure.

    This processor handles:
    - Paragraph boundary detection
    - Paragraph quality assessment
    - Paragraph merging and splitting
    - Paragraph statistics calculation
    """

    def __init__(self):
        """Initialize paragraph reconstructor."""
        self.stage = ProcessingStage.PARAGRAPH_RECONSTRUCTION

    def get_stage(self) -> ProcessingStage:
        """Return the processing stage."""
        return self.stage

    def process(
        self,
        content: str,
        metadata: Dict[str, Any],
        options: ProcessingOptions,
        context: Dict[str, Any]
    ) -> tuple[str, Dict[str, Any]]:
        """
        Reconstruct and normalize paragraphs.

        Args:
            content: Input content to reconstruct
            metadata: Content metadata
            options: Processing configuration options
            context: Processing context

        Returns:
            Tuple of (reconstructed_content, updated_metadata)
        """
        if self.should_skip_content(content, options):
            return content, metadata

        # Split content into paragraphs
        paragraphs = self._split_into_paragraphs(content)

        # Filter and normalize paragraphs
        normalized_paragraphs = self._normalize_paragraphs(paragraphs, options)

        # Merge short paragraphs if needed
        merged_paragraphs = self._merge_short_paragraphs(normalized_paragraphs, options)

        # Split long paragraphs if needed
        reconstructed_paragraphs = self._split_long_paragraphs(merged_paragraphs, options)

        # Reconstruct content
        reconstructed_content = '\n\n'.join(reconstructed_paragraphs)

        # Update metadata
        metadata["paragraphs_reconstructed"] = True
        metadata["paragraph_count"] = len(reconstructed_paragraphs)

        # Track metrics
        context.setdefault("metrics", {})
        context["metrics"]["paragraphs_reconstructed"] = len(reconstructed_paragraphs)

        return reconstructed_content, metadata

    def validate(
        self,
        content: str,
        metadata: Dict[str, Any],
        options: ProcessingOptions
    ) -> list[str]:
        """
        Validate content for paragraph reconstruction.

        Args:
            content: Content to validate
            metadata: Content metadata
            options: Processing configuration options

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        # Validate paragraph length constraints
        if options.min_paragraph_length < 1:
            errors.append("Minimum paragraph length must be positive")

        if options.max_paragraph_length < options.min_paragraph_length:
            errors.append("Maximum paragraph length must be greater than minimum")

        return errors

    def get_processing_metrics(
        self,
        input_length: int,
        output_length: int,
        duration_seconds: float
    ) -> Dict[str, Any]:
        """
        Calculate processing metrics for paragraph reconstruction.

        Args:
            input_length: Length of input content
            output_length: Length of output content
            duration_seconds: Processing duration

        Returns:
            Dictionary of processing metrics
        """
        return {
            "input_length": input_length,
            "output_length": output_length,
            "duration_seconds": duration_seconds,
            "paragraphs_reconstructed": output_length,  # Approximation
        }

    def _split_into_paragraphs(self, content: str) -> List[str]:
        """
        Split content into paragraphs.

        Args:
            content: Content to split

        Returns:
            List of paragraphs
        """
        # Split by double newlines, then clean each paragraph
        raw_paragraphs = content.split('\n\n')
        paragraphs = []

        for para in raw_paragraphs:
            cleaned_para = para.strip()
            if cleaned_para:
                # Replace single newlines within paragraph with spaces
                cleaned_para = ' '.join(cleaned_para.split('\n'))
                paragraphs.append(cleaned_para)

        return paragraphs

    def _normalize_paragraphs(
        self,
        paragraphs: List[str],
        options: ProcessingOptions
    ) -> List[str]:
        """
        Normalize paragraph structure.

        Args:
            paragraphs: List of paragraphs to normalize
            options: Processing configuration options

        Returns:
            List of normalized paragraphs
        """
        normalized = []

        for paragraph in paragraphs:
            # Filter out very short paragraphs
            if len(paragraph) < options.min_paragraph_length:
                continue

            # Filter out very long paragraphs
            if len(paragraph) > options.max_paragraph_length:
                continue

            normalized.append(paragraph)

        return normalized

    def _merge_short_paragraphs(
        self,
        paragraphs: List[str],
        options: ProcessingOptions
    ) -> List[str]:
        """
        Merge very short paragraphs with neighbors.

        Args:
            paragraphs: List of paragraphs
            options: Processing configuration options

        Returns:
            List of paragraphs with short ones merged
        """
        merged = []
        i = 0

        while i < len(paragraphs):
            current = paragraphs[i]

            # Check if paragraph is too short and there's a next paragraph
            if (len(current) < options.min_paragraph_length * 2 and
                i + 1 < len(paragraphs)):

                # Merge with next paragraph
                merged.append(f"{current} {paragraphs[i + 1]}")
                i += 2
            else:
                merged.append(current)
                i += 1

        return merged

    def _split_long_paragraphs(
        self,
        paragraphs: List[str],
        options: ProcessingOptions
    ) -> List[str]:
        """
        Split very long paragraphs.

        Args:
            paragraphs: List of paragraphs
            options: Processing configuration options

        Returns:
            List of paragraphs with long ones split
        """
        split_paragraphs = []

        for paragraph in paragraphs:
            if len(paragraph) > options.max_paragraph_length:
                # Split at sentence boundaries
                sentences = re.split(r'(?<=[.!?])\s+', paragraph)
                current_chunk = ""

                for sentence in sentences:
                    if len(current_chunk + " " + sentence) <= options.max_paragraph_length:
                        current_chunk = f"{current_chunk} {sentence}".strip() if current_chunk else sentence
                    else:
                        if current_chunk:
                            split_paragraphs.append(current_chunk)
                        current_chunk = sentence

                if current_chunk:
                    split_paragraphs.append(current_chunk)
            else:
                split_paragraphs.append(paragraph)

        return split_paragraphs

    def estimate_processing_time(self, content_length: int, options: ProcessingOptions) -> float:
        """
        Estimate processing time for paragraph reconstruction.

        Args:
            content_length: Length of content to process
            options: Processing configuration options

        Returns:
            Estimated processing time in seconds
        """
        # Paragraph reconstruction is moderately fast: 0.001 seconds per character
        return content_length * 0.001

    def get_memory_usage_estimate(self, content_length: int) -> int:
        """
        Estimate memory usage for paragraph reconstruction.

        Args:
            content_length: Length of content to process

        Returns:
            Estimated memory usage in bytes
        """
        # Medium memory usage: 3x content size
        return content_length * 3
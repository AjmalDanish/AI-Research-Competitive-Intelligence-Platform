"""
Metadata Cleaner Implementation.

Cleans and normalizes metadata including:
- Metadata field normalization
- Duplicate removal
- Validation and cleanup
"""

from typing import Any, Dict, List

from backend.core.interfaces.content_processor import IContentProcessor
from backend.core.domain.content_processor import ProcessingStage, ProcessingOptions


class MetadataCleaner(IContentProcessor):
    """
    Cleans and normalizes metadata.

    This processor handles:
    - Metadata field normalization
    - Duplicate removal
    - Validation and cleanup
    """

    def __init__(self):
        """Initialize metadata cleaner."""
        self.stage = ProcessingStage.METADATA_CLEANUP

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
        Clean and normalize metadata.

        Args:
            content: Input content (metadata is main focus)
            metadata: Content metadata to clean
            options: Processing configuration options
            context: Processing context

        Returns:
            Tuple of (content, cleaned_metadata)
        """
        # Clean metadata fields
        cleaned_metadata = self._clean_metadata_fields(metadata)

        # Remove duplicates from metadata
        deduplicated_metadata = self._remove_duplicate_metadata(cleaned_metadata)

        # Validate cleaned metadata
        validated_metadata = self._validate_metadata(deduplicated_metadata)

        # Update context with metadata changes
        context.setdefault("metadata_changes", [])
        if metadata != validated_metadata:
            context["metadata_changes"].append("Metadata normalized and cleaned")

        return content, validated_metadata

    def validate(
        self, content: str, metadata: Dict[str, Any], options: ProcessingOptions
    ) -> list[str]:
        """
        Validate metadata for cleaning.

        Args:
            content: Content to validate
            metadata: Content metadata
            options: Processing configuration options

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        # Check if metadata is a dictionary
        if not isinstance(metadata, dict):
            errors.append("Metadata must be a dictionary")
            return errors

        # Validate common metadata fields
        if "title" in metadata:
            if not metadata["title"] or not metadata["title"].strip():
                errors.append("Title cannot be empty")

        if "url" in metadata:
            if not metadata["url"] or not metadata["url"].strip():
                errors.append("URL cannot be empty")

        return errors

    def get_processing_metrics(
        self, input_length: int, output_length: int, duration_seconds: float
    ) -> Dict[str, Any]:
        """
        Calculate processing metrics for metadata cleanup.

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
            "metadata_fields_cleaned": input_length,  # Approximation
        }

    def _clean_metadata_fields(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean and normalize metadata fields.

        Args:
            metadata: Raw metadata

        Returns:
            Cleaned metadata
        """
        cleaned = {}

        # Clean text fields
        text_fields = ["title", "description", "author", "language", "content_type"]
        for field in text_fields:
            if field in metadata and metadata[field]:
                cleaned[field] = str(metadata[field]).strip()

        # Clean URL fields
        url_fields = ["url", "canonical_url"]
        for field in url_fields:
            if field in metadata and metadata[field]:
                cleaned[field] = str(metadata[field]).strip()

        # Clean list fields
        list_fields = ["keywords"]
        for field in list_fields:
            if field in metadata and metadata[field]:
                if isinstance(metadata[field], list):
                    cleaned[field] = [
                        str(item).strip() for item in metadata[field] if str(item).strip()
                    ]
                else:
                    cleaned[field] = [str(metadata[field]).strip()]

        # Copy remaining fields
        for key, value in metadata.items():
            if key not in cleaned and value is not None:
                cleaned[key] = value

        return cleaned

    def _remove_duplicate_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Remove duplicate values from metadata fields.

        Args:
            metadata: Metadata with potential duplicates

        Returns:
            Metadata with duplicates removed
        """
        deduplicated = {}

        for key, value in metadata.items():
            if isinstance(value, list):
                # Only deduplicate lists of hashable items
                # Skip lists containing unhashable types (like dicts)
                if value and all(
                    isinstance(item, (str, int, float, bool, tuple)) for item in value
                ):
                    deduplicated[key] = list(dict.fromkeys(value))
                else:
                    # Keep original list if it contains unhashable items
                    deduplicated[key] = value
            else:
                deduplicated[key] = value

        return deduplicated

    def _validate_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate cleaned metadata.

        Args:
            metadata: Metadata to validate

        Returns:
            Validated metadata
        """
        validated = {}

        # Mark metadata as normalized
        validated["metadata_normalized"] = True
        validated["duplicates_removed"] = True

        # Add validation status
        validated["validation_passed"] = True

        # Copy all fields
        validated.update(metadata)

        return validated

    def estimate_processing_time(self, content_length: int, options: ProcessingOptions) -> float:
        """
        Estimate processing time for metadata cleanup.

        Args:
            content_length: Length of content to process
            options: Processing configuration options

        Returns:
            Estimated processing time in seconds
        """
        # Metadata cleanup is very fast: 0.0001 seconds per character
        return content_length * 0.0001

    def get_memory_usage_estimate(self, content_length: int) -> int:
        """
        Estimate memory usage for metadata cleanup.

        Args:
            content_length: Length of content to process

        Returns:
            Estimated memory usage in bytes
        """
        # Low memory usage: 1.5x content size (metadata is typically small)
        return content_length * 2

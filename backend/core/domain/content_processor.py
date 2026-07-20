"""
Content Processor Domain Models.

This module defines all domain models used in the content processing pipeline.
These models represent the structure and metadata of processed content.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum


class ProcessingStage(Enum):
    """Processing stages in the content processing pipeline."""

    WHITESPACE_NORMALIZATION = "whitespace_normalization"
    UNICODE_NORMALIZATION = "unicode_normalization"
    HTML_ENTITY_DECODING = "html_entity_decoding"
    BOILERPLATE_REMOVAL = "boilerplate_removal"
    NAVIGATION_FOOTER_REMOVAL = "navigation_footer_removal"
    DUPLICATE_DETECTION = "duplicate_detection"
    PARAGRAPH_RECONSTRUCTION = "paragraph_reconstruction"
    HEADING_ASSOCIATION = "heading_association"
    READING_ORDER_RECONSTRUCTION = "reading_order_reconstruction"
    METADATA_CLEANUP = "metadata_cleanup"
    VALIDATION = "validation"


@dataclass
class ProcessingOptions:
    """Configuration options for content processing."""

    enable_whitespace_normalization: bool = True
    enable_unicode_normalization: bool = True
    enable_html_entity_decoding: bool = True
    enable_boilerplate_removal: bool = True
    enable_navigation_footer_removal: bool = True
    enable_duplicate_detection: bool = True
    enable_paragraph_reconstruction: bool = True
    enable_heading_association: bool = True
    enable_reading_order_reconstruction: bool = True
    enable_metadata_cleanup: bool = True
    enable_validation: bool = True

    # Whitespace normalization options
    normalize_newlines: bool = True
    collapse_multiple_spaces: bool = True
    trim_whitespace: bool = True

    # Unicode normalization options
    unicode_form: str = "NFC"  # NFC, NFD, NFKC, NFKD
    normalize_quotes: bool = True
    normalize_dashes: bool = True

    # Boilerplate removal options
    remove_comments: bool = True
    remove_advertisements: bool = True
    remove_social_media_widgets: bool = True

    # Navigation/footer removal options
    remove_navigation_menus: bool = True
    remove_footers: bool = True
    remove_sidebars: bool = True

    # Duplicate detection options
    min_duplicate_length: int = 50
    similarity_threshold: float = 0.9

    # Paragraph reconstruction options
    min_paragraph_length: int = 10
    max_paragraph_length: int = 2000

    # Heading association options
    max_heading_distance: int = 5

    # Reading order reconstruction options
    respect_html_structure: bool = True
    fallback_to_visual_order: bool = False

    # Validation options
    strict_validation: bool = True
    allow_empty_content: bool = False
    minimum_content_length: int = 100

    # Performance options
    timeout_seconds: int = 30
    max_content_length: int = 10_000_000


@dataclass
class ProcessingStageResult:
    """Result of a single processing stage."""

    stage: ProcessingStage
    success: bool
    duration_seconds: float
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProcessingMetrics:
    """Performance and quality metrics for content processing."""

    total_processing_duration_seconds: float = 0.0
    input_content_length: int = 0
    output_content_length: int = 0
    content_compression_ratio: float = 0.0

    # Stage metrics
    stage_results: List[ProcessingStageResult] = field(default_factory=list)

    # Content metrics
    whitespace_normalized_count: int = 0
    unicode_normalized_count: int = 0
    html_entities_decoded: int = 0
    boilerplate_sections_removed: int = 0
    navigation_sections_removed: int = 0
    duplicates_removed: int = 0
    paragraphs_reconstructed: int = 0
    headings_associated: int = 0
    reading_order_segments: int = 0

    # Validation metrics
    validation_errors: List[str] = field(default_factory=list)
    validation_warnings: List[str] = field(default_factory=list)
    validation_passed: bool = True

    # Performance metrics
    memory_usage_bytes: int = 0
    cpu_usage_percent: float = 0.0

    def add_stage_result(self, result: ProcessingStageResult) -> None:
        """Add a processing stage result."""
        self.stage_results.append(result)
        self.total_processing_duration_seconds += result.duration_seconds


@dataclass
class TextSegment:
    """A segment of text with associated metadata."""

    text: str
    segment_type: str  # "paragraph", "heading", "list", "code", "quote"
    position: int
    start_index: int
    end_index: int
    level: Optional[int] = None  # For headings (1-6)

    # Additional metadata
    is_duplicate: bool = False
    is_boilerplate: bool = False
    is_navigation: bool = False
    is_footer: bool = False

    # Parent-child relationships
    parent_heading: Optional[int] = None  # Position of parent heading
    children_segments: List[int] = field(default_factory=list)  # Positions of child segments

    # Quality metrics
    word_count: int = 0
    sentence_count: int = 0
    character_count: int = 0
    average_word_length: float = 0.0


@dataclass
class ContentSection:
    """A logical section of content with related text segments."""

    section_id: str
    heading: Optional[TextSegment]
    segments: List[TextSegment]
    position: int
    section_type: str = "content"  # "content", "navigation", "footer", "boilerplate"

    # Section metadata
    word_count: int = 0
    sentence_count: int = 0
    estimated_reading_time_minutes: float = 0.0

    def calculate_metrics(self) -> None:
        """Calculate section metrics from segments."""
        self.word_count = sum(seg.word_count for seg in self.segments)
        self.sentence_count = sum(seg.sentence_count for seg in self.segments)
        # Average reading time: ~200 words per minute
        self.estimated_reading_time_minutes = self.word_count / 200.0


@dataclass
class NormalizedText:
    """Normalized and processed text content."""

    original_text: str
    normalized_text: str

    # Text statistics
    original_word_count: int = 0
    normalized_word_count: int = 0
    word_reduction: int = 0
    word_reduction_percentage: float = 0.0

    # Character statistics
    original_char_count: int = 0
    normalized_char_count: int = 0
    char_reduction: int = 0
    char_reduction_percentage: float = 0.0

    # Text quality indicators
    whitespace_normalized: bool = False
    unicode_normalized: bool = False
    html_entities_decoded: bool = False
    duplicates_removed: bool = False
    boilerplate_removed: bool = False

    # Validation status
    is_valid: bool = True
    validation_errors: List[str] = field(default_factory=list)

    def calculate_statistics(self) -> None:
        """Calculate text statistics."""
        # Word counts
        self.original_word_count = len(self.original_text.split())
        self.normalized_word_count = len(self.normalized_text.split())
        self.word_reduction = self.original_word_count - self.normalized_word_count

        if self.original_word_count > 0:
            self.word_reduction_percentage = (self.word_reduction / self.original_word_count) * 100

        # Character counts
        self.original_char_count = len(self.original_text)
        self.normalized_char_count = len(self.normalized_text)
        self.char_reduction = self.original_char_count - self.normalized_char_count

        if self.original_char_count > 0:
            self.char_reduction_percentage = (self.char_reduction / self.original_char_count) * 100


@dataclass
class ContentMetadata:
    """Cleaned and normalized metadata."""

    title: str
    description: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    author: Optional[str] = None
    publish_date: Optional[datetime] = None
    language: Optional[str] = None
    content_type: Optional[str] = None
    canonical_url: Optional[str] = None

    # Open Graph data
    og_title: Optional[str] = None
    og_description: Optional[str] = None
    og_image: Optional[str] = None
    og_type: Optional[str] = None

    # Twitter Card data
    twitter_title: Optional[str] = None
    twitter_description: Optional[str] = None
    twitter_image: Optional[str] = None
    twitter_card_type: Optional[str] = None

    # Processing metadata
    metadata_normalized: bool = False
    duplicates_removed: bool = False
    validation_passed: bool = True

    def normalize(self) -> "ContentMetadata":
        """Normalize metadata fields."""
        # Normalize title
        self.title = self.title.strip()

        # Normalize description
        if self.description:
            self.description = self.description.strip()

        # Normalize keywords
        self.keywords = [kw.strip() for kw in self.keywords if kw.strip()]

        # Normalize language codes
        if self.language:
            self.language = self.language.lower().strip()

        # Mark as normalized
        self.metadata_normalized = True

        return self


@dataclass
class ProcessingResult:
    """Complete result of content processing pipeline."""

    # Source information
    source_url: str
    original_content: str

    # Processed content
    normalized_text: NormalizedText
    content_sections: List[ContentSection]
    text_segments: List[TextSegment]
    metadata: ContentMetadata

    # Processing metrics
    metrics: ProcessingMetrics

    # Processing status
    processing_complete: bool = True
    processing_errors: List[str] = field(default_factory=list)
    processing_warnings: List[str] = field(default_factory=list)

    # Quality indicators
    content_quality_score: float = 0.0
    determinism_score: float = 1.0  # Should always be 1.0 for deterministic processing

    # Timestamps
    processing_started: Optional[datetime] = None
    processing_completed: Optional[datetime] = None

    def calculate_quality_score(self) -> float:
        """Calculate overall content quality score."""
        score = 1.0

        # Penalize validation errors
        if self.metrics.validation_errors:
            error_penalty = min(0.5, len(self.metrics.validation_errors) * 0.1)
            score -= error_penalty

        # Penalize warnings
        if self.metrics.validation_warnings:
            warning_penalty = min(0.2, len(self.metrics.validation_warnings) * 0.05)
            score -= warning_penalty

        # Bonus for content quality
        if self.normalized_text.normalized_word_count > 100:
            score += 0.1

        if self.normalized_text.is_valid:
            score += 0.1

        # Ensure score is in valid range
        self.content_quality_score = max(0.0, min(1.0, score))

        return self.content_quality_score

    def get_effective_content(self) -> str:
        """Get the effective content after processing."""
        # Return only non-boilerplate, non-navigation content
        effective_segments = [
            seg
            for seg in self.text_segments
            if not seg.is_boilerplate and not seg.is_navigation and not seg.is_footer
        ]
        return " ".join(seg.text for seg in effective_segments)

    def get_content_by_section_type(self, section_type: str) -> List[ContentSection]:
        """Get content sections by type."""
        return [
            section for section in self.content_sections if section.section_type == section_type
        ]

    def get_reading_order_text(self) -> str:
        """Get text in proper reading order."""
        sections = self.get_content_by_section_type("content")
        ordered_sections = sorted(sections, key=lambda x: x.position)
        return " ".join(
            " ".join(seg.text for seg in section.segments) for section in ordered_sections
        )

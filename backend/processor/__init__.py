"""
Content Processor module.

This module provides content processing capabilities for the AI Website Intelligence Platform.
It transforms ParserResult into clean, normalized, structured content.

Components:
- ProcessingService: Orchestration layer for content processing
- Individual processors: Independent processing stages
- Domain models: ProcessingResult, ProcessingMetrics, ContentSection, NormalizedText, ProcessingOptions

Open/Closed Principle: New processors can be added without modifying existing code.
"""

from backend.processor.processor_service import ProcessingService
from backend.processor.exceptions import (
    ProcessorError,
    ProcessorNotAvailableError,
    ProcessingTimeoutError,
    ProcessingValidationError,
)

# Import available processor implementations
from backend.processor.implementations.whitespace_normalizer import WhitespaceNormalizer
from backend.processor.implementations.unicode_normalizer import UnicodeNormalizer
from backend.processor.implementations.html_entity_decoder import HTMLEntityDecoder
from backend.processor.implementations.boilerplate_remover import BoilerplateRemover
from backend.processor.implementations.navigation_remover import NavigationRemover
from backend.processor.implementations.duplicate_detector import DuplicateDetector
from backend.processor.implementations.paragraph_reconstructor import ParagraphReconstructor
from backend.processor.implementations.heading_associator import HeadingAssociator
from backend.processor.implementations.reading_order_reconstructor import ReadingOrderReconstructor
from backend.processor.implementations.metadata_cleaner import MetadataCleaner
from backend.processor.implementations.content_validator import ContentValidator

# Domain models
from backend.core.domain.content_processor import (
    ProcessingResult,
    ProcessingMetrics,
    ContentSection,
    NormalizedText,
    ProcessingOptions,
    ProcessingStage,
    TextSegment,
    ContentMetadata,
)

# Core interface
from backend.core.interfaces.content_processor import IContentProcessor

__all__ = [
    # Service
    "ProcessingService",

    # Exceptions
    "ProcessorError",
    "ProcessorNotAvailableError",
    "ProcessingTimeoutError",
    "ProcessingValidationError",

    # Processor implementations
    "WhitespaceNormalizer",
    "UnicodeNormalizer",
    "HTMLEntityDecoder",
    "BoilerplateRemover",
    "NavigationRemover",
    "DuplicateDetector",
    "ParagraphReconstructor",
    "HeadingAssociator",
    "ReadingOrderReconstructor",
    "MetadataCleaner",
    "ContentValidator",

    # Domain models
    "ProcessingResult",
    "ProcessingMetrics",
    "ContentSection",
    "NormalizedText",
    "ProcessingOptions",
    "ProcessingStage",
    "TextSegment",
    "ContentMetadata",

    # Core interface
    "IContentProcessor",
]
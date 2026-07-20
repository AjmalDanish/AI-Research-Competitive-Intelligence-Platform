"""
Content Processor Implementations.

This module exports all available content processor implementations.
Following Open/Closed Principle: new processors can be added
without modifying existing code.
"""

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

__all__ = [
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
]
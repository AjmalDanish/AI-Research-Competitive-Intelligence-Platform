"""
Information Extraction Module.

This module provides deterministic, evidence-based information extraction
from processed content. It serves as the canonical knowledge layer for
future AI modules.
"""

from backend.extractor.extractor_service import ExtractionService
from backend.extractor.registry import ExtractionRegistry
from backend.extractor.rule_loader import RuleLoader

__all__ = [
    "ExtractionService",
    "ExtractionRegistry",
    "RuleLoader",
]

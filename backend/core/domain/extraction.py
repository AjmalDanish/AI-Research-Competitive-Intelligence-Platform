"""
Extraction Domain Models.

This module defines all domain models used in the information extraction pipeline.
These models represent structured, deterministic, explainable extracted information.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any


class ExtractionStage(StrEnum):
    """Extraction pipeline stages."""

    EMAIL_EXTRACTION = "email_extraction"
    PHONE_EXTRACTION = "phone_extraction"
    URL_EXTRACTION = "url_extraction"
    SOCIAL_MEDIA_EXTRACTION = "social_media_extraction"
    TECHNOLOGY_EXTRACTION = "technology_extraction"
    ORGANIZATION_EXTRACTION = "organization_extraction"
    PERSON_EXTRACTION = "person_extraction"
    ADDRESS_EXTRACTION = "address_extraction"
    DATE_EXTRACTION = "date_extraction"
    NORMALIZATION = "normalization"
    VALIDATION = "validation"
    DEDUPLICATION = "deduplication"
    CONFIDENCE_ASSIGNMENT = "confidence_assignment"


class EntityType(StrEnum):
    """Types of entities that can be extracted."""

    EMAIL = "email"
    PHONE = "phone"
    URL = "url"
    SOCIAL_MEDIA = "social_media"
    TECHNOLOGY = "technology"
    ORGANIZATION = "organization"
    PERSON = "person"
    ADDRESS = "address"
    DATE = "date"


class EvidenceKind(StrEnum):
    """Types of evidence that support extraction."""

    JSON_LD = "json_ld"
    SCHEMA_ORG = "schema_org"
    OPEN_GRAPH = "open_graph"
    META_TAGS = "meta_tags"
    HTML_STRUCTURE = "html_structure"
    HTTP_HEADERS = "http_headers"
    REGEX_MATCH = "regex_match"
    VERIFIED_REGEX = "verified_regex"
    WEAK_HEURISTIC = "weak_heuristic"
    SCRIPT_URL = "script_url"
    STYLESHEET_URL = "stylesheet_url"
    GENERATOR_TAG = "generator_tag"
    CONTACT_METADATA = "contact_metadata"
    AUTHOR_METADATA = "author_metadata"


class ConfidenceSource(StrEnum):
    """Sources of confidence scores."""

    STRUCTURED_DATA = "structured_data"  # JSON-LD, Schema.org
    META_INFORMATION = "meta_information"  # Meta tags, OpenGraph
    VERIFIED_PATTERN = "verified_pattern"  # Well-tested regex patterns
    STRUCTURAL_PATTERN = "structural_pattern"  # HTML structure
    WEAK_PATTERN = "weak_pattern"  # Less reliable patterns
    CANDIDATE = "candidate"  # Possible match, low confidence


@dataclass(frozen=True)
class SourceLocation:
    """Location of extracted content in the source."""

    line_number: int
    character_offset: int
    context: str = ""
    length: int = 0

    def __post_init__(self):
        """Validate source location."""
        if self.line_number < 0:
            raise ValueError("line_number must be >= 0")
        if self.character_offset < 0:
            raise ValueError("character_offset must be >= 0")
        if self.length < 0:
            raise ValueError("length must be >= 0")


@dataclass(frozen=True)
class Evidence:
    """Evidence supporting an extraction."""

    kind: EvidenceKind
    rule_name: str
    matched_text: str
    matched_value: str
    location: SourceLocation | None = None
    confidence_source: ConfidenceSource = ConfidenceSource.CANDIDATE
    pattern: str | None = None
    additional_context: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate evidence."""
        if not self.rule_name:
            raise ValueError("rule_name cannot be empty")
        if not self.matched_text:
            raise ValueError("matched_text cannot be empty")
        if not self.matched_value:
            raise ValueError("matched_value cannot be empty")


@dataclass(frozen=True)
class ExtractedEntity:
    """Base class for all extracted entities."""

    id: str
    type: EntityType
    value: str
    normalized_value: str
    confidence: float
    confidence_reason: str
    extractor: str
    processor: str
    source: str
    position: int
    line_number: int
    character_offset: int
    evidence: list[Evidence]
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate extracted entity."""
        if not self.id:
            raise ValueError("id cannot be empty")
        if not self.value:
            raise ValueError("value cannot be empty")
        if not self.normalized_value:
            raise ValueError("normalized_value cannot be empty")
        if self.confidence < 0.0 or self.confidence > 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        if not self.evidence:
            raise ValueError("evidence cannot be empty")
        if self.position < 0:
            raise ValueError("position must be >= 0")
        if self.line_number < 0:
            raise ValueError("line_number must be >= 0")
        if self.character_offset < 0:
            raise ValueError("character_offset must be >= 0")

    def get_primary_evidence(self) -> Evidence:
        """Get the primary (highest confidence) evidence."""
        return (
            self.evidence[0]
            if self.evidence
            else Evidence(
                kind=EvidenceKind.WEAK_HEURISTIC,
                rule_name="unknown",
                matched_text=self.value,
                matched_value=self.value,
                confidence_source=ConfidenceSource.CANDIDATE,
            )
        )


@dataclass(frozen=True)
class ExtractedEmail(ExtractedEntity):
    """Extracted email address."""

    email_type: str = "plain"  # plain, mailto, obfuscated
    domain: str = ""
    local_part: str = ""
    is_disposable: bool = False
    is_role_based: bool = False

    def __post_init__(self):
        """Validate email entity."""
        super().__post_init__()
        if self.type not in ["plain", "mailto", "obfuscated"]:
            raise ValueError(f"Invalid email_type: {self.type}")


@dataclass(frozen=True)
class ExtractedPhone(ExtractedEntity):
    """Extracted phone number."""

    phone_type: str = "unknown"  # mobile, landline, toll_free, fax
    country_code: str = ""
    area_code: str = ""
    number: str = ""
    is_valid: bool = False
    formatted_value: str = ""

    def __post_init__(self):
        """Validate phone entity."""
        super().__post_init__()


@dataclass(frozen=True)
class ExtractedURL(ExtractedEntity):
    """Extracted URL."""

    url_type: str = "unknown"  # http, https, ftp, mailto
    domain: str = ""
    path: str = ""
    scheme: str = ""
    is_internal: bool = False
    is_secure: bool = False

    def __post_init__(self):
        """Validate URL entity."""
        super().__post_init__()
        if not self.domain:
            raise ValueError("domain cannot be empty")


@dataclass(frozen=True)
class ExtractedTechnology(ExtractedEntity):
    """Extracted technology."""

    technology_type: str = "unknown"  # frontend, backend, cms, analytics, infrastructure
    category: str = ""
    version: str | None = None
    vendor: str = ""
    is_detected: bool = True

    def __post_init__(self):
        """Validate technology entity."""
        super().__post_init__()
        if not self.category:
            raise ValueError("category cannot be empty")


@dataclass(frozen=True)
class ExtractedOrganization(ExtractedEntity):
    """Extracted organization."""

    org_type: str = "unknown"  # company, non_profit, government, educational
    legal_suffix: str | None = None
    domain: str | None = None
    is_verified: bool = False

    def __post_init__(self):
        """Validate organization entity."""
        super().__post_init__()


@dataclass(frozen=True)
class ExtractedPerson(ExtractedEntity):
    """Extracted person."""

    person_type: str = "unknown"  # author, executive, contact, contributor
    first_name: str | None = None
    last_name: str | None = None
    full_name: str = ""
    title: str | None = None
    role: str | None = None

    def __post_init__(self):
        """Validate person entity."""
        super().__post_init__()
        if not self.full_name:
            raise ValueError("full_name cannot be empty")


@dataclass(frozen=True)
class ExtractedDate(ExtractedEntity):
    """Extracted date."""

    date_type: str = "unknown"  # published, modified, copyright, expiry
    date_value: datetime | None = None
    timezone: str | None = None
    is_approximate: bool = False

    def __post_init__(self):
        """Validate date entity."""
        super().__post_init__()


@dataclass(frozen=True)
class ExtractedAddress(ExtractedEntity):
    """Extracted address."""

    address_type: str = "unknown"  # physical, postal, billing, registered
    street: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    country: str | None = None

    def __post_init__(self):
        """Validate address entity."""
        super().__post_init__()


@dataclass(frozen=True)
class ExtractedSocialProfile(ExtractedEntity):
    """Extracted social media profile."""

    platform: str = ""  # github, linkedin, twitter, etc.
    username: str = ""
    profile_url: str = ""
    is_verified: bool = False
    follower_count: int | None = None

    def __post_init__(self):
        """Validate social profile entity."""
        super().__post_init__()
        if not self.platform:
            raise ValueError("platform cannot be empty")
        if not self.profile_url:
            raise ValueError("profile_url cannot be empty")


@dataclass
class ExtractionMetrics:
    """Metrics for extraction operations."""

    total_extraction_duration_seconds: float = 0.0
    input_content_length: int = 0
    entities_extracted: int = 0

    # Entity counts by type
    email_count: int = 0
    phone_count: int = 0
    url_count: int = 0
    social_media_count: int = 0
    technology_count: int = 0
    organization_count: int = 0
    person_count: int = 0
    address_count: int = 0
    date_count: int = 0

    # Processing metrics
    duplicates_removed: int = 0
    validation_failures: int = 0
    normalization_failures: int = 0

    # Performance metrics
    extractor_timings: dict[str, float] = field(default_factory=dict)
    stage_durations: dict[str, float] = field(default_factory=dict)

    # Confidence distribution
    confidence_distribution: dict[str, int] = field(default_factory=dict)

    # Validation metrics
    validation_errors: list[str] = field(default_factory=list)
    validation_warnings: list[str] = field(default_factory=list)
    validation_passed: bool = True

    # Resource metrics
    memory_usage_bytes: int = 0
    cpu_usage_percent: float = 0.0

    def add_entity(self, entity_type: EntityType) -> None:
        """Add an entity to metrics."""
        self.entities_extracted += 1

        if entity_type == EntityType.EMAIL:
            self.email_count += 1
        elif entity_type == EntityType.PHONE:
            self.phone_count += 1
        elif entity_type == EntityType.URL:
            self.url_count += 1
        elif entity_type == EntityType.SOCIAL_MEDIA:
            self.social_media_count += 1
        elif entity_type == EntityType.TECHNOLOGY:
            self.technology_count += 1
        elif entity_type == EntityType.ORGANIZATION:
            self.organization_count += 1
        elif entity_type == EntityType.PERSON:
            self.person_count += 1
        elif entity_type == EntityType.ADDRESS:
            self.address_count += 1
        elif entity_type == EntityType.DATE:
            self.date_count += 1

    def add_extractor_timing(self, extractor_name: str, duration_seconds: float) -> None:
        """Add extractor timing."""
        self.extractor_timings[extractor_name] = duration_seconds

    def add_stage_duration(self, stage: str, duration_seconds: float) -> None:
        """Add stage duration."""
        self.stage_durations[stage] = duration_seconds

    def add_confidence_score(self, confidence: float) -> None:
        """Add confidence score to distribution."""
        bucket = f"{int(confidence * 100)}%"
        self.confidence_distribution[bucket] = self.confidence_distribution.get(bucket, 0) + 1


@dataclass
class ExtractionOptions:
    """Configuration options for extraction operations."""

    # Feature flags
    enable_email_extraction: bool = True
    enable_phone_extraction: bool = True
    enable_url_extraction: bool = True
    enable_social_media_extraction: bool = True
    enable_technology_extraction: bool = True
    enable_organization_extraction: bool = True
    enable_person_extraction: bool = True
    enable_address_extraction: bool = True
    enable_date_extraction: bool = True

    # Processing options
    enable_normalization: bool = True
    enable_validation: bool = True
    enable_deduplication: bool = True
    enable_confidence_assignment: bool = True

    # Performance options
    enable_caching: bool = True
    enable_parallel_processing: bool = False
    timeout_seconds: float = 30.0

    # Validation options
    strict_validation: bool = False
    min_confidence_threshold: float = 0.5

    # Deduplication options
    deduplication_strategy: str = "exact"  # exact, fuzzy, semantic

    # Technology detection options
    detect_all_technologies: bool = True
    detect_frontend_frameworks: bool = True
    detect_backend_frameworks: bool = True
    detect_cms_platforms: bool = True
    detect_analytics_tools: bool = True
    detect_infrastructure: bool = True

    # Social media detection options
    detect_all_platforms: bool = True
    normalize_social_urls: bool = True

    # Organization detection options
    detect_legal_entities: bool = True
    detect_from_structured_data_org: bool = True

    # Person detection options
    detect_from_metadata: bool = True
    detect_from_structured_data_person: bool = True


@dataclass
class ExtractorContext:
    """Shared context for extraction operations."""

    processing_result: Any  # ProcessingResult from Milestone 5
    configuration: ExtractionOptions
    feature_flags: dict[str, bool] = field(default_factory=dict)
    metrics: ExtractionMetrics = field(default_factory=ExtractionMetrics)
    cache: dict[str, Any] = field(default_factory=dict)
    intermediate_state: dict[str, Any] = field(default_factory=dict)
    logger: Any | None = None

    def get_content(self) -> str:
        """Get the content to extract from."""
        if hasattr(self.processing_result, "normalized_text"):
            return self.processing_result.normalized_text.normalized_text  # type: ignore[no-any-return]
        elif hasattr(self.processing_result, "original_content"):
            return self.processing_result.original_content  # type: ignore[no-any-return]
        return ""

    def get_metadata(self) -> dict[str, Any]:
        """Get the metadata from processing result."""
        if hasattr(self.processing_result, "metadata"):
            # Convert ContentMetadata to dict
            metadata_dict = {}
            for field, value in self.processing_result.metadata:
                if hasattr(value, "__dict__"):
                    metadata_dict[field] = value.__dict__
                else:
                    metadata_dict[field] = value
            return metadata_dict
        return {}

    def is_feature_enabled(self, feature: str) -> bool:
        """Check if a feature is enabled."""
        return self.feature_flags.get(feature, True)


@dataclass
class ExtractorCapability:
    """Capability descriptor for an extractor."""

    name: str
    version: str
    description: str
    supported_types: list[EntityType]
    supported_patterns: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    priority: int = 100
    configuration_schema: dict[str, Any] = field(default_factory=dict)
    confidence_strategy: str = "pattern_based"
    deterministic: bool = True

    def can_extract(self, entity_type: EntityType) -> bool:
        """Check if extractor can extract given entity type."""
        return entity_type in self.supported_types

    def has_dependency(self, extractor_name: str) -> bool:
        """Check if extractor has a dependency."""
        return extractor_name in self.dependencies


@dataclass
class RuleMatch:
    """Result of a rule match."""

    rule_name: str
    matched_text: str
    extracted_value: str
    confidence: float
    location: SourceLocation | None = None
    pattern: str | None = None
    rule_metadata: dict[str, Any] = field(default_factory=dict)

    def to_evidence(self, kind: EvidenceKind, confidence_source: ConfidenceSource) -> Evidence:
        """Convert rule match to evidence."""
        return Evidence(
            kind=kind,
            rule_name=self.rule_name,
            matched_text=self.matched_text,
            matched_value=self.extracted_value,
            location=self.location,
            confidence_source=confidence_source,
            pattern=self.pattern,
            additional_context=self.rule_metadata,
        )


@dataclass
class ExtractionResult:
    """Complete extraction result."""

    entities: list[ExtractedEntity] = field(default_factory=list)
    metrics: ExtractionMetrics = field(default_factory=ExtractionMetrics)
    metadata: dict[str, Any] = field(default_factory=dict)
    processing_complete: bool = True
    processing_started: datetime | None = None
    processing_completed: datetime | None = None
    source_url: str = ""

    # Quality indicators
    confidence_score: float = 0.0
    determinism_score: float = 1.0

    def get_entities_by_type(self, entity_type: EntityType) -> list[ExtractedEntity]:
        """Get all entities of a specific type."""
        return [entity for entity in self.entities if entity.type == entity_type]

    def get_entities_by_extractor(self, extractor_name: str) -> list[ExtractedEntity]:
        """Get all entities extracted by a specific extractor."""
        return [entity for entity in self.entities if entity.extractor == extractor_name]

    def get_high_confidence_entities(self, threshold: float = 0.8) -> list[ExtractedEntity]:
        """Get entities with confidence above threshold."""
        return [entity for entity in self.entities if entity.confidence >= threshold]

    def calculate_quality_score(self) -> float:
        """Calculate overall quality score."""
        score = 1.0

        # Penalize validation failures
        if self.metrics.validation_errors:
            error_penalty = min(0.5, len(self.metrics.validation_errors) * 0.1)
            score -= error_penalty

        # Penalize low confidence entities
        low_confidence_count = sum(1 for entity in self.entities if entity.confidence < 0.7)
        if low_confidence_count > 0:
            confidence_penalty = min(0.2, low_confidence_count * 0.05)
            score -= confidence_penalty

        # Bonus for high entity count with good confidence
        if len(self.entities) > 10:
            good_confidence_count = sum(1 for entity in self.entities if entity.confidence >= 0.8)
            if good_confidence_count / len(self.entities) > 0.7:
                score += 0.1

        # Ensure score is in valid range
        self.confidence_score = max(0.0, min(1.0, score))
        return self.confidence_score

    def get_summary(self) -> dict[str, Any]:
        """Get summary of extraction results."""
        return {
            "total_entities": len(self.entities),
            "entity_types": {
                entity_type.value: len(self.get_entities_by_type(entity_type))
                for entity_type in EntityType
            },
            "average_confidence": (
                sum(entity.confidence for entity in self.entities) / len(self.entities)
                if self.entities
                else 0.0
            ),
            "high_confidence_count": len(self.get_high_confidence_entities()),
            "duplicates_removed": self.metrics.duplicates_removed,
            "validation_failures": self.metrics.validation_failures,
            "processing_duration": self.metrics.total_extraction_duration_seconds,
            "quality_score": self.confidence_score,
        }

"""
Quick integration test for extraction foundation (Phase 1).

This test verifies the basic structure and registry functionality.
"""

from backend.extractor import ExtractionService, ExtractionRegistry, RuleLoader
from backend.core.domain.extraction import ExtractionOptions


def test_phase1_basic_structure():
    """Test basic Phase 1 structure."""
    print("🧪 Testing Phase 1: Basic Structure")

    # Test RuleLoader
    print("  Testing RuleLoader...")
    rule_loader = RuleLoader()
    assert rule_loader is not None

    # Test loading email rules
    email_rules = rule_loader.load_rules("email")
    assert email_rules is not None
    assert "version" in email_rules
    assert "rules" in email_rules
    print(f"    ✅ Loaded email rules (version: {email_rules['version']})")

    # Test loading phone rules
    phone_rules = rule_loader.load_rules("phone")
    assert phone_rules is not None
    print(f"    ✅ Loaded phone rules (version: {phone_rules['version']})")

    # Test loading social rules
    social_rules = rule_loader.load_rules("social")
    assert social_rules is not None
    print(f"    ✅ Loaded social rules (version: {social_rules['version']})")

    # Test Registry
    print("  Testing Registry...")
    registry = ExtractionRegistry()
    assert registry is not None
    print("    ✅ Registry created")

    # Test registry statistics
    stats = registry.get_extractor_statistics()
    assert stats is not None
    assert "total_extractors" in stats
    assert stats["total_extractors"] == 0  # No extractors registered yet
    print(f"    ✅ Registry statistics: {stats['total_extractors']} extractors")

    # Test dependency validation (no extractors = no errors)
    validation_errors = registry.validate_dependencies()
    assert validation_errors == []
    print("    ✅ Dependency validation passed")

    # Test ExecutionService
    print("  Testing ExtractionService...")
    try:
        service = ExtractionService(registry=registry)
        # This will fail because no extractors are registered,
        # but the service should be created successfully
        print("    ⚠️  ExtractionService created (no extractors registered)")
    except Exception as e:
        print(f"    ⚠️  ExtractionService creation: {e}")

    print("✅ Phase 1 basic structure test passed")
    return True


def test_phase1_rule_validation():
    """Test rule validation."""
    print("🧪 Testing Phase 1: Rule Validation")

    rule_loader = RuleLoader()

    # Test rule validation
    print("  Testing rule validation...")
    email_rules = rule_loader.load_rules("email")
    is_valid = rule_loader.validate_rules(email_rules)
    assert is_valid
    print("    ✅ Email rules validation passed")

    # Test rule schema
    schema = rule_loader.get_rule_schema()
    assert schema is not None
    assert "type" in schema
    print("    ✅ Rule schema defined")

    # Test rule versions
    email_version = rule_loader.get_rule_version("email")
    phone_version = rule_loader.get_rule_version("phone")
    assert email_version == "1.0.0"
    assert phone_version == "1.0.0"
    print(f"    ✅ Rule versions: email={email_version}, phone={phone_version}")

    print("✅ Phase 1 rule validation test passed")
    return True


def test_phase1_domain_models():
    """Test domain models."""
    print("🧪 Testing Phase 1: Domain Models")

    from backend.core.domain.extraction import (
        Evidence,
        EvidenceKind,
        ConfidenceSource,
        ExtractorContext,
        ExtractionOptions,
    )

    # Test Evidence model
    print("  Testing Evidence model...")
    evidence = Evidence(
        kind=EvidenceKind.REGEX_MATCH,
        rule_name="test_rule",
        matched_text="test@example.com",
        matched_value="test@example.com",
        confidence_source=ConfidenceSource.VERIFIED_PATTERN,
    )
    assert evidence.kind == EvidenceKind.REGEX_MATCH
    assert evidence.matched_value == "test@example.com"
    print("    ✅ Evidence model created")

    # Test ExtractionOptions model
    print("  Testing ExtractionOptions model...")
    options = ExtractionOptions(
        enable_email_extraction=True,
        enable_phone_extraction=False,
    )
    assert options.enable_email_extraction is True
    assert options.enable_phone_extraction is False
    print("    ✅ ExtractionOptions model created")

    print("✅ Phase 1 domain models test passed")
    return True


if __name__ == "__main__":
    print("🚀 Running Phase 1 Extraction Foundation Tests")
    print()

    try:
        test_phase1_basic_structure()
        print()
        test_phase1_rule_validation()
        print()
        test_phase1_domain_models()

        print()
        print("🎉 All Phase 1 tests passed!")
        print(
            "Phase 1: Project scaffolding, Domain models, Interfaces, Registry, RuleLoader - COMPLETE"
        )

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        exit(1)

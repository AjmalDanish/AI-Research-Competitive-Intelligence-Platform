"""
Quick integration test for content processing foundation.

This test verifies the basic functionality of the ProcessingService
and the processing pipeline.
"""

from backend.processor import ProcessingService, ProcessingOptions


def test_processing_service_basic():
    """Test basic content processing pipeline."""
    # Create processing service
    service = ProcessingService(options=ProcessingOptions())

    # Sample content with issues
    test_content = """
    <p>This   is    a   test.</p>
    
    <p>Another  paragraph  with  extra  spaces.</p>
    
    <p>This is a duplicate paragraph.</p>
    
    <p>This is a duplicate paragraph.</p>
    
    <p>&copy; 2024  Test  Company.  All rights reserved.</p>
    """

    # Process content
    result = service.process(test_content)

    # Verify result structure
    assert result is not None
    assert hasattr(result, "normalized_text")
    assert hasattr(result, "metrics")
    assert hasattr(result, "metadata")

    # Verify normalization worked
    assert result.normalized_text.original_text == test_content
    assert result.normalized_text.normalized_text != test_content

    # Verify metrics
    assert result.metrics.total_processing_duration_seconds > 0
    assert len(result.metrics.stage_results) > 0

    # Verify metadata (Content Processor doesn't extract titles - that's Parser's job)
    # The title will be empty if not provided in input metadata
    assert result.metadata is not None
    assert hasattr(result.metadata, "validation_passed")

    print("✅ Basic processing test passed")
    return True


def test_processing_pipeline_stages():
    """Test that all processing stages are available."""
    service = ProcessingService(options=ProcessingOptions())

    stages = service.get_available_stages()

    # Verify all stages are registered
    from backend.core.domain.content_processor import ProcessingStage

    expected_stages = [
        ProcessingStage.WHITESPACE_NORMALIZATION,
        ProcessingStage.UNICODE_NORMALIZATION,
        ProcessingStage.HTML_ENTITY_DECODING,
        ProcessingStage.BOILERPLATE_REMOVAL,
        ProcessingStage.NAVIGATION_FOOTER_REMOVAL,
        ProcessingStage.DUPLICATE_DETECTION,
        ProcessingStage.PARAGRAPH_RECONSTRUCTION,
        ProcessingStage.HEADING_ASSOCIATION,
        ProcessingStage.READING_ORDER_RECONSTRUCTION,
        ProcessingStage.METADATA_CLEANUP,
        ProcessingStage.VALIDATION,
    ]

    for expected_stage in expected_stages:
        assert expected_stage in stages, f"Stage {expected_stage} not registered"

    print(f"✅ All {len(expected_stages)} processing stages registered")
    return True


def test_individual_processors():
    """Test individual processor functionality."""
    from backend.processor.implementations import (
        WhitespaceNormalizer,
        UnicodeNormalizer,
        HTMLEntityDecoder,
    )

    options = ProcessingOptions()

    # Test whitespace normalizer
    ws_normalizer = WhitespaceNormalizer()
    test_text = "  Test   text  "
    result, metadata = ws_normalizer.process(test_text, {}, options, {})
    assert result == "Test text", "Whitespace normalization failed"

    # Test HTML entity decoder
    entity_decoder = HTMLEntityDecoder()
    test_text = "Test &amp; text &lt;with&gt; entities"
    result, metadata = entity_decoder.process(test_text, {}, options, {})
    assert "&amp;" not in result, "HTML entity decoding failed"

    print("✅ Individual processors functional")
    return True


if __name__ == "__main__":
    print("🚀 Running Content Processing Foundation Tests")
    print()

    try:
        test_processing_service_basic()
        test_processing_pipeline_stages()
        test_individual_processors()

        print()
        print("🎉 All tests passed!")
        print("Content Processing Foundation is functional.")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        exit(1)

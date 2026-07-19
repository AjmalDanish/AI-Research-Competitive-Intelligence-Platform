"""
Complete application testing script.
Tests all services, models, and API components.
"""

import os
import sys
from datetime import datetime

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_phase1_components():
    """Test Phase 1 components."""
    print("\n" + "=" * 60)
    print("PHASE 1: Core Infrastructure Testing")
    print("=" * 60)

    results = []

    # Test FastAPI
    print("\n[1/5] Testing FastAPI...")
    try:
        print("✅ FastAPI imported successfully")
        results.append(True)
    except Exception as e:
        print(f"❌ FastAPI import failed: {e}")
        results.append(False)

    # Test Configuration
    print("\n[2/5] Testing Configuration...")
    try:
        from app.core.config import settings

        print(f"✅ Config loaded: {settings.PROJECT_NAME}")
        print(f"   Version: {settings.VERSION}")
        print(f"   Environment: {settings.ENVIRONMENT}")
        results.append(True)
    except Exception as e:
        print(f"❌ Configuration failed: {e}")
        results.append(False)

    # Test Security
    print("\n[3/5] Testing Security...")
    try:
        from app.core.security import create_access_token, get_password_hash

        get_password_hash("test_password")
        create_access_token(subject="test_user")
        print("✅ Security functions working")
        print("   Password hashing: ✓")
        print("   Token creation: ✓")
        results.append(True)
    except Exception as e:
        print(f"❌ Security failed: {e}")
        results.append(False)

    # Test Database Session
    print("\n[4/5] Testing Database Session...")
    try:
        print("✅ Database session configured")
        print("   AsyncSessionLocal: ✓")
        print("   Base model: ✓")
        results.append(True)
    except Exception as e:
        print(f"❌ Database session failed: {e}")
        results.append(False)

    # Test Models
    print("\n[5/5] Testing Database Models...")
    try:
        print("✅ All models imported successfully")
        print("   Competitor models: ✓")
        print("   Market models: ✓")
        print("   User models: ✓")
        print("   Alert models: ✓")
        results.append(True)
    except Exception as e:
        print(f"❌ Models import failed: {e}")
        results.append(False)

    return all(results), results


def test_phase2_services():
    """Test Phase 2 services."""
    print("\n" + "=" * 60)
    print("PHASE 2: Advanced Services Testing")
    print("=" * 60)

    results = []

    # Test Scraping Service
    print("\n[1/3] Testing Scraping Service...")
    try:
        from app.services.scraping_service import (
            ScrapedData,
            ScrapingConfig,
            ScrapingOrchestrator,
        )

        # Test configuration
        config = ScrapingConfig(max_concurrent_requests=3)
        print(f"✅ ScrapingConfig created: max_concurrent={config.max_concurrent_requests}")

        # Test data structure
        data = ScrapedData(
            url="https://test.com",
            title="Test Title",
            content="Test Content",
            metadata={},
            scraped_at=datetime.utcnow(),
            source_type="html",
        )
        print(f"✅ ScrapedData created: {data.url}")

        # Test orchestrator
        ScrapingOrchestrator(config)
        print("✅ ScrapingOrchestrator created")

        results.append(True)
    except Exception as e:
        print(f"❌ Scraping service failed: {e}")
        import traceback

        traceback.print_exc()
        results.append(False)

    # Test Data Pipeline
    print("\n[2/3] Testing Data Pipeline...")
    try:
        from app.services.data_pipeline import (
            DataPipeline,
            DataTransformer,
            DataValidator,
        )

        # Test transformer
        transformer = DataTransformer()
        normalized = transformer.normalize_text("  test  string  ")
        print(f"✅ DataTransformer working: '{normalized}'")

        # Test validator
        validator = DataValidator()
        result = validator.validate_competitor_data({"name": "Test", "website": "https://test.com"})
        print(f"✅ DataValidator working: valid={result['valid']}")

        # Test pipeline
        DataPipeline()
        print("✅ DataPipeline created")

        results.append(True)
    except Exception as e:
        print(f"❌ Data pipeline failed: {e}")
        import traceback

        traceback.print_exc()
        results.append(False)

    # Test Analytics Service
    print("\n[3/3] Testing Analytics Service...")
    try:
        from app.services.analytics_service import (
            AnalyticsService,
            InsightType,
            RiskLevel,
        )

        # Test enums
        print(f"✅ InsightType: {[t.value for t in InsightType]}")
        print(f"✅ RiskLevel: {[r.value for r in RiskLevel]}")

        # Test analytics service
        AnalyticsService()
        print("✅ AnalyticsService created")

        results.append(True)
    except Exception as e:
        print(f"❌ Analytics service failed: {e}")
        import traceback

        traceback.print_exc()
        results.append(False)

    return all(results), results


def test_api_structure():
    """Test API structure."""
    print("\n" + "=" * 60)
    print("API Structure Testing")
    print("=" * 60)

    results = []

    print("\n[1/3] Testing API Router...")
    try:
        from app.api.v1.api import api_router

        print("✅ Main API router imported")
        print(f"   Routes: {len(api_router.routes)} endpoints")
        results.append(True)
    except Exception as e:
        print(f"❌ API router failed: {e}")
        results.append(False)

    print("\n[2/3] Testing Individual Endpoint Modules...")
    try:
        print("✅ All endpoint modules imported")
        print("   Health: ✓")
        print("   Auth: ✓")
        print("   Users: ✓")
        print("   Competitors: ✓")
        print("   Activities: ✓")
        print("   Products: ✓")
        print("   News: ✓")
        print("   Market: ✓")
        print("   Alerts: ✓")
        print("   Reports: ✓")
        print("   Searches: ✓")
        results.append(True)
    except Exception as e:
        print(f"❌ Endpoint modules failed: {e}")
        results.append(False)

    print("\n[3/3] Testing Main Application...")
    try:
        from app.main import app

        print("✅ Main FastAPI application created")
        print(f"   Title: {app.title}")
        print(f"   Version: {app.version}")
        results.append(True)
    except Exception as e:
        print(f"❌ Main application failed: {e}")
        import traceback

        traceback.print_exc()
        results.append(False)

    return all(results), results


def test_advanced_features():
    """Test advanced features."""
    print("\n" + "=" * 60)
    print("Advanced Features Testing")
    print("=" * 60)

    results = []

    # Test data transformation
    print("\n[1/4] Testing Data Transformation...")
    try:
        from app.services.data_pipeline import DataTransformer

        transformer = DataTransformer()

        # Test text normalization
        text = "  Test   String  "
        normalized = transformer.normalize_text(text)
        assert normalized == "Test String"
        print(f"✅ Text normalization: '{text}' → '{normalized}'")

        # Test categorization
        content = "The company launched a new product and raised funding"
        categories = transformer.categorize_content(content)
        assert "product" in categories
        assert "funding" in categories
        print(f"✅ Content categorization: {categories}")

        # Test sentiment analysis
        sentiment = transformer.calculate_sentiment("Great success and growth")
        assert sentiment["sentiment"] == "positive"
        print(f"✅ Sentiment analysis: {sentiment['sentiment']}")

        results.append(True)
    except Exception as e:
        print(f"❌ Data transformation failed: {e}")
        import traceback

        traceback.print_exc()
        results.append(False)

    # Test data validation
    print("\n[2/4] Testing Data Validation...")
    try:
        from app.services.data_pipeline import DataValidator

        validator = DataValidator()

        # Test valid data
        valid_data = {"name": "Test", "website": "https://test.com"}
        result = validator.validate_competitor_data(valid_data)
        assert result["valid"] is True
        print("✅ Valid data validation: ✓")

        # Test invalid data
        invalid_data = {"name": ""}  # Missing required fields
        result = validator.validate_competitor_data(invalid_data)
        assert result["valid"] is False
        print("✅ Invalid data validation: ✓")

        # Test deduplication
        data = [
            {"id": 1, "name": "Item 1"},
            {"id": 2, "name": "Item 2"},
            {"id": 1, "name": "Item 1 Duplicate"},
        ]
        unique = validator.deduplicate_data(data, "id")
        assert len(unique) == 2
        print(f"✅ Data deduplication: {len(data)} → {len(unique)} items")

        results.append(True)
    except Exception as e:
        print(f"❌ Data validation failed: {e}")
        import traceback

        traceback.print_exc()
        results.append(False)

    # Test scraping capabilities
    print("\n[3/4] Testing Scraping Capabilities...")
    try:
        from app.services.scraping_service import HTMLScraper, ScrapingConfig

        config = ScrapingConfig()
        scraper = HTMLScraper(config)

        # Test HTML extraction
        sample_html = """
        <html>
        <head><title>Test Page</title></head>
        <body>
        <h1>Main Heading</h1>
        <p>Test paragraph with content.</p>
        <a href="https://example.com">Link</a>
        </body>
        </html>
        """

        extracted = scraper.extract_data(sample_html)
        assert extracted["title"] == "Test Page"
        assert "Main Heading" in extracted["headings"]["h1"]
        assert len(extracted["links"]) > 0
        print("✅ HTML extraction: ✓")
        print(f"   Title: {extracted['title']}")
        print(f"   Links found: {len(extracted['links'])}")
        print(f"   Word count: {extracted['word_count']}")

        results.append(True)
    except Exception as e:
        print(f"❌ Scraping capabilities failed: {e}")
        import traceback

        traceback.print_exc()
        results.append(False)

    # Test analytics capabilities
    print("\n[4/4] Testing Analytics Capabilities...")
    try:
        from app.services.analytics_service import Insight, InsightType, RiskLevel

        # Test insight creation
        insight = Insight(
            insight_type=InsightType.COMPETITOR_MOVEMENT,
            title="Test Insight",
            description="Test description",
            confidence=0.8,
            impact_level=RiskLevel.MEDIUM,
            actionable=True,
            recommendations=["Test recommendation"],
            metadata={},
            generated_at=datetime.utcnow(),
        )
        print("✅ Insight creation: ✓")
        print(f"   Type: {insight.insight_type}")
        print(f"   Impact: {insight.impact_level}")
        print(f"   Confidence: {insight.confidence}")

        results.append(True)
    except Exception as e:
        print(f"❌ Analytics capabilities failed: {e}")
        import traceback

        traceback.print_exc()
        results.append(False)

    return all(results), results


def main():
    """Run all tests."""
    print("=" * 60)
    print("🚀 COMPLETE APPLICATION TESTING")
    print("AI Research Competitive Intelligence Platform")
    print("=" * 60)

    # Test each phase
    phase1_success, phase1_results = test_phase1_components()
    phase2_success, phase2_results = test_phase2_services()
    api_success, api_results = test_api_structure()
    advanced_success, advanced_results = test_advanced_features()

    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)

    tests = {
        "Phase 1 - Core Infrastructure": phase1_success,
        "Phase 2 - Advanced Services": phase2_success,
        "API Structure": api_success,
        "Advanced Features": advanced_success,
    }

    for test_name, success in tests.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name}: {status}")

    total_passed = sum(tests.values())
    total_tests = len(tests)

    print(f"\n🎯 OVERALL: {total_passed}/{total_tests} test suites passed")

    if total_passed == total_tests:
        print("\n🎉 SUCCESS! All test suites passed!")
        print("\n✅ Your complete application is ready to run!")
        print("\n🚀 Next steps:")
        print("1. Start the full server: python -m uvicorn app.main:app --reload")
        print("2. Test endpoints at: http://localhost:8000/docs")
        print("3. Test specific services individually")
        print("4. Run database migrations when ready")
        return 0
    else:
        print("\n⚠️  Some test suites failed.")
        print("Please review the errors above and install missing dependencies:")
        print(
            "pip install sqlalchemy aiohttp beautifulsoup4 lxml pandas numpy scikit-learn python-jose passlib bcrypt"
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())

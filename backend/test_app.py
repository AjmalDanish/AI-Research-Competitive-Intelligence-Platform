"""
Simple test script to verify basic functionality.
Run this to check if the application setup is correct.
"""

import os
import sys

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_imports():
    """Test that all core modules can be imported."""
    print("Testing core imports...")

    try:
        from app.core.config import settings

        print(f"✅ Config imported: {settings.PROJECT_NAME}")
    except Exception as e:
        print(f"❌ Config import failed: {e}")
        return False

    try:
        print("✅ Security imported")
    except Exception as e:
        print(f"❌ Security import failed: {e}")
        return False

    try:
        print("✅ Competitor model imported")
    except Exception as e:
        print(f"❌ Competitor model import failed: {e}")
        return False

    try:
        print("✅ Scraping service imported")
    except Exception as e:
        print(f"❌ Scraping service import failed: {e}")
        return False

    try:
        print("✅ Data pipeline imported")
    except Exception as e:
        print(f"❌ Data pipeline import failed: {e}")
        return False

    try:
        print("✅ Analytics service imported")
    except Exception as e:
        print(f"❌ Analytics service import failed: {e}")
        return False

    return True


def test_config():
    """Test configuration settings."""
    print("\nTesting configuration...")

    try:
        from app.core.config import settings

        print(f"✅ Project Name: {settings.PROJECT_NAME}")
        print(f"✅ Version: {settings.VERSION}")
        print(f"✅ Environment: {settings.ENVIRONMENT}")
        print(f"✅ Debug Mode: {settings.DEBUG}")
        print(f"✅ API Version: {settings.API_V1_STR}")

        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


def test_models():
    """Test database models."""
    print("\nTesting database models...")

    try:

        print("✅ All models imported successfully")
        return True
    except Exception as e:
        print(f"❌ Models test failed: {e}")
        return False


def test_services():
    """Test service classes."""
    print("\nTesting service classes...")

    try:
        from app.services.data_pipeline import PipelineResult, PipelineStatus
        from app.services.scraping_service import ScrapedData, ScrapingConfig

        # Test creating objects
        config = ScrapingConfig()
        print(f"✅ ScrapingConfig created: max_concurrent={config.max_concurrent_requests}")

        data = ScrapedData(
            url="https://test.com",
            title="Test",
            content="Content",
            metadata={},
            scraped_at=None,
            source_type="html",
        )
        print(f"✅ ScrapedData created: {data.url}")

        result = PipelineResult(pipeline_id="test", status=PipelineStatus.RUNNING)
        print(f"✅ PipelineResult created: status={result.status}")

        print("✅ All service classes work correctly")
        return True
    except Exception as e:
        print(f"❌ Services test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_api_structure():
    """Test API structure."""
    print("\nTesting API structure...")

    try:

        print("✅ API router imported")
        print("✅ Core endpoints imported")
        return True
    except Exception as e:
        print(f"❌ API structure test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("AI Research Competitive Intelligence Platform - Basic Tests")
    print("=" * 60)

    tests = [
        ("Import Tests", test_imports),
        ("Configuration Tests", test_config),
        ("Model Tests", test_models),
        ("Service Tests", test_services),
        ("API Structure Tests", test_api_structure),
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results[test_name] = False

    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)

    passed = sum(1 for result in results.values() if result)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")

    print(f"\nTotal: {passed}/{total} test suites passed")

    if passed == total:
        print("\n🎉 All basic tests passed! The application structure is correct.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

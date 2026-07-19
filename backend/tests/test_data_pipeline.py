"""
Unit tests for the data pipeline service.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch

from app.services.data_pipeline import (
    PipelineStatus,
    PipelineResult,
    DataTransformer,
    DataValidator,
    DataPipeline,
)
from app.services.scraping_service import ScrapedData


@pytest.fixture
def sample_scraped_data():
    """Create sample scraped data for testing."""
    return [
        ScrapedData(
            url="https://example.com/article1",
            title="Company X Launches New AI Platform",
            content="Company X has announced the launch of their new AI-powered platform designed for enterprise customers. The platform includes advanced machine learning capabilities and real-time analytics.",
            metadata={"source_type": "html", "source_name": "Tech News", "author": "John Doe"},
            scraped_at=datetime.utcnow(),
            source_type="html",
        ),
        ScrapedData(
            url="https://example.com/article2",
            title="Company Y Raises $50M in Series B Funding",
            content="Company Y, a leading startup in the cloud computing space, has successfully raised $50 million in Series B funding led by top venture capital firms.",
            metadata={
                "source_type": "html",
                "source_name": "Business News",
                "author": "Jane Smith",
            },
            scraped_at=datetime.utcnow(),
            source_type="html",
        ),
    ]


class TestPipelineStatus:
    """Tests for PipelineStatus enum."""

    def test_status_values(self):
        """Test all status values exist."""
        assert PipelineStatus.PENDING == "pending"
        assert PipelineStatus.RUNNING == "running"
        assert PipelineStatus.COMPLETED == "completed"
        assert PipelineStatus.FAILED == "failed"
        assert PipelineStatus.CANCELLED == "cancelled"


class TestPipelineResult:
    """Tests for PipelineResult dataclass."""

    def test_result_creation(self):
        """Test creating pipeline result."""
        result = PipelineResult(pipeline_id="test_pipeline", status=PipelineStatus.RUNNING)

        assert result.pipeline_id == "test_pipeline"
        assert result.status == PipelineStatus.RUNNING
        assert result.records_processed == 0
        assert result.records_failed == 0
        assert result.errors == []

    def test_result_duration(self):
        """Test duration calculation."""
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(seconds=30)

        result = PipelineResult(
            pipeline_id="test_pipeline",
            status=PipelineStatus.COMPLETED,
            start_time=start_time,
            end_time=end_time,
        )

        assert result.duration == 30.0

    def test_result_duration_no_times(self):
        """Test duration with no times set."""
        result = PipelineResult(pipeline_id="test_pipeline", status=PipelineStatus.RUNNING)

        assert result.duration is None

    def test_success_rate_calculation(self):
        """Test success rate calculation."""
        result = PipelineResult(
            pipeline_id="test_pipeline",
            status=PipelineStatus.COMPLETED,
            records_processed=80,
            records_failed=20,
        )

        assert result.success_rate == 80.0

    def test_success_rate_no_records(self):
        """Test success rate with no records."""
        result = PipelineResult(pipeline_id="test_pipeline", status=PipelineStatus.COMPLETED)

        assert result.success_rate == 0.0


class TestDataTransformer:
    """Tests for DataTransformer class."""

    def test_normalize_text(self):
        """Test text normalization."""
        transformer = DataTransformer()

        text = "  This   is   a   test  \n\n  string  "
        normalized = transformer.normalize_text(text)

        assert normalized == "This is a test string"

    def test_normalize_text_empty(self):
        """Test normalizing empty text."""
        transformer = DataTransformer()

        normalized = transformer.normalize_text("")

        assert normalized == ""

    def test_normalize_text_none(self):
        """Test normalizing None text."""
        transformer = DataTransformer()

        normalized = transformer.normalize_text(None)

        assert normalized == ""

    def test_extract_urls(self):
        """Test URL extraction."""
        transformer = DataTransformer()

        text = "Visit https://example.com or http://test.org for more info"
        urls = transformer.extract_urls(text)

        assert len(urls) == 2
        assert "https://example.com" in urls
        assert "http://test.org" in urls

    def test_extract_urls_none(self):
        """Test URL extraction with no URLs."""
        transformer = DataTransformer()

        urls = transformer.extract_urls("No URLs here")

        assert urls == []

    def test_categorize_content_product(self):
        """Test content categorization for product launches."""
        transformer = DataTransformer()

        content = "The company announced the launch of their new product release"
        categories = transformer.categorize_content(content)

        assert "product" in categories

    def test_categorize_content_funding(self):
        """Test content categorization for funding news."""
        transformer = DataTransformer()

        content = "The startup raised funding in their series A round"
        categories = transformer.categorize_content(content)

        assert "funding" in categories

    def test_categorize_content_multiple(self):
        """Test content categorization with multiple categories."""
        transformer = DataTransformer()

        content = "The product launch and funding round were successful"
        categories = transformer.categorize_content(content)

        assert "product" in categories
        assert "funding" in categories

    def test_calculate_sentiment_positive(self):
        """Test positive sentiment calculation."""
        transformer = DataTransformer()

        content = "The company achieved success and growth with innovation"
        sentiment = transformer.calculate_sentiment(content)

        assert sentiment["sentiment"] == "positive"
        assert sentiment["score"] > 0

    def test_calculate_sentiment_negative(self):
        """Test negative sentiment calculation."""
        transformer = DataTransformer()

        content = "The company faced challenges and losses with declining revenue"
        sentiment = transformer.calculate_sentiment(content)

        assert sentiment["sentiment"] == "negative"
        assert sentiment["score"] < 0

    def test_calculate_sentiment_neutral(self):
        """Test neutral sentiment calculation."""
        transformer = DataTransformer()

        content = "The company provided general information"
        sentiment = transformer.calculate_sentiment(content)

        assert sentiment["sentiment"] == "neutral"
        assert sentiment["score"] == 0.0


class TestDataValidator:
    """Tests for DataValidator class."""

    def test_validate_competitor_data_valid(self):
        """Test validating valid competitor data."""
        validator = DataValidator()

        data = {"name": "Test Company", "website": "https://test.com", "email": "test@test.com"}

        result = validator.validate_competitor_data(data)

        assert result["valid"] is True
        assert result["errors"] == []

    def test_validate_competitor_data_missing_name(self):
        """Test validating competitor data with missing name."""
        validator = DataValidator()

        data = {"website": "https://test.com"}

        result = validator.validate_competitor_data(data)

        assert result["valid"] is False
        assert "Missing required field: name" in result["errors"]

    def test_validate_competitor_data_invalid_email(self):
        """Test validating competitor data with invalid email."""
        validator = DataValidator()

        data = {"name": "Test Company", "website": "https://test.com", "email": "invalid-email"}

        result = validator.validate_competitor_data(data)

        assert "Invalid email format" in result["errors"]

    def test_validate_competitor_data_website_warning(self):
        """Test validating competitor data with non-HTTPS website."""
        validator = DataValidator()

        data = {"name": "Test Company", "website": "test.com", "email": "test@test.com"}

        result = validator.validate_competitor_data(data)

        assert any("http" in warning for warning in result["warnings"])

    def test_validate_activity_data_valid(self):
        """Test validating valid activity data."""
        validator = DataValidator()

        data = {"competitor_id": 1, "activity_type": "product_release", "title": "Test Activity"}

        result = validator.validate_activity_data(data)

        assert result["valid"] is True
        assert result["errors"] == []

    def test_validate_activity_data_missing_fields(self):
        """Test validating activity data with missing fields."""
        validator = DataValidator()

        data = {"competitor_id": 1}

        result = validator.validate_activity_data(data)

        assert result["valid"] is False
        assert len(result["errors"]) == 2

    def test_deduplicate_data(self):
        """Test data deduplication."""
        validator = DataValidator()

        data = [
            {"id": 1, "name": "Item 1"},
            {"id": 2, "name": "Item 2"},
            {"id": 1, "name": "Item 1 Duplicate"},
            {"id": 3, "name": "Item 3"},
        ]

        unique_data = validator.deduplicate_data(data, "id")

        assert len(unique_data) == 3
        assert unique_data[0]["id"] == 1
        assert unique_data[1]["id"] == 2
        assert unique_data[2]["id"] == 3


@pytest.mark.integration
class TestDataPipelineIntegration:
    """Integration tests for data pipeline."""

    @pytest.mark.asyncio
    async def test_full_pipeline_workflow(self, sample_scraped_data):
        """Test complete pipeline workflow."""
        pipeline = DataPipeline()

        # Test transformation
        transformed_data = await pipeline._transform_data(sample_scraped_data[0])

        # Verify transformation
        assert "title" in transformed_data
        assert "content" in transformed_data
        assert "categories" in transformed_data
        assert "sentiment" in transformed_data

        # Test validation
        validation = pipeline._validate_transformed_data(transformed_data)

        assert validation["valid"] is True
        assert len(validation["errors"]) == 0

    @pytest.mark.asyncio
    async def test_pipeline_with_invalid_data(self):
        """Test pipeline with invalid scraped data."""
        pipeline = DataPipeline()

        invalid_data = ScrapedData(
            url="",
            title="",
            content="",
            metadata={},
            scraped_at=datetime.utcnow(),
            source_type="html",
        )

        transformed_data = await pipeline._transform_data(invalid_data)
        validation = pipeline._validate_transformed_data(transformed_data)

        assert validation["valid"] is False
        assert len(validation["errors"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

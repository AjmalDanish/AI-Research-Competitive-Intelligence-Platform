"""
Data pipeline service for processing and transforming competitive intelligence data.

This module handles data extraction, transformation, and loading (ETL) processes
for competitive intelligence data.
"""

import asyncio
import logging
from typing import List, Dict, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json

import pandas as pd
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from app.core.config import settings
from app.core.logging import get_logger
from app.db.session import AsyncSessionLocal
from app.models.competitor import Competitor, CompetitorActivity, CompetitorNews
from app.models.market import MarketTrend, MarketIntelligence
from app.services.scraping_service import ScrapedData, ScrapingOrchestrator, ScrapingConfig

logger = get_logger(__name__)


class PipelineStatus(str, Enum):
    """Pipeline execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class PipelineResult:
    """Result of a pipeline execution."""
    pipeline_id: str
    status: PipelineStatus
    records_processed: int = 0
    records_failed: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def duration(self) -> Optional[float]:
        """Calculate pipeline duration in seconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        total = self.records_processed + self.records_failed
        if total == 0:
            return 0.0
        return (self.records_processed / total) * 100


class DataTransformer:
    """Transforms raw scraped data into structured formats."""
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """Normalize text by removing extra whitespace and special characters."""
        if not text:
            return ""
        return ' '.join(text.split())
    
    @staticmethod
    def extract_urls(text: str) -> List[str]:
        """Extract URLs from text."""
        import re
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        return re.findall(url_pattern, text)
    
    @staticmethod
    def extract_dates(text: str) -> List[datetime]:
        """Extract dates from text."""
        from dateutil.parser import parse
        from dateutil.parser._parser import ParserError
        
        dates = []
        import re
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',
            r'\d{2}/\d{2}/\d{4}',
            r'\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}',
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    parsed_date = parse(match)
                    dates.append(parsed_date)
                except ParserError:
                    continue
        
        return dates
    
    @staticmethod
    def categorize_content(content: str) -> List[str]:
        """Categorize content based on keywords."""
        categories = {
            'product': ['launch', 'release', 'product', 'feature', 'update'],
            'funding': ['funding', 'investment', 'raise', 'series', 'round'],
            'partnership': ['partnership', 'collaboration', 'acquisition', 'merger'],
            'leadership': ['ceo', 'executive', 'leadership', 'appointment', 'hire'],
            'technology': ['ai', 'machine learning', 'blockchain', 'cloud', 'saas'],
            'financial': ['revenue', 'earnings', 'profit', 'loss', 'financial'],
            'market': ['market', 'share', 'growth', 'expansion', 'global'],
        }
        
        content_lower = content.lower()
        detected_categories = []
        
        for category, keywords in categories.items():
            if any(keyword in content_lower for keyword in keywords):
                detected_categories.append(category)
        
        return detected_categories
    
    @staticmethod
    def extract_entities(text: str) -> Dict[str, List[str]]:
        """Extract named entities from text."""
        entities = {
            'companies': [],
            'locations': [],
            'organizations': [],
            'people': []
        }
        
        # Simple keyword-based extraction (would use NLP in production)
        company_keywords = ['Inc', 'Corp', 'Ltd', 'LLC', 'Company', 'Technologies']
        for keyword in company_keywords:
            if keyword in text:
                # Extract surrounding context
                words = text.split()
                for i, word in enumerate(words):
                    if keyword in word:
                        context_start = max(0, i - 2)
                        context_end = min(len(words), i + 3)
                        entity = ' '.join(words[context_start:context_end])
                        entities['companies'].append(entity)
        
        return entities
    
    @staticmethod
    def calculate_sentiment(text: str) -> Dict[str, Any]:
        """Calculate sentiment analysis of text."""
        # Simple sentiment analysis (would use ML models in production)
        positive_words = [
            'success', 'growth', 'innovation', 'launch', 'expand', 'increase',
            'profit', 'gain', 'improve', 'advance', 'breakthrough'
        ]
        negative_words = [
            'decline', 'loss', 'fail', 'cut', 'reduce', 'layoff', 'shutdown',
            'decrease', 'struggle', 'challenge', 'concern', 'risk'
        ]
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        total = positive_count + negative_count
        if total == 0:
            sentiment = 'neutral'
            score = 0.0
        elif positive_count > negative_count:
            sentiment = 'positive'
            score = positive_count / total
        else:
            sentiment = 'negative'
            score = -negative_count / total
        
        return {
            'sentiment': sentiment,
            'score': score,
            'positive_count': positive_count,
            'negative_count': negative_count
        }


class DataValidator:
    """Validates data quality and integrity."""
    
    @staticmethod
    def validate_competitor_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate competitor data."""
        errors = []
        warnings = []
        
        # Required fields
        required_fields = ['name', 'website']
        for field in required_fields:
            if not data.get(field):
                errors.append(f"Missing required field: {field}")
        
        # Validate website format
        if data.get('website'):
            if not data['website'].startswith(('http://', 'https://')):
                warnings.append("Website should start with http:// or https://")
        
        # Validate email format
        if data.get('email'):
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, data['email']):
                errors.append("Invalid email format")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    @staticmethod
    def validate_activity_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate activity data."""
        errors = []
        warnings = []
        
        required_fields = ['competitor_id', 'activity_type', 'title']
        for field in required_fields:
            if not data.get(field):
                errors.append(f"Missing required field: {field}")
        
        # Validate activity type
        valid_types = ['product_release', 'partnership', 'funding', 'leadership', 'technology', 'financial']
        if data.get('activity_type') and data['activity_type'] not in valid_types:
            warnings.append(f"Unknown activity type: {data['activity_type']}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    @staticmethod
    def deduplicate_data(data: List[Dict[str, Any]], key_field: str) -> List[Dict[str, Any]]:
        """Remove duplicate records based on a key field."""
        seen = set()
        unique_data = []
        
        for item in data:
            key = item.get(key_field)
            if key not in seen:
                seen.add(key)
                unique_data.append(item)
        
        return unique_data


class DataPipeline:
    """Main data pipeline for competitive intelligence."""
    
    def __init__(self):
        self.transformer = DataTransformer()
        self.validator = DataValidator()
        self.logger = logger
        self._is_running = False
    
    async def process_scraped_data(
        self,
        scraped_data: List[ScrapedData],
        db: AsyncSession
    ) -> PipelineResult:
        """
        Process scraped data and store in database.
        
        Args:
            scraped_data: List of scraped data items
            db: Database session
            
        Returns:
            PipelineResult: Processing results
        """
        pipeline_id = f"pipeline_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        result = PipelineResult(
            pipeline_id=pipeline_id,
            status=PipelineStatus.RUNNING,
            start_time=datetime.utcnow()
        )
        
        try:
            self._is_running = True
            
            for data in scraped_data:
                try:
                    # Transform data
                    transformed = await self._transform_data(data)
                    
                    # Validate data
                    validation = self._validate_transformed_data(transformed)
                    if not validation['valid']:
                        result.errors.extend(validation['errors'])
                        result.records_failed += 1
                        continue
                    
                    # Store data
                    await self._store_data(transformed, db)
                    result.records_processed += 1
                    
                    self.logger.info(
                        f"Processed data from {data.url} - {data.title}"
                    )
                    
                except Exception as e:
                    self.logger.error(f"Error processing data from {data.url}: {e}")
                    result.errors.append(str(e))
                    result.records_failed += 1
            
            await db.commit()
            result.status = PipelineStatus.COMPLETED
            
        except Exception as e:
            self.logger.error(f"Pipeline error: {e}")
            result.status = PipelineStatus.FAILED
            result.errors.append(str(e))
            await db.rollback()
            
        finally:
            self._is_running = False
            result.end_time = datetime.utcnow()
            result.metadata['duration'] = result.duration
            
            self.logger.info(
                f"Pipeline {pipeline_id} completed: "
                f"{result.records_processed} processed, {result.records_failed} failed"
            )
        
        return result
    
    async def _transform_data(self, scraped_data: ScrapedData) -> Dict[str, Any]:
        """Transform scraped data into structured format."""
        content = scraped_data.content
        
        transformed = {
            'url': scraped_data.url,
            'title': self.transformer.normalize_text(scraped_data.title),
            'content': self.transformer.normalize_text(content),
            'summary': content[:500] if len(content) > 500 else content,
            'categories': self.transformer.categorize_content(content),
            'sentiment': self.transformer.calculate_sentiment(content),
            'entities': self.transformer.extract_entities(content),
            'urls': self.transformer.extract_urls(content),
            'dates': self.transformer.extract_dates(content),
            'scraped_at': scraped_data.scraped_at,
            'metadata': scraped_data.metadata
        }
        
        return transformed
    
    def _validate_transformed_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate transformed data."""
        errors = []
        
        if not data.get('title'):
            errors.append("Missing title")
        
        if not data.get('url'):
            errors.append("Missing URL")
        
        if not data.get('content'):
            errors.append("Missing content")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    async def _store_data(self, data: Dict[str, Any], db: AsyncSession):
        """Store processed data in database."""
        # Determine data type and store accordingly
        if any(keyword in data['title'].lower() for keyword in ['release', 'launch', 'product']):
            await self._store_as_activity(data, db)
        elif any(keyword in data['title'].lower() for keyword in ['news', 'press', 'announcement']):
            await self._store_as_news(data, db)
        else:
            await self._store_as_intelligence(data, db)
    
    async def _store_as_activity(self, data: Dict[str, Any], db: AsyncSession):
        """Store data as competitor activity."""
        activity = CompetitorActivity(
            title=data['title'],
            description=data['summary'],
            activity_type=data['categories'][0] if data['categories'] else 'other',
            source_url=data['url'],
            source_type=data['metadata'].get('source_type', 'web'),
            impact_level='high' if data['sentiment']['score'] > 0.5 else 'medium',
            processed=True,
            verified=False,
            metadata=data
        )
        db.add(activity)
    
    async def _store_as_news(self, data: Dict[str, Any], db: AsyncSession):
        """Store data as competitor news."""
        news = CompetitorNews(
            title=data['title'],
            summary=data['summary'],
            content=data['content'],
            source_url=data['url'],
            source_name=data['metadata'].get('source_name', 'Unknown'),
            sentiment=data['sentiment']['sentiment'],
            sentiment_score=abs(data['sentiment']['score']),
            category=data['categories'][0] if data['categories'] else 'general',
            tags=data['categories'],
            processed=True,
            analyzed=True,
            metadata=data
        )
        db.add(news)
    
    async def _store_as_intelligence(self, data: Dict[str, Any], db: AsyncSession):
        """Store data as market intelligence."""
        intelligence = MarketIntelligence(
            title=data['title'],
            summary=data['summary'],
            content=data['content'],
            source_type='web',
            source_url=data['url'],
            sentiment=data['sentiment']['sentiment'],
            importance_level='high' if data['sentiment']['score'] > 0.5 else 'medium',
            categories=data['categories'],
            tags=data['categories'],
            processed=True,
            verified=False,
            metadata=data
        )
        db.add(intelligence)
    
    async def run_scheduled_pipeline(
        self,
        competitor_ids: List[int],
        db: AsyncSession
    ) -> PipelineResult:
        """
        Run scheduled data collection pipeline.
        
        Args:
            competitor_ids: List of competitor IDs to monitor
            db: Database session
            
        Returns:
            PipelineResult: Pipeline execution results
        """
        self.logger.info(f"Starting scheduled pipeline for {len(competitor_ids)} competitors")
        
        # Get competitor websites
        competitors_query = select(Competitor).where(Competitor.id.in_(competitor_ids))
        result = await db.execute(competitors_query)
        competitors = result.scalars().all()
        
        if not competitors:
            return PipelineResult(
                pipeline_id=f"scheduled_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                status=PipelineStatus.FAILED,
                errors=["No competitors found for monitoring"]
            )
        
        # Collect URLs to scrape
        urls_to_scrape = []
        for competitor in competitors:
            if competitor.website:
                urls_to_scrape.append(competitor.website)
        
        # Setup scraping
        scraping_config = ScrapingConfig(
            max_concurrent_requests=3,
            request_timeout=30,
            retry_attempts=2
        )
        
        orchestrator = ScrapingOrchestrator(scraping_config)
        
        # Scrape data
        scraped_data = await orchestrator.scrape_multiple(urls_to_scrape)
        
        # Process scraped data
        result = await self.process_scraped_data(scraped_data, db)
        
        return result
    
    def stop(self):
        """Stop pipeline execution."""
        self._is_running = False
        self.logger.info("Pipeline stop requested")


# Global pipeline instance
pipeline = DataPipeline()


async def get_pipeline() -> DataPipeline:
    """Get the global pipeline instance."""
    return pipeline
"""
Analytics and insights service for competitive intelligence.

This module provides advanced analytics, trend analysis, and
predictive capabilities for competitive intelligence data.
"""

import logging
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import statistics

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from app.core.config import settings
from app.core.logging import get_logger
from app.db.session import AsyncSessionLocal
from app.models.competitor import Competitor, CompetitorActivity, CompetitorProduct, CompetitorNews
from app.models.market import MarketTrend, MarketIntelligence

logger = get_logger(__name__)


class InsightType(str, Enum):
    """Types of insights that can be generated."""

    COMPETITOR_MOVEMENT = "competitor_movement"
    MARKET_TREND = "market_trend"
    RISK_ASSESSMENT = "risk_assessment"
    OPPORTUNITY_ANALYSIS = "opportunity_analysis"
    PERFORMANCE_METRIC = "performance_metric"
    PREDICTIVE_INSIGHT = "predictive_insight"


class RiskLevel(str, Enum):
    """Risk assessment levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Insight:
    """Generated insight from analytics."""

    insight_type: InsightType
    title: str
    description: str
    confidence: float  # 0.0 to 1.0
    impact_level: RiskLevel
    actionable: bool
    recommendations: List[str]
    metadata: Dict[str, Any]
    generated_at: datetime


@dataclass
class CompetitorAnalysis:
    """Analysis results for a competitor."""

    competitor_id: int
    competitor_name: str
    activity_level: str
    growth_trend: str
    market_position: str
    strengths: List[str]
    weaknesses: List[str]
    opportunities: List[str]
    threats: List[str]
    risk_assessment: RiskLevel
    performance_score: float
    last_updated: datetime


@dataclass
class MarketForecast:
    """Market forecast and predictions."""

    forecast_period: str
    predicted_growth: float
    confidence_interval: Tuple[float, float]
    key_drivers: List[str]
    risk_factors: List[str]
    opportunities: List[str]
    methodology: str
    generated_at: datetime


class AnalyticsService:
    """Service for generating analytics and insights."""

    def __init__(self):
        self.logger = logger
        self._vectorizer = TfidfVectorizer(max_features=100, stop_words="english")
        self._scaler = StandardScaler()

    async def analyze_competitor(
        self, competitor_id: int, db: AsyncSession, time_period: int = 90  # days
    ) -> CompetitorAnalysis:
        """
        Perform comprehensive competitor analysis.

        Args:
            competitor_id: ID of competitor to analyze
            db: Database session
            time_period: Analysis period in days

        Returns:
            CompetitorAnalysis: Comprehensive analysis results
        """
        # Get competitor data
        result = await db.execute(select(Competitor).where(Competitor.id == competitor_id))
        competitor = result.scalar_one_or_none()

        if not competitor:
            raise ValueError(f"Competitor {competitor_id} not found")

        # Get recent activities
        cutoff_date = datetime.utcnow() - timedelta(days=time_period)
        activities_result = await db.execute(
            select(CompetitorActivity).where(
                and_(
                    CompetitorActivity.competitor_id == competitor_id,
                    CompetitorActivity.activity_date >= cutoff_date,
                )
            )
        )
        activities = activities_result.scalars().all()

        # Get products
        products_result = await db.execute(
            select(CompetitorProduct).where(CompetitorProduct.competitor_id == competitor_id)
        )
        products = products_result.scalars().all()

        # Get news
        news_result = await db.execute(
            select(CompetitorNews).where(
                and_(
                    CompetitorNews.competitor_id == competitor_id,
                    CompetitorNews.publish_date >= cutoff_date,
                )
            )
        )
        news_items = news_result.scalars().all()

        # Generate analysis
        activity_level = self._assess_activity_level(activities)
        growth_trend = self._analyze_growth_trend(activities, news_items)
        market_position = self._assess_market_position(competitor, products)

        swot_analysis = await self._perform_swot_analysis(
            competitor, activities, products, news_items, db
        )

        risk_assessment = self._assess_competitor_risk(activities, news_items)
        performance_score = self._calculate_performance_score(activities, products, news_items)

        return CompetitorAnalysis(
            competitor_id=competitor.id,
            competitor_name=competitor.name,
            activity_level=activity_level,
            growth_trend=growth_trend,
            market_position=market_position,
            strengths=swot_analysis["strengths"],
            weaknesses=swot_analysis["weaknesses"],
            opportunities=swot_analysis["opportunities"],
            threats=swot_analysis["threats"],
            risk_assessment=risk_assessment,
            performance_score=performance_score,
            last_updated=datetime.utcnow(),
        )

    def _assess_activity_level(self, activities: List[CompetitorActivity]) -> str:
        """Assess competitor's activity level."""
        if len(activities) == 0:
            return "inactive"
        elif len(activities) < 5:
            return "low"
        elif len(activities) < 15:
            return "moderate"
        else:
            return "high"

    def _analyze_growth_trend(
        self, activities: List[CompetitorActivity], news_items: List[CompetitorNews]
    ) -> str:
        """Analyze competitor's growth trend."""
        positive_indicators = 0
        negative_indicators = 0

        for activity in activities:
            if activity.impact_level in ["high", "critical"]:
                positive_indicators += 1

        for news in news_items:
            if news.sentiment == "positive":
                positive_indicators += 1
            elif news.sentiment == "negative":
                negative_indicators += 1

        if positive_indicators > negative_indicators * 2:
            return "rapid_growth"
        elif positive_indicators > negative_indicators:
            return "steady_growth"
        elif negative_indicators > positive_indicators:
            return "declining"
        else:
            return "stable"

    def _assess_market_position(
        self, competitor: Competitor, products: List[CompetitorProduct]
    ) -> str:
        """Assess competitor's market position."""
        factors = []

        # Tier assessment
        if competitor.tier == "enterprise":
            factors.append("high")
        elif competitor.tier == "large":
            factors.append("medium_high")
        elif competitor.tier == "medium":
            factors.append("medium")
        else:
            factors.append("low")

        # Product diversity
        if len(products) > 10:
            factors.append("high")
        elif len(products) > 5:
            factors.append("medium")
        else:
            factors.append("low")

        # Revenue assessment
        if competitor.revenue:
            if competitor.revenue > 1000000000:  # $1B
                factors.append("high")
            elif competitor.revenue > 100000000:  # $100M
                factors.append("medium_high")
            elif competitor.revenue > 10000000:  # $10M
                factors.append("medium")
            else:
                factors.append("low")

        # Aggregate position
        position_scores = {"high": 4, "medium_high": 3, "medium": 2, "low": 1}
        avg_score = statistics.mean([position_scores.get(f, 2) for f in factors])

        if avg_score >= 3.5:
            return "market_leader"
        elif avg_score >= 2.5:
            return "strong_competitor"
        elif avg_score >= 1.5:
            return "market_follower"
        else:
            return "niche_player"

    async def _perform_swot_analysis(
        self,
        competitor: Competitor,
        activities: List[CompetitorActivity],
        products: List[CompetitorProduct],
        news_items: List[CompetitorNews],
        db: AsyncSession,
    ) -> Dict[str, List[str]]:
        """Perform SWOT analysis."""
        swot = {"strengths": [], "weaknesses": [], "opportunities": [], "threats": []}

        # Strengths
        if competitor.revenue and competitor.revenue > 100000000:
            swot["strengths"].append("Strong financial position")
        if len(products) > 5:
            swot["strengths"].append("Diverse product portfolio")
        if len([a for a in activities if a.activity_type == "product_release"]) > 3:
            swot["strengths"].append("Active product development")

        # Weaknesses
        if len(products) < 3:
            swot["weaknesses"].append("Limited product offerings")
        if not competitor.website:
            swot["weaknesses"].append("No web presence")
        if len([n for n in news_items if n.sentiment == "negative"]) > len(news_items) * 0.3:
            swot["weaknesses"].append("Negative public perception")

        # Opportunities
        positive_news = [n for n in news_items if n.sentiment == "positive"]
        if len(positive_news) > len(news_items) * 0.5:
            swot["opportunities"].append("Positive market sentiment")
        swot["opportunities"].append("Market expansion potential")
        swot["opportunities"].append("Strategic partnership opportunities")

        # Threats
        negative_news = [n for n in news_items if n.sentiment == "negative"]
        if len(negative_news) > len(news_items) * 0.3:
            swot["threats"].append("Negative market perception")
        swot["threats"].append("Competitive pressure")
        swot["threats"].append("Market volatility risks")

        return swot

    def _assess_competitor_risk(
        self, activities: List[CompetitorActivity], news_items: List[CompetitorNews]
    ) -> RiskLevel:
        """Assess competitor risk level."""
        risk_factors = 0

        # High-impact negative activities
        high_impact_negative = [
            a for a in activities if a.impact_level == "critical" and "shutdown" in a.title.lower()
        ]
        risk_factors += len(high_impact_negative) * 3

        # Negative sentiment in news
        negative_news_ratio = len([n for n in news_items if n.sentiment == "negative"]) / max(
            len(news_items), 1
        )
        if negative_news_ratio > 0.5:
            risk_factors += 2
        elif negative_news_ratio > 0.3:
            risk_factors += 1

        # Inactivity
        if len(activities) == 0:
            risk_factors += 2

        # Determine risk level
        if risk_factors >= 5:
            return RiskLevel.CRITICAL
        elif risk_factors >= 3:
            return RiskLevel.HIGH
        elif risk_factors >= 1:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    def _calculate_performance_score(
        self,
        activities: List[CompetitorActivity],
        products: List[CompetitorProduct],
        news_items: List[CompetitorNews],
    ) -> float:
        """Calculate overall performance score (0-100)."""
        score = 50.0  # Base score

        # Activity score
        score += min(len(activities) * 2, 20)  # Max +20

        # Product diversity score
        score += min(len(products) * 3, 15)  # Max +15

        # Sentiment score
        if news_items:
            positive_ratio = len([n for n in news_items if n.sentiment == "positive"]) / len(
                news_items
            )
            score += positive_ratio * 10  # Max +10

        # Impact score
        high_impact = len([a for a in activities if a.impact_level in ["high", "critical"]])
        score += min(high_impact * 2, 5)  # Max +5

        return min(max(score, 0), 100)  # Clamp between 0-100

    async def generate_market_forecast(
        self, industry: str, db: AsyncSession, forecast_months: int = 12
    ) -> MarketForecast:
        """
        Generate market forecast for an industry.

        Args:
            industry: Industry to forecast
            db: Database session
            forecast_months: Number of months to forecast

        Returns:
            MarketForecast: Market forecast results
        """
        # Get market trends
        trends_result = await db.execute(
            select(MarketTrend).where(MarketTrend.industry == industry)
        )
        trends = trends_result.scalars().all()

        # Get market intelligence
        intelligence_result = await db.execute(
            select(MarketIntelligence).where(MarketIntelligence.industry == industry)
        )
        intelligence_items = intelligence_result.scalars().all()

        # Analyze trends
        growth_rates = [t.growth_rate for t in trends if t.growth_rate is not None]
        avg_growth = statistics.mean(growth_rates) if growth_rates else 5.0

        # Calculate confidence interval
        std_dev = statistics.stdev(growth_rates) if len(growth_rates) > 1 else 2.0
        confidence_interval = (max(0, avg_growth - 1.96 * std_dev), avg_growth + 1.96 * std_dev)

        # Identify key drivers
        key_drivers = self._identify_key_drivers(trends, intelligence_items)

        # Identify risk factors
        risk_factors = self._identify_risk_factors(intelligence_items)

        # Identify opportunities
        opportunities = self._identify_opportunities(intelligence_items)

        return MarketForecast(
            forecast_period=f"{forecast_months} months",
            predicted_growth=avg_growth,
            confidence_interval=confidence_interval,
            key_drivers=key_drivers,
            risk_factors=risk_factors,
            opportunities=opportunities,
            methodology="Statistical analysis of market trends and intelligence data",
            generated_at=datetime.utcnow(),
        )

    def _identify_key_drivers(
        self, trends: List[MarketTrend], intelligence_items: List[MarketIntelligence]
    ) -> List[str]:
        """Identify key market drivers."""
        drivers = []

        # From trends
        for trend in trends:
            if trend.growth_rate and trend.growth_rate > 10:
                drivers.append(f"Growing trend: {trend.name}")

        # From intelligence
        for intel in intelligence_items:
            if intel.importance_level == "critical":
                drivers.append(f"Critical factor: {intel.title}")

        return drivers[:5]  # Top 5 drivers

    def _identify_risk_factors(self, intelligence_items: List[MarketIntelligence]) -> List[str]:
        """Identify market risk factors."""
        risks = []

        for intel in intelligence_items:
            if intel.sentiment == "negative" and intel.importance_level in ["high", "critical"]:
                risks.append(f"Risk: {intel.title}")

        return risks[:5]  # Top 5 risks

    def _identify_opportunities(self, intelligence_items: List[MarketIntelligence]) -> List[str]:
        """Identify market opportunities."""
        opportunities = []

        for intel in intelligence_items:
            if intel.sentiment == "positive":
                opportunities.append(f"Opportunity: {intel.title}")

        return opportunities[:5]  # Top 5 opportunities

    async def generate_insights(
        self, db: AsyncSession, insight_type: Optional[InsightType] = None
    ) -> List[Insight]:
        """
        Generate actionable insights from data analysis.

        Args:
            db: Database session
            insight_type: Type of insights to generate (None for all)

        Returns:
            List of generated insights
        """
        insights = []

        # Generate competitor movement insights
        if insight_type is None or insight_type == InsightType.COMPETITOR_MOVEMENT:
            insights.extend(await self._generate_competitor_movement_insights(db))

        # Generate market trend insights
        if insight_type is None or insight_type == InsightType.MARKET_TREND:
            insights.extend(await self._generate_market_trend_insights(db))

        # Generate risk assessment insights
        if insight_type is None or insight_type == InsightType.RISK_ASSESSMENT:
            insights.extend(await self._generate_risk_assessment_insights(db))

        # Generate opportunity analysis insights
        if insight_type is None or insight_type == InsightType.OPPORTUNITY_ANALYSIS:
            insights.extend(await self._generate_opportunity_insights(db))

        return insights

    async def _generate_competitor_movement_insights(self, db: AsyncSession) -> List[Insight]:
        """Generate insights about competitor movements."""
        insights = []

        # Get recent activities
        recent_date = datetime.utcnow() - timedelta(days=30)
        result = await db.execute(
            select(CompetitorActivity).where(CompetitorActivity.activity_date >= recent_date)
        )
        activities = result.scalars().all()

        # Analyze activity patterns
        activity_types = {}
        for activity in activities:
            activity_type = activity.activity_type
            activity_types[activity_type] = activity_types.get(activity_type, 0) + 1

        # Generate insights based on activity patterns
        for activity_type, count in activity_types.items():
            if count > 5:
                insights.append(
                    Insight(
                        insight_type=InsightType.COMPETITOR_MOVEMENT,
                        title=f"High {activity_type} activity detected",
                        description=f"Detected {count} {activity_type} activities in the last 30 days, indicating increased competitor activity in this area.",
                        confidence=0.8,
                        impact_level=(
                            RiskLevel.MEDIUM
                            if activity_type == "product_release"
                            else RiskLevel.LOW
                        ),
                        actionable=True,
                        recommendations=[
                            f"Monitor {activity_type} activities closely",
                            "Consider competitive response strategies",
                            "Update market intelligence accordingly",
                        ],
                        metadata={"activity_type": activity_type, "count": count},
                        generated_at=datetime.utcnow(),
                    )
                )

        return insights

    async def _generate_market_trend_insights(self, db: AsyncSession) -> List[Insight]:
        """Generate insights about market trends."""
        insights = []

        # Get emerging trends
        result = await db.execute(select(MarketTrend).where(MarketTrend.status == "emerging"))
        trends = result.scalars().all()

        for trend in trends:
            insights.append(
                Insight(
                    insight_type=InsightType.MARKET_TREND,
                    title=f"Emerging trend: {trend.name}",
                    description=trend.description
                    or f"New trend detected in {trend.industry or 'general market'}",
                    confidence=trend.confidence_level == "high" and 0.8 or 0.6,
                    impact_level=(
                        RiskLevel.HIGH
                        if trend.growth_rate and trend.growth_rate > 20
                        else RiskLevel.MEDIUM
                    ),
                    actionable=True,
                    recommendations=[
                        "Consider strategic positioning for this trend",
                        "Evaluate potential impact on current offerings",
                        "Monitor trend development",
                    ],
                    metadata={"trend_id": trend.id, "growth_rate": trend.growth_rate},
                    generated_at=datetime.utcnow(),
                )
            )

        return insights

    async def _generate_risk_assessment_insights(self, db: AsyncSession) -> List[Insight]:
        """Generate risk assessment insights."""
        insights = []

        # Get recent negative news
        recent_date = datetime.utcnow() - timedelta(days=7)
        result = await db.execute(
            select(CompetitorNews).where(
                and_(
                    CompetitorNews.sentiment == "negative",
                    CompetitorNews.publish_date >= recent_date,
                )
            )
        )
        negative_news = result.scalars().all()

        if len(negative_news) > 3:
            insights.append(
                Insight(
                    insight_type=InsightType.RISK_ASSESSMENT,
                    title="Increased negative sentiment detected",
                    description=f"Detected {len(negative_news)} negative news items in the last 7 days, indicating potential market risks.",
                    confidence=0.7,
                    impact_level=RiskLevel.HIGH,
                    actionable=True,
                    recommendations=[
                        "Monitor competitor responses to negative sentiment",
                        "Review potential impact on your organization",
                        "Prepare contingency plans",
                    ],
                    metadata={"negative_news_count": len(negative_news)},
                    generated_at=datetime.utcnow(),
                )
            )

        return insights

    async def _generate_opportunity_insights(self, db: AsyncSession) -> List[Insight]:
        """Generate opportunity analysis insights."""
        insights = []

        # Get market gaps (areas with low competition)
        # This would be more sophisticated in production

        insights.append(
            Insight(
                insight_type=InsightType.OPPORTUNITY_ANALYSIS,
                title="Market gap analysis opportunity",
                description="Analysis indicates potential opportunities in underserved market segments.",
                confidence=0.6,
                impact_level=RiskLevel.MEDIUM,
                actionable=True,
                recommendations=[
                    "Conduct detailed market gap analysis",
                    "Evaluate feasibility of entering underserved segments",
                    "Develop go-to-market strategy",
                ],
                metadata={"analysis_type": "market_gap"},
                generated_at=datetime.utcnow(),
            )
        )

        return insights


# Global analytics service instance
analytics_service = AnalyticsService()


async def get_analytics_service() -> AnalyticsService:
    """Get the global analytics service instance."""
    return analytics_service

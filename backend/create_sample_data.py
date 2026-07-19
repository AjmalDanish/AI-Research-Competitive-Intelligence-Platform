"""
Create sample data for testing and demonstration.
"""

import asyncio
from datetime import datetime, timedelta, timezone
from app.db.session import AsyncSessionLocal
from app.models.competitor import Competitor, CompetitorActivity, CompetitorProduct, CompetitorNews
from app.models.market import MarketTrend
from app.models.alert import Alert


async def create_sample_data():
    """Create sample data for testing."""
    now = datetime.now(timezone.utc)

    async with AsyncSessionLocal() as session:
        # Create sample competitor
        competitor = Competitor(
            name="TechCorp Industries",
            website="https://techcorp.com",
            industry="Technology",
            sector="Enterprise Software",
            description="Leading provider of enterprise software solutions",
            founded_year=2010,
            headquarters="San Francisco, CA",
            employees=5000,
            revenue=2500000000.0,
            market_cap=15000000000.0,
            tier="large",
            status="active",
            twitter_handle="@techcorp",
            linkedin_url="https://linkedin.com/company/techcorp",
            meta_data={"key_competitor": True, "market_leader": True},
        )

        session.add(competitor)
        await session.flush()
        await session.refresh(competitor)

        # Create sample activities
        activities = [
            CompetitorActivity(
                competitor_id=competitor.id,
                activity_type="product_release",
                title="New AI Platform Launch",
                description="TechCorp announced the launch of their new AI-powered analytics platform",
                activity_date=now - timedelta(days=5),
                detected_date=now - timedelta(days=5),
                source_url="https://techcorp.com/press/new-ai-platform",
                source_type="press_release",
                impact_level="high",
                market_impact="Significant impact on enterprise analytics market",
                processed=True,
                verified=True,
                meta_data={"importance": "high"},
            ),
            CompetitorActivity(
                competitor_id=competitor.id,
                activity_type="partnership",
                title="Strategic Partnership with GlobalCloud",
                description="TechCorp forms strategic partnership with GlobalCloud for cloud services",
                activity_date=now - timedelta(days=15),
                detected_date=now - timedelta(days=15),
                source_url="https://techcrunch.com/techcorp-globalcloud-partnership",
                source_type="news",
                impact_level="medium",
                market_impact="Expands cloud service offerings",
                processed=True,
                verified=True,
                meta_data={"partnership_type": "strategic"},
            ),
        ]

        for activity in activities:
            session.add(activity)

        # Create sample products
        products = [
            CompetitorProduct(
                competitor_id=competitor.id,
                name="Enterprise Analytics Suite",
                description="Complete enterprise analytics and business intelligence platform",
                category="Analytics",
                price=999.0,
                pricing_model="subscription",
                launch_date=now - timedelta(days=365),
                status="active",
                meta_data={"flagship": True, "tier": "enterprise"},
            ),
            CompetitorProduct(
                competitor_id=competitor.id,
                name="Cloud Data Warehouse",
                description="Scalable cloud data warehouse solution",
                category="Data Management",
                price=2499.0,
                pricing_model="subscription",
                launch_date=now - timedelta(days=180),
                status="active",
                meta_data={"flagship": True, "tier": "enterprise"},
            ),
        ]

        for product in products:
            session.add(product)

        # Create sample news
        news_items = [
            CompetitorNews(
                competitor_id=competitor.id,
                title="TechCorp Reports Record Q4 Revenue",
                summary="TechCorp announced record revenue for Q4, beating analyst expectations by 15%",
                content="Full content of the news article would go here...",
                url="https://reuters.com/techcorp-record-q4-revenue",
                source="Reuters",
                published_date=now - timedelta(days=2),
                detected_date=now - timedelta(days=2),
                sentiment="positive",
                sentiment_score=0.8,
                relevance_score=0.9,
                keywords=["revenue", "earnings", "Q4", "growth"],
                processed=True,
                meta_data={"quarter": "Q4", "fiscal_year": 2024},
            ),
            CompetitorNews(
                competitor_id=competitor.id,
                title="TechCorp Acquires AI Startup",
                summary="TechCorp announces acquisition of AI startup for $500M",
                content="Full content of the acquisition article...",
                url="https://techcrunch.com/techcorp-acquires-ai-startup",
                source="TechCrunch",
                published_date=now - timedelta(days=10),
                detected_date=now - timedelta(days=10),
                sentiment="positive",
                sentiment_score=0.7,
                relevance_score=0.85,
                keywords=["acquisition", "AI", "startup", "M&A"],
                processed=True,
                meta_data={"deal_value": 500000000, "acquisition_type": "AI"},
            ),
        ]

        for news_item in news_items:
            session.add(news_item)

        # Create sample market trends
        trends = [
            MarketTrend(
                name="AI Platform Adoption",
                description="Increasing adoption of AI platforms in enterprise",
                category="Technology",
                industry="Software",
                sector="Technology",
                market_segment="Enterprise",
                growth_rate=0.35,
                market_size=15000000000.0,
                forecast_value=20000000000.0,
                forecast_year=2025,
                start_date=now - timedelta(days=90),
                peak_date=now - timedelta(days=30),
                end_date=now,
                detected_date=now - timedelta(days=90),
                trend_direction="up",
                confidence_level="high",
                impact_assessment="Significant market growth expected",
                sources=["Gartner", "Forrester", "IDC"],
                data_points=[
                    {"date": (now - timedelta(days=90)).isoformat(), "value": 100},
                    {"date": (now - timedelta(days=30)).isoformat(), "value": 135},
                ],
                verified=True,
                status="active",
                meta_data={"growth_rate": 0.35, "market_size": 15000000000},
            ),
            MarketTrend(
                name="Cloud Migration Acceleration",
                description="Accelerated cloud migration due to remote work trends",
                category="Cloud Computing",
                industry="Cloud Services",
                sector="Technology",
                market_segment="Enterprise",
                growth_rate=0.45,
                market_size=35000000000.0,
                forecast_value=50000000000.0,
                forecast_year=2025,
                start_date=now - timedelta(days=120),
                peak_date=now - timedelta(days=45),
                end_date=now,
                detected_date=now - timedelta(days=120),
                trend_direction="up",
                confidence_level="high",
                impact_assessment="Major market shift in progress",
                sources=["McKinsey", "Deloitte", "Accenture"],
                data_points=[
                    {"date": (now - timedelta(days=120)).isoformat(), "value": 100},
                    {"date": (now - timedelta(days=45)).isoformat(), "value": 145},
                ],
                verified=True,
                status="active",
                meta_data={"growth_rate": 0.45, "market_size": 35000000000},
            ),
            MarketTrend(
                name="Data Privacy Regulations",
                description="Increasing focus on data privacy and compliance",
                category="Regulatory",
                industry="Legal",
                sector="Compliance",
                market_segment="Enterprise",
                growth_rate=0.25,
                market_size=5000000000.0,
                forecast_value=7000000000.0,
                forecast_year=2025,
                start_date=now - timedelta(days=60),
                peak_date=now,
                end_date=now,
                detected_date=now - timedelta(days=60),
                trend_direction="up",
                confidence_level="medium",
                impact_assessment="Regulatory compliance costs increasing",
                sources=["GDPR", "CCPA", "industry reports"],
                data_points=[
                    {"date": (now - timedelta(days=60)).isoformat(), "value": 100},
                    {"date": now.isoformat(), "value": 125},
                ],
                verified=True,
                status="active",
                meta_data={"regulation_impact": "high", "compliance_costs": 0.25},
            ),
        ]

        for trend in trends:
            session.add(trend)

        # Create sample alerts
        alerts = [
            Alert(
                user_id=1,
                title="Competitor Price Change Detected",
                description="TechCorp reduced pricing for Enterprise Analytics Suite by 20%",
                alert_type="pricing",
                severity="high",
                status="active",
                is_read=False,
                triggered_at=now - timedelta(hours=2),
                meta_data={"competitor": "TechCorp", "price_change": -0.2},
            ),
            Alert(
                user_id=1,
                title="New Product Launch Alert",
                description="TechCorp launched new AI-powered analytics platform",
                alert_type="product",
                severity="medium",
                status="active",
                is_read=False,
                triggered_at=now - timedelta(hours=24),
                meta_data={"competitor": "TechCorp", "product": "AI Platform"},
            ),
            Alert(
                user_id=1,
                title="Market Trend Alert",
                description="AI platform adoption accelerating in enterprise segment",
                alert_type="market",
                severity="medium",
                status="active",
                is_read=True,
                triggered_at=now - timedelta(days=3),
                meta_data={"trend": "AI Adoption", "growth_rate": 0.35},
            ),
        ]

        for alert in alerts:
            session.add(alert)

        await session.commit()

        print("Sample data created successfully!")
        print(f"- Created {len(activities)} competitor activities")
        print(f"- Created {len(products)} competitor products")
        print(f"- Created {len(news_items)} news items")
        print(f"- Created {len(trends)} market trends")
        print(f"- Created {len(alerts)} alerts")
        print(f"- Created 1 competitor (TechCorp Industries)")


if __name__ == "__main__":
    asyncio.run(create_sample_data())

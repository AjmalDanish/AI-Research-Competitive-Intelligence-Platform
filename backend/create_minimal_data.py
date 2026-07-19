"""
Create minimal sample data using SQL queries.
"""

import asyncio
from sqlalchemy import text
from app.db.session import AsyncSessionLocal


async def create_minimal_sample_data():
    """Create minimal sample data for testing."""
    async with AsyncSessionLocal() as session:
        # Create a competitor
        await session.execute(text("""
            INSERT INTO competitors (name, website, industry, status, created_at, updated_at)
            VALUES ('TechCorp Industries', 'https://techcorp.com', 'Technology', 'active', datetime('now'), datetime('now'))
        """))

        # Create some market trends
        await session.execute(text("""
            INSERT INTO market_trends (name, description, category, industry, sector, growth_rate, market_size, start_date, end_date, detected_date, trend_direction, status, created_at, updated_at)
            VALUES 
            ('AI Platform Adoption', 'Increasing adoption of AI platforms in enterprise', 'Technology', 'Software', 'Technology', 0.35, 15000000000.0, datetime('now', '-90 days'), datetime('now'), datetime('now', '-90 days'), 'up', 'active', datetime('now'), datetime('now')),
            ('Cloud Migration Acceleration', 'Accelerated cloud migration due to remote work trends', 'Cloud Computing', 'Cloud Services', 'Technology', 0.45, 35000000000.0, datetime('now', '-120 days'), datetime('now'), datetime('now', '-120 days'), 'up', 'active', datetime('now'), datetime('now)'),
            ('Data Privacy Regulations', 'Increasing focus on data privacy and compliance', 'Regulatory', 'Legal', 'Compliance', 0.25, 5000000000.0, datetime('now', '-60 days'), datetime('now'), datetime('now', '-60 days'), 'up', 'active', datetime('now'), datetime('now)')
        """))

        # Create some alerts
        await session.execute(text("""
            INSERT INTO alerts (user_id, alert_type, severity, status, is_read, triggered_at, created_at, updated_at)
            VALUES 
            (1, 'pricing', 'high', 'active', 0, datetime('now', '-2 hours'), datetime('now'), datetime('now')),
            (1, 'product', 'medium', 'active', 0, datetime('now', '-24 hours'), datetime('now'), datetime('now')),
            (1, 'market', 'medium', 'active', 1, datetime('now', '-3 days'), datetime('now'), datetime('now'))
        """))

        await session.commit()
        print("Minimal sample data created successfully!")
        print("✅ Created 1 competitor")
        print("✅ Created 3 market trends")
        print("✅ Created 3 alerts")


if __name__ == "__main__":
    asyncio.run(create_minimal_sample_data())

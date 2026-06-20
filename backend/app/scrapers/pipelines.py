"""
Scrapy pipelines for storing scraped data into PostgreSQL.
"""
import asyncio
from datetime import datetime
from typing import Dict, Any
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.core.config import settings
from app.models.models import Lead, LeadStatus


class DatabasePipeline:
    """
    Pipeline to store scraped companies in PostgreSQL leads table.

    - Checks for duplicates by website or company_name
    - Stores raw scraped data in scraped_data JSON column
    - Sets status to 'new'
    """

    def __init__(self):
        self.engine = None
        self.session_factory = None

    async def async_open_spider(self, spider):
        """Initialize database connection when spider opens."""
        self.engine = create_async_engine(
            settings.DATABASE_URL,
            pool_pre_ping=True,
            pool_size=5,
        )
        self.session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        spider.logger.info("Database pipeline initialized")

    async def async_close_spider(self, spider):
        """Close database connection when spider closes."""
        if self.engine:
            await self.engine.dispose()
            spider.logger.info("Database pipeline closed")

    async def async_process_item(self, item: Dict[str, Any], spider):
        """
        Process scraped item and store in database.

        Returns the item if stored successfully, drops it if duplicate.
        """
        async with self.session_factory() as session:
            try:
                # Extract fields
                company_name = item.get('company_name')
                website = item.get('website')

                if not company_name:
                    spider.logger.warning("Skipping item without company_name")
                    return None

                # Check for duplicates
                duplicate_query = select(Lead).where(
                    or_(
                        Lead.website == website if website else False,
                        Lead.company_name == company_name
                    )
                )
                result = await session.execute(duplicate_query)
                existing = result.scalar_one_or_none()

                if existing:
                    spider.logger.debug(f"Duplicate found: {company_name}")
                    return None

                # Create new lead
                new_lead = Lead(
                    company_name=company_name,
                    website=website,
                    country=item.get('country'),
                    city=item.get('city'),
                    sector=item.get('sector'),
                    status=LeadStatus.new,
                    scraped_data={
                        item.get('source', 'unknown'): {
                            'phone': item.get('phone'),
                            'description': item.get('description'),
                            'source_url': item.get('source_url'),
                            'scraped_at': datetime.utcnow().isoformat(),
                        }
                    }
                )

                session.add(new_lead)
                await session.commit()

                spider.logger.info(f"Stored: {company_name} from {item.get('source')}")
                return item

            except Exception as e:
                await session.rollback()
                spider.logger.error(f"Error storing item: {e}")
                return None

    # Scrapy will call async methods directly if they exist
    # No sync wrappers needed - Scrapy detects and uses async_* methods automatically

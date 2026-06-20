"""
Pipeline for storing hiring signals (new_hire) from job boards.

Creates LeadSignal records when companies are hiring engineering roles.
Links signals to existing leads by matching company name.
"""
import asyncio
from datetime import datetime
from typing import Dict, Any
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.core.config import settings
from app.models.models import Lead, LeadSignal


class SignalsPipeline:
    """
    Pipeline to store hiring signals and link them to existing leads.

    When a company is found hiring engineers:
    1. Try to match to existing lead by company name
    2. Create LeadSignal with signal_type=new_hire
    3. If company doesn't exist, skip (will be created by directories spider)
    """

    def __init__(self):
        self.engine = None
        self.session_factory = None

    async def async_open_spider(self, spider):
        """Initialize database connection."""
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
        spider.logger.info("Signals pipeline initialized")

    async def async_close_spider(self, spider):
        """Close database connection."""
        if self.engine:
            await self.engine.dispose()
            spider.logger.info("Signals pipeline closed")

    async def async_process_item(self, item: Dict[str, Any], spider):
        """
        Process hiring signal and create LeadSignal.

        Item should have:
        - signal_type: 'new_hire'
        - company_name: name of hiring company
        - job_title: role being hired
        - source, source_url
        """
        if item.get('signal_type') != 'new_hire':
            # Not a signal item, pass through
            return item

        async with self.session_factory() as session:
            try:
                company_name = item.get('company_name')
                if not company_name:
                    spider.logger.warning("Signal without company_name, skipping")
                    return None

                # Try to find matching lead
                # Match by exact name or partial match
                query = select(Lead).where(
                    or_(
                        Lead.company_name.ilike(f"%{company_name}%"),
                        Lead.company_name == company_name
                    )
                )
                result = await session.execute(query)
                lead = result.scalar_one_or_none()

                if not lead:
                    spider.logger.debug(f"No matching lead for hiring signal: {company_name}")
                    # Don't create signal if lead doesn't exist yet
                    return None

                # Check if we already have this signal (avoid duplicates)
                existing_signal_query = select(LeadSignal).where(
                    LeadSignal.lead_id == lead.id,
                    LeadSignal.signal_type == 'new_hire',
                    LeadSignal.title.ilike(f"%{item.get('job_title', '')}%")
                )
                existing = await session.execute(existing_signal_query)
                if existing.scalar_one_or_none():
                    spider.logger.debug(f"Signal already exists for {company_name}")
                    return None

                # Create new hiring signal
                signal = LeadSignal(
                    lead_id=lead.id,
                    signal_type='new_hire',
                    title=f"Hiring {item.get('job_title', 'engineering role')}",
                    detail=item.get('detail', ''),
                    source_url=item.get('source_url'),
                    detected_at=datetime.utcnow()
                )

                session.add(signal)
                await session.commit()

                spider.logger.info(
                    f"✅ Created hiring signal: {company_name} - {item.get('job_title')}"
                )

                return item

            except Exception as e:
                await session.rollback()
                spider.logger.error(f"Error creating signal: {e}")
                return None

    # Scrapy will call async methods directly if they exist
    # No sync wrappers needed - Scrapy detects and uses async_* methods automatically

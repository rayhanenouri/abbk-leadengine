"""
Pipeline for storing all types of signals.

Creates LeadSignal records for:
- new_hire: hiring signals from job boards
- news: business news mentions
- funding: funding announcements
- export_signal: export contracts
- audit_signal: ISO/certification mentions
- multinational_signal: multinational company indicators

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
    Pipeline to store all types of signals and link them to existing leads.

    Process flow:
    1. Try to match to existing lead by company name
    2. Create LeadSignal with appropriate signal_type
    3. If company doesn't exist, skip (will be created by directories spider)
    4. Avoid duplicate signals for same company/type/title
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
        Process any type of signal and create LeadSignal.

        Item should have:
        - signal_type: 'new_hire', 'news', 'funding', 'export_signal', etc.
        - company_name: name of company
        - title: signal title
        - detail: (optional) detailed description
        - source_url: (optional) source URL
        """
        signal_type = item.get('signal_type')

        # Valid signal types
        valid_signals = [
            'new_hire', 'news', 'funding', 'export_signal', 'audit_signal',
            'multinational_signal', 'tender_detected', 'event_attendance',
            'training_detected', 'logo_detected', 'role_detected',
        ]

        if signal_type not in valid_signals:
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

                # Build signal title based on type
                if signal_type == 'new_hire':
                    title = f"Hiring {item.get('job_title', 'engineering role')}"
                else:
                    title = item.get('title', f"{signal_type.replace('_', ' ').title()} detected")

                # Check if we already have similar signal (avoid duplicates)
                existing_signal_query = select(LeadSignal).where(
                    LeadSignal.lead_id == lead.id,
                    LeadSignal.signal_type == signal_type,
                    LeadSignal.title == title[:500]  # Match first 500 chars
                )
                existing = await session.execute(existing_signal_query)
                if existing.scalar_one_or_none():
                    spider.logger.debug(f"Signal already exists: {company_name} - {signal_type}")
                    return None

                # Create new signal
                signal = LeadSignal(
                    lead_id=lead.id,
                    signal_type=signal_type,
                    title=title[:500],  # Truncate to 500 chars (DB limit)
                    detail=item.get('detail', '')[:1000] if item.get('detail') else None,  # Truncate detail
                    source_url=item.get('source_url'),
                    detected_at=datetime.utcnow()
                )

                session.add(signal)

                # Special handling for signals with audit requirements
                if item.get('has_audit_requirement'):
                    # Set under_audit flag on lead (funding, tenders, etc.)
                    from sqlalchemy import update as sql_update
                    await session.execute(
                        sql_update(Lead)
                        .where(Lead.id == lead.id)
                        .values(under_audit=True)
                    )

                    audit_reason = "international funding" if signal_type == 'funding' else "public tender"
                    spider.logger.info(
                        f"🔍 Set under_audit=True for {company_name} ({audit_reason} detected)"
                    )

                await session.commit()

                spider.logger.info(
                    f"✅ Created {signal_type} signal: {company_name} - {title[:50]}"
                )

                # Trigger automatic score recalculation for this lead
                try:
                    from app.workers.tasks.scoring import calculate_lead_score
                    calculate_lead_score.delay(lead.id)
                    spider.logger.info(f"🔄 Triggered score recalculation for lead {lead.id}")
                except Exception as e:
                    spider.logger.warning(f"Failed to trigger score recalculation: {e}")

                return item

            except Exception as e:
                await session.rollback()
                spider.logger.error(f"Error creating signal: {e}")
                return None

    # Scrapy will call async methods directly if they exist
    # No sync wrappers needed - Scrapy detects and uses async_* methods automatically

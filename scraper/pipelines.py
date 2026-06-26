"""
Scrapy Pipeline to save signals to PostgreSQL database
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from app.db.session import AsyncSessionLocal
from app.models.models import Lead, LeadSignal
from sqlalchemy import select
from datetime import datetime


class LeadSignalPipeline:
    """Pipeline to save scraped signals to database"""

    def process_item(self, item, spider):
        """Process each scraped item - run sync"""
        import asyncio
        try:
            # Try to get existing loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Create new thread with new loop
                import threading
                result = [None]
                def run():
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    result[0] = new_loop.run_until_complete(self.save_to_db(item))
                    new_loop.close()

                thread = threading.Thread(target=run)
                thread.start()
                thread.join()
            else:
                loop.run_until_complete(self.save_to_db(item))
        except RuntimeError:
            # No loop, create one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.save_to_db(item))
            loop.close()

        return item

    async def save_to_db(self, item):
        """Save signal to database"""

        async with AsyncSessionLocal() as db:
            # Find or create lead
            company_name = item.get('company_name', '').strip()

            if not company_name or len(company_name) < 3:
                return

            # Search for existing lead
            result = await db.execute(
                select(Lead).where(Lead.company_name.ilike(f'%{company_name}%'))
            )
            lead = result.scalar_one_or_none()

            # Create new lead if not found
            if not lead:
                lead = Lead(
                    company_name=company_name,
                    sector=item.get('sector', 'Engineering'),
                    city=item.get('city', 'Tunis'),
                    country='Tunisia',
                    website=item.get('website'),
                    status='new',
                    scraped_data={
                        'source': item.get('source_site', 'scraper'),
                        'found_at': item.get('found_at', datetime.now().isoformat())
                    }
                )
                db.add(lead)
                await db.flush()

            # Add signal if signal_type exists
            if 'signal_type' in item:
                # Check for duplicate signal
                existing_signal = await db.execute(
                    select(LeadSignal).where(
                        LeadSignal.lead_id == lead.id,
                        LeadSignal.signal_type == item['signal_type'],
                        LeadSignal.source_url == item.get('source_url', '')
                    )
                )

                if not existing_signal.scalar_one_or_none():
                    signal = LeadSignal(
                        lead_id=lead.id,
                        signal_type=item['signal_type'],
                        title=item.get('title', 'Signal detected'),
                        detail=item.get('detail', ''),
                        source_url=item.get('source_url', ''),
                        detected_at=datetime.now()
                    )
                    db.add(signal)

            await db.commit()

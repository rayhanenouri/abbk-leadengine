#!/usr/bin/env python3
"""
Recalculate all scores with hiring signals included.
"""
import asyncio
from sqlalchemy import select, delete
from app.db.session import AsyncSessionLocal
from app.models.models import Lead, LeadScore, Service
from app.services.scoring_engine import score_lead


async def rescore_all():
    """Delete old scores and recalculate with hiring signals."""
    async with AsyncSessionLocal() as session:
        print("=" * 60)
        print("Recalculating scores with hiring signals...")
        print("=" * 60)
        print()

        # Delete old scores
        print("Deleting old scores...")
        await session.execute(delete(LeadScore))
        await session.commit()
        print("✅ Old scores deleted\n")

        # Get services
        services_result = await session.execute(
            select(Service).where(Service.is_active == True)
        )
        services = services_result.scalars().all()

        # Get all leads WITH their signals (eager load)
        from sqlalchemy.orm import selectinload
        leads_result = await session.execute(
            select(Lead).options(selectinload(Lead.signals))
        )
        leads = leads_result.scalars().all()

        print(f"Scoring {len(leads)} leads against {len(services)} services...")
        print()

        total_scores = 0
        leads_with_hiring = 0

        for lead in leads:
            # Check if lead has hiring signals
            has_hiring = any(s.signal_type == 'new_hire' for s in lead.signals)
            if has_hiring:
                leads_with_hiring += 1
                print(f"🔥 {lead.company_name} - HAS HIRING SIGNAL")

            scores = await score_lead(lead, services, session)
            total_scores += len(scores)

        await session.commit()

        print()
        print("=" * 60)
        print("✅ Rescoring complete!")
        print(f"   Leads scored:       {len(leads)}")
        print(f"   With hiring signals: {leads_with_hiring}")
        print(f"   Services:           {len(services)}")
        print(f"   Total scores:       {total_scores}")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(rescore_all())

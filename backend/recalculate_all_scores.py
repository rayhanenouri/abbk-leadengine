#!/usr/bin/env python3
"""
Recalculate scores for all leads in the database.
"""
import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.models.models import Lead, LeadScore, Service
from app.services.scoring_engine import score_lead


async def recalculate_all_scores():
    """Recalculate scores for all leads."""

    # Create database connection
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Get all leads with signals eagerly loaded
        leads_result = await session.execute(
            select(Lead).options(selectinload(Lead.signals))
        )
        leads = leads_result.scalars().all()

        print(f"Found {len(leads)} leads to score")

        # Get all active services
        services_result = await session.execute(
            select(Service).where(Service.is_active == True)
        )
        services = services_result.scalars().all()

        print(f"Found {len(services)} active ABBK services")

        # Delete all existing scores
        print("Deleting old scores...")
        await session.execute(delete(LeadScore))
        await session.commit()

        # Calculate scores for each lead
        total_scores = 0
        for i, lead in enumerate(leads, 1):
            print(f"[{i}/{len(leads)}] Scoring {lead.company_name}...")

            new_scores = await score_lead(lead, services, session)
            total_scores += len(new_scores)

            if i % 10 == 0:
                await session.commit()
                print(f"  Progress: {i}/{len(leads)} leads, {total_scores} scores")

        # Final commit
        await session.commit()

        print("\n" + "="*60)
        print(f"✅ Scoring complete!")
        print(f"   Total leads: {len(leads)}")
        print(f"   Total scores: {total_scores}")
        print(f"   Avg scores per lead: {total_scores/len(leads):.1f}")
        print("="*60)

    await engine.dispose()


if __name__ == '__main__':
    asyncio.run(recalculate_all_scores())

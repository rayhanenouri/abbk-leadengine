#!/usr/bin/env python3
"""Recalculate all scores after seeding signals"""

import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.db.session import AsyncSessionLocal
from app.models.models import Lead, LeadScore, LeadSignal, Service
from app.services.scoring_engine import calculate_score_for_service
from sqlalchemy import select, delete

async def recalc():
    print("🔄 Recalculating scores for all 380 leads...\n")

    async with AsyncSessionLocal() as db:
        # Get all services
        services_result = await db.execute(select(Service))
        services = services_result.scalars().all()
        print(f"   Found {len(services)} ABBK services\n")

        # Get all leads
        leads_result = await db.execute(select(Lead))
        leads = leads_result.scalars().all()
        print(f"   Found {len(leads)} companies\n")

        scored = 0

        for idx, lead in enumerate(leads):
            # Get signals
            signals_result = await db.execute(
                select(LeadSignal).where(LeadSignal.lead_id == lead.id)
            )
            signals = list(signals_result.scalars().all())

            # Delete old scores
            await db.execute(delete(LeadScore).where(LeadScore.lead_id == lead.id))

            # Calculate new scores
            for service in services:
                score_data = await calculate_score_for_service(lead, service, signals, db)

                score_record = LeadScore(
                    lead_id=lead.id,
                    service_id=service.id,
                    service_type=service.service_type,
                    service_name=service.name,
                    score=score_data['score'],
                    reasoning=score_data['reasoning'],
                    signal_breakdown=score_data['signal_breakdown']
                )
                db.add(score_record)

            scored += 1
            if scored % 50 == 0:
                print(f"   ✓ Scored {scored}/{len(leads)} companies...")
                await db.commit()

        await db.commit()

        # Stats
        scores_result = await db.execute(select(LeadScore))
        all_scores = list(scores_result.scalars().all())

        hot = len([s for s in all_scores if s.score >= 60])
        high = len([s for s in all_scores if s.score >= 70])

        print(f"\n✅ Scoring complete!")
        print(f"   Total scores: {len(all_scores)}")
        print(f"   🔥 Hot leads (60+): {hot}")
        print(f"   🔥 High priority (70+): {high}")

if __name__ == "__main__":
    asyncio.run(recalc())

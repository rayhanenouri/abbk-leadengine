"""
Score all leads that don't have scores yet.
Run this after importing a database.
"""
import asyncio
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.models import Lead, LeadScore
from app.services.scoring_engine import score_lead

async def score_all_unscored_leads():
    """Score all leads that don't have any scores."""
    # Use sync engine
    sync_engine = create_engine(settings.DATABASE_URL.replace('+asyncpg', ''))

    with Session(sync_engine) as session:
        # Find all leads without scores
        subquery = select(LeadScore.lead_id).distinct()
        leads_without_scores = session.query(Lead).filter(
            ~Lead.id.in_(subquery)
        ).all()

        print(f"Found {len(leads_without_scores)} leads without scores")

        # Also find leads with scores for comparison
        leads_with_scores = session.query(Lead).filter(
            Lead.id.in_(subquery)
        ).count()

        print(f"Leads with scores: {leads_with_scores}")
        print(f"Leads without scores: {len(leads_without_scores)}")

        if not leads_without_scores:
            print("All leads already have scores!")
            return

        # Score each lead
        from app.db.session import AsyncSessionLocal
        async with AsyncSessionLocal() as async_session:
            for idx, lead in enumerate(leads_without_scores, 1):
                try:
                    print(f"Scoring {idx}/{len(leads_without_scores)}: {lead.company_name}")
                    await score_lead(async_session, lead.id)

                    if idx % 10 == 0:
                        print(f"Progress: {idx}/{len(leads_without_scores)} ({idx/len(leads_without_scores)*100:.1f}%)")

                except Exception as e:
                    print(f"Error scoring {lead.company_name}: {e}")
                    continue

            await async_session.commit()

        print(f"\nCompleted! Scored {len(leads_without_scores)} leads")

if __name__ == "__main__":
    asyncio.run(score_all_unscored_leads())

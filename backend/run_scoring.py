#!/usr/bin/env python3
"""
Run scoring engine on all leads in database.
"""
import asyncio
from app.db.session import AsyncSessionLocal
from app.services.scoring_engine import score_all_leads


async def main():
    """Score all leads against all active services."""
    print("=" * 60)
    print("ABBK LeadEngine - Scoring Engine")
    print("=" * 60)
    print()

    async with AsyncSessionLocal() as session:
        print("Starting scoring process...")
        result = await score_all_leads(session)

        print()
        print("=" * 60)
        print("✅ Scoring complete!")
        print(f"   Leads scored:    {result['leads_scored']}")
        print(f"   Services:        {result['services']}")
        print(f"   Scores created:  {result['scores_created']}")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

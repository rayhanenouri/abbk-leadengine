#!/usr/bin/env python3
"""
Recalculate all lead scores using the ADVANCED WEIGHTED SIGNAL SCORING ENGINE.

This script:
1. Loads all 121 leads from the database
2. Detects signals for each lead (from lead_signals table + boolean flags)
3. Loads all 21 ABBK services with their scoring_weights
4. Calculates weighted scores using service-specific weights
5. Normalizes scores to 0-100 scale
6. Generates detailed reasoning for each score
7. Stores updated scores in lead_scores table

Usage:
    cd backend
    python recalculate_scores_advanced.py
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from app.db.session import AsyncSessionLocal
from app.services.scoring_engine import score_all_leads
from sqlalchemy import select as sql_select, func, desc
from app.models.models import Lead, LeadScore, Service


async def main():
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║   ABBK LeadEngine - Advanced Weighted Signal Scoring        ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")

    async with AsyncSessionLocal() as db:
        # Get counts before scoring
        leads_count = await db.scalar(sql_select(func.count()).select_from(Lead))
        services_count = await db.scalar(
            sql_select(func.count()).select_from(Service).where(Service.is_active == True)
        )
        old_scores_count = await db.scalar(sql_select(func.count()).select_from(LeadScore))

        print(f"📊 Database Status:")
        print(f"   • {leads_count} leads in database")
        print(f"   • {services_count} active ABBK services")
        print(f"   • {old_scores_count} old scores (will be replaced)")
        print()

        # Run advanced scoring engine
        print("🚀 Starting advanced weighted signal scoring...\n")

        result = await score_all_leads(db)

        print("\n✅ Scoring complete!\n")
        print(f"📈 Results:")
        print(f"   • {result['leads_scored']} leads scored")
        print(f"   • {result['services']} ABBK services")
        print(f"   • {result['scores_created']} total scores created")
        print(f"   • {result['leads_with_signals']} leads have detected signals")
        print(f"   • {result['scores_created'] // result['leads_scored']} scores per lead")
        print()

        # Get top 10 leads
        top_leads_query = (
            sql_select(
                Lead.company_name,
                Lead.sector,
                Lead.city,
                func.max(LeadScore.score).label('best_score'),
                func.count(LeadScore.id).label('score_count')
            )
            .join(LeadScore, Lead.id == LeadScore.lead_id)
            .group_by(Lead.id, Lead.company_name, Lead.sector, Lead.city)
            .order_by(desc('best_score'))
            .limit(10)
        )

        result_top = await db.execute(top_leads_query)
        top_leads = result_top.all()

        print("🏆 Top 10 Leads by Best Score:")
        print()
        for idx, (name, sector, city, score, count) in enumerate(top_leads, 1):
            print(f"{idx:2}. {name[:40]:40} | Score: {score:5.1f}/100 | {sector[:25]:25} | {city}")

        print()
        print("💡 Next steps:")
        print("   1. Open dashboard: http://localhost:5173")
        print("   2. Login: admin@abbk.tn / admin123")
        print("   3. View ranked leads with new scores")
        print("   4. Click any lead to see detailed score breakdown")
        print()


if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""
Final cleanup of junk navigation/page entries.

These are scraped from website navigation menus and are not real companies.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, delete
from app.db.session import AsyncSessionLocal
from app.models.models import Lead, LeadScore, LeadSignal, ScoreHistory, Notification, LeadStatusHistory


# Exact company names that are junk (navigation items, page titles)
JUNK_EXACT_NAMES = [
    "Aller au contenu principal",
    "Les événements",
    "privacy policy",
    "Membres",
    "History",
    "Accès aux marchés",
    "Our News",
    "Adhésion",
    "Coopération internationale",
    "Events & Gallery",
    "Plateforme Mécanique",
    "Publications de l'APII",
    "Salon virtuel de l'industrie Tunisienne",
    "API publications",
    "Nos marchés cibles",
    "Ranking ENR 2021 (Engineering News Record)",
]

# Company names containing these patterns (partial matches)
JUNK_PATTERNS = [
    "contenu principal",
    "événement",
    "privacy policy",
    "cookie",
    "terms of use",
    "mentions légales",
    "contact us",
    "about us",
    "notre histoire",
    "qui sommes nous",
]


async def final_cleanup():
    """Delete all junk navigation/page entries."""

    print("\n" + "=" * 70)
    print("🧹 FINAL CLEANUP — REMOVING JUNK NAVIGATION ENTRIES")
    print("=" * 70)

    async with AsyncSessionLocal() as db:
        # Count before
        result = await db.execute(select(Lead))
        total_before = len(result.scalars().all())

        print(f"\n📊 Companies before cleanup: {total_before}")

        # Get all junk lead IDs
        result = await db.execute(
            select(Lead.id, Lead.company_name).where(
                Lead.company_name.in_(JUNK_EXACT_NAMES)
            )
        )
        junk_leads = result.fetchall()

        if not junk_leads:
            print("✅ No junk entries found!")
            return

        junk_ids = [lead[0] for lead in junk_leads]

        print(f"\n🗑️  Found {len(junk_ids)} junk entries to delete:\n")
        for lead_id, name in junk_leads:
            print(f"   • {name}")

        # Delete related records first (in correct order for foreign keys)
        print(f"\n🔄 Deleting related records...")

        # Delete notifications
        result = await db.execute(
            delete(Notification).where(Notification.lead_id.in_(junk_ids))
        )
        notif_deleted = result.rowcount
        print(f"   ✅ Deleted {notif_deleted} notifications")

        # Delete lead status history
        result = await db.execute(
            delete(LeadStatusHistory).where(LeadStatusHistory.lead_id.in_(junk_ids))
        )
        status_history_deleted = result.rowcount
        print(f"   ✅ Deleted {status_history_deleted} status history records")

        # Delete score history
        result = await db.execute(
            delete(ScoreHistory).where(ScoreHistory.lead_id.in_(junk_ids))
        )
        score_history_deleted = result.rowcount
        print(f"   ✅ Deleted {score_history_deleted} score history records")

        # Delete scores
        result = await db.execute(
            delete(LeadScore).where(LeadScore.lead_id.in_(junk_ids))
        )
        scores_deleted = result.rowcount
        print(f"   ✅ Deleted {scores_deleted} scores")

        # Delete signals
        result = await db.execute(
            delete(LeadSignal).where(LeadSignal.lead_id.in_(junk_ids))
        )
        signals_deleted = result.rowcount
        print(f"   ✅ Deleted {signals_deleted} signals")

        # Delete leads
        result = await db.execute(
            delete(Lead).where(Lead.id.in_(junk_ids))
        )
        leads_deleted = result.rowcount

        await db.commit()

        # Count after
        result = await db.execute(select(Lead))
        total_after = len(result.scalars().all())

        print(f"\n✅ CLEANUP COMPLETE!")
        print(f"   Companies deleted: {leads_deleted}")
        print(f"   Scores deleted: {scores_deleted}")
        print(f"   Signals deleted: {signals_deleted}")
        print(f"   Remaining companies: {total_after}")

        # Show sample of remaining companies
        result = await db.execute(
            select(Lead.company_name, Lead.website, Lead.sector)
            .where(Lead.website.isnot(None))
            .limit(15)
        )

        print(f"\n📋 Sample of remaining REAL companies:\n")
        for row in result:
            print(f"   ✓ {row.company_name[:40]:40} — {row.sector or 'No sector':15}")

        # Count by website status
        result = await db.execute(
            select(Lead).where(Lead.website.isnot(None))
        )
        with_website = len(result.scalars().all())

        without_website = total_after - with_website

        print(f"\n📊 FINAL DATABASE STATISTICS:")
        print(f"   Total companies: {total_after}")
        print(f"   🌐 WITH websites: {with_website} ({with_website / total_after * 100:.1f}%)")
        print(f"   ❓ WITHOUT websites: {without_website} ({without_website / total_after * 100:.1f}%)")

        print("\n" + "=" * 70)
        print("✅ DATABASE IS CLEAN — READY FOR DEMO!")
        print("=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(final_cleanup())

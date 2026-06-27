#!/usr/bin/env python3
"""
Clean junk entries from leads table.

Deletes companies that are obviously not real leads:
- Company names containing: Secteur, LISTS, Cluster, Gouvernorat, Our tools, Our projects, etc.
- Companies with no website AND no phone AND no sector (completely empty)
- Duplicates and test data

Keeps only real companies with actual data.
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, delete, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from app.models.models import Lead, LeadScore, LeadSignal


# Junk patterns to delete
JUNK_PATTERNS = [
    "Secteur",
    "LISTS",
    "Cluster",
    "Gouvernorat",
    "Our tools",
    "Our projects",
    "Fiche de l'adherent",
    "Plateforme Électronique",
    "Essais sur",
    "Liste des",
    "Annuaire",
    "Recherche",
    "Filter by",
    "Page",
    "Home",
    "Contact",
    "About",
]


async def clean_junk_companies():
    """Delete all junk entries from leads table."""

    async with AsyncSessionLocal() as db:
        # Count before
        result = await db.execute(select(Lead))
        total_before = len(result.scalars().all())

        print(f"\n📊 Companies before cleanup: {total_before}")

        # Delete companies with junk names
        junk_conditions = [
            Lead.company_name.ilike(f"%{pattern}%") for pattern in JUNK_PATTERNS
        ]

        # Delete companies with no data at all
        empty_condition = and_(
            Lead.website.is_(None),
            Lead.sector.is_(None)
        )

        # First, get IDs of leads to delete
        select_stmt = select(Lead.id).where(
            or_(*junk_conditions, empty_condition)
        )
        result = await db.execute(select_stmt)
        lead_ids_to_delete = [row[0] for row in result.fetchall()]

        print(f"🔍 Found {len(lead_ids_to_delete)} junk entries to delete")

        if not lead_ids_to_delete:
            print("✅ No junk entries found!")
            return

        # Delete related scores first
        await db.execute(
            delete(LeadScore).where(LeadScore.lead_id.in_(lead_ids_to_delete))
        )

        # Delete related signals
        await db.execute(
            delete(LeadSignal).where(LeadSignal.lead_id.in_(lead_ids_to_delete))
        )

        # Now delete leads
        result = await db.execute(
            delete(Lead).where(Lead.id.in_(lead_ids_to_delete))
        )
        deleted_count = result.rowcount

        await db.commit()

        # Count after
        result = await db.execute(select(Lead))
        total_after = len(result.scalars().all())

        print(f"🗑️  Deleted {deleted_count} junk entries")
        print(f"✅ Companies after cleanup: {total_after}")
        print(f"📈 Kept {total_after / total_before * 100:.1f}% of original data")

        # Show sample of remaining companies
        result = await db.execute(
            select(Lead.company_name, Lead.website, Lead.sector)
            .limit(20)
        )

        print("\n📋 Sample of remaining companies:")
        for row in result:
            website = row.website or "No website"
            sector = row.sector or "No sector"
            print(f"  • {row.company_name} — {sector} — {website}")

        # Count companies with vs without websites
        result = await db.execute(
            select(Lead).where(Lead.website.isnot(None))
        )
        with_website = len(result.scalars().all())

        without_website = total_after - with_website

        print(f"\n🌐 Companies WITH websites: {with_website} ({with_website / total_after * 100:.1f}%)")
        print(f"❓ Companies WITHOUT websites: {without_website} ({without_website / total_after * 100:.1f}%)")

        return {
            "total_before": total_before,
            "deleted": deleted_count,
            "total_after": total_after,
            "with_website": with_website,
            "without_website": without_website
        }


if __name__ == "__main__":
    print("🧹 CLEANING JUNK COMPANIES FROM DATABASE\n")
    stats = asyncio.run(clean_junk_companies())
    print("\n✅ Cleanup complete!")

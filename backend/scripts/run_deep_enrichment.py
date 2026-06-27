#!/usr/bin/env python3
"""
Run Deep Enrichment Pipeline

Complete workflow:
1. Clean junk companies from database
2. Mark companies without websites as 'unverified'
3. Deep enrich all companies WITH websites
4. Recalculate all scores with real intelligence
5. Show statistics and top leads

This is the CORE workflow that creates real business value.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, update, delete, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from app.models.models import Lead, LeadSignal, LeadScore
from app.scrapers.utils.deep_enricher import DeepCompanyEnricher
from app.services.scoring_engine import score_all_leads
from datetime import datetime


# Junk patterns
JUNK_PATTERNS = [
    "Secteur", "LISTS", "Cluster", "Gouvernorat", "Our tools", "Our projects",
    "Fiche de l'adherent", "Plateforme Électronique", "Essais sur",
    "Liste des", "Annuaire", "Recherche", "Filter by", "Page", "Home",
    "Contact", "About", "Adhérents", "Members", "Directory", "Catégorie"
]


async def step1_clean_junk():
    """Step 1: Clean junk companies."""

    print("\n" + "=" * 60)
    print("STEP 1: CLEAN JUNK COMPANIES")
    print("=" * 60)

    async with AsyncSessionLocal() as db:
        # Count before
        result = await db.execute(select(Lead))
        total_before = len(result.scalars().all())

        print(f"📊 Companies before: {total_before}")

        # Delete junk
        junk_conditions = [Lead.company_name.ilike(f"%{p}%") for p in JUNK_PATTERNS]
        empty_condition = and_(
            Lead.website.is_(None),
            Lead.sector.is_(None)
        )

        # First get IDs to delete
        select_stmt = select(Lead.id).where(or_(*junk_conditions, empty_condition))
        result = await db.execute(select_stmt)
        lead_ids_to_delete = [row[0] for row in result.fetchall()]

        if lead_ids_to_delete:
            # Delete related records first
            await db.execute(delete(LeadScore).where(LeadScore.lead_id.in_(lead_ids_to_delete)))
            await db.execute(delete(LeadSignal).where(LeadSignal.lead_id.in_(lead_ids_to_delete)))

            # Delete leads
            result = await db.execute(delete(Lead).where(Lead.id.in_(lead_ids_to_delete)))
            deleted = result.rowcount
        else:
            deleted = 0

        await db.commit()

        # Count after
        result = await db.execute(select(Lead))
        total_after = len(result.scalars().all())

        print(f"🗑️  Deleted: {deleted} junk entries")
        print(f"✅ Remaining: {total_after} real companies")

        return total_after


async def step2_mark_unverified():
    """Step 2: Count companies without websites (skip marking - no 'unverified' status in enum)."""

    print("\n" + "=" * 60)
    print("STEP 2: COUNT UNVERIFIED LEADS")
    print("=" * 60)

    async with AsyncSessionLocal() as db:
        # Just count companies without websites
        result = await db.execute(
            select(Lead).where(Lead.website.is_(None))
        )

        count = len(result.scalars().all())

        print(f"❓ {count} companies WITHOUT websites (will have low scores)")
        print(f"   They stay in 'new' status - low priority for enrichment")

        return count


async def step3_deep_enrichment():
    """Step 3: Deep enrichment for all companies with websites."""

    print("\n" + "=" * 60)
    print("STEP 3: DEEP ENRICHMENT (CORE VALUE)")
    print("=" * 60)

    async with AsyncSessionLocal() as db:
        # Get companies with websites
        result = await db.execute(
            select(Lead).where(Lead.website.isnot(None))
        )
        leads = result.scalars().all()

        total = len(leads)
        enriched = 0
        errors = 0

        print(f"\n🔍 Enriching {total} companies with websites...\n")

        enricher = DeepCompanyEnricher()

        for i, lead in enumerate(leads, 1):
            try:
                print(f"[{i}/{total}] {lead.company_name}...")

                # Run enrichment
                enrichment_data = await enricher.enrich_company(
                    company_id=lead.id,
                    company_name=lead.company_name,
                    website=lead.website
                )

                # Store in database
                if not lead.scraped_data:
                    lead.scraped_data = {}

                lead.scraped_data["deep_enrichment"] = enrichment_data

                # Update flags
                signals = enrichment_data.get("signals", {})

                if signals.get("is_multinational"):
                    lead.is_multinational = True

                if signals.get("is_exporter"):
                    lead.is_exporter = True

                if signals.get("has_iso_certification"):
                    lead.under_audit = True

                if signals.get("employee_count"):
                    lead.employee_count = signals["employee_count"]

                # Create signals
                signals_created = 0

                if signals.get("is_hiring_engineers"):
                    for job in signals.get("job_openings", [])[:3]:
                        db.add(LeadSignal(
                            lead_id=lead.id,
                            signal_type="new_hire",
                            title=f"Hiring: {job['title']}",
                            detail="Job opening detected on company website",
                            source_url=enrichment_data.get("jobs", {}).get("url", lead.website),
                            detected_at=datetime.utcnow()
                        ))
                        signals_created += 1

                if signals.get("has_engineering"):
                    db.add(LeadSignal(
                        lead_id=lead.id,
                        signal_type="engineering_detected",
                        title="Engineering/CAD activity detected",
                        detail="Company website mentions engineering, CAD, or simulation",
                        source_url=lead.website,
                        detected_at=datetime.utcnow()
                    ))
                    signals_created += 1

                if signals.get("has_iso_certification"):
                    db.add(LeadSignal(
                        lead_id=lead.id,
                        signal_type="audit_signal",
                        title="ISO certification detected",
                        detail="Company has ISO or quality certification",
                        source_url=lead.website,
                        detected_at=datetime.utcnow()
                    ))
                    signals_created += 1

                await db.commit()

                enriched += 1

                # Show what we found
                found = []
                if signals.get("has_engineering"):
                    found.append("🔧 Engineering")
                if signals.get("has_cad_software"):
                    found.append("💻 CAD")
                if signals.get("is_hiring_engineers"):
                    found.append("👔 Hiring")
                if signals.get("has_iso_certification"):
                    found.append("✅ ISO")
                if signals.get("is_multinational"):
                    found.append("🌍 Multinational")
                if signals.get("employee_count"):
                    found.append(f"👥 {signals['employee_count']} employees")

                print(f"  ✅ {' | '.join(found) if found else 'No signals'}")

                # Rate limiting
                await asyncio.sleep(3)

            except Exception as e:
                print(f"  ❌ Error: {e}")
                errors += 1

        await enricher.close()

        print(f"\n✅ Enrichment complete!")
        print(f"   Total: {total}")
        print(f"   Enriched: {enriched}")
        print(f"   Errors: {errors}")

        return enriched


async def step4_recalculate_scores():
    """Step 4: Recalculate ALL scores with real enriched data."""

    print("\n" + "=" * 60)
    print("STEP 4: RECALCULATE SCORES")
    print("=" * 60)

    async with AsyncSessionLocal() as db:
        # Get all leads
        result = await db.execute(select(Lead))
        leads = result.scalars().all()

        # Delete old scores
        await db.execute(delete(LeadScore))
        await db.commit()

        print(f"🔄 Recalculating scores for {len(leads)} companies...\n")

        stats = await score_all_leads(db)

        print(f"\n✅ Scores recalculated!")
        print(f"   Total scores: {stats.get('total_scores', 0)}")
        print(f"   Leads scored: {stats.get('leads_scored', 0)}")

        return total_scores


async def step5_show_statistics():
    """Step 5: Show final statistics and top leads."""

    print("\n" + "=" * 60)
    print("STEP 5: FINAL STATISTICS")
    print("=" * 60)

    async with AsyncSessionLocal() as db:
        # Total companies
        result = await db.execute(select(Lead))
        total = len(result.scalars().all())

        # Verified vs unverified
        result = await db.execute(
            select(Lead).where(Lead.status == "unverified")
        )
        unverified = len(result.scalars().all())
        verified = total - unverified

        # With enrichment
        result = await db.execute(select(Lead))
        leads = result.scalars().all()

        enriched = sum(1 for lead in leads if lead.scraped_data and "deep_enrichment" in lead.scraped_data)

        # Signals
        result = await db.execute(select(LeadSignal))
        signals = len(result.scalars().all())

        # Scores
        result = await db.execute(select(LeadScore))
        scores = len(result.scalars().all())

        print(f"\n📊 DATABASE STATISTICS:")
        print(f"   Total companies: {total}")
        print(f"   ✅ Verified (have websites): {verified}")
        print(f"   ❓ Unverified (no websites): {unverified}")
        print(f"   🔍 Deep enriched: {enriched}")
        print(f"   🎯 Total signals: {signals}")
        print(f"   📈 Total scores: {scores}")

        # Top 10 leads
        print(f"\n🏆 TOP 10 LEADS (by best score):\n")

        result = await db.execute(
            select(Lead, LeadScore)
            .join(LeadScore, Lead.id == LeadScore.lead_id)
            .order_by(LeadScore.score.desc())
            .limit(10)
        )

        for i, row in enumerate(result, 1):
            lead = row[0]
            score = row[1]

            signals_found = []
            if lead.is_multinational:
                signals_found.append("🌍 Multinational")
            if lead.under_audit:
                signals_found.append("✅ ISO")
            if lead.is_exporter:
                signals_found.append("📦 Export")

            enrichment = lead.scraped_data.get("deep_enrichment", {}) if lead.scraped_data else {}
            enrichment_signals = enrichment.get("signals", {})

            if enrichment_signals.get("has_engineering"):
                signals_found.append("🔧 Engineering")
            if enrichment_signals.get("is_hiring_engineers"):
                signals_found.append("👔 Hiring")

            signals_str = " | ".join(signals_found) if signals_found else "No signals"

            print(f"{i:2}. {lead.company_name[:40]:40} | {score.score:5.1f}/100 | {score.service_name[:20]:20}")
            print(f"    {signals_str}")

        print("\n" + "=" * 60)
        print("✅ ENRICHMENT PIPELINE COMPLETE!")
        print("=" * 60)
        print("\n🎯 Platform now has REAL company intelligence.")
        print("   Manager can see exactly what each company does,")
        print("   why they need SOLIDWORKS, and when to call them.\n")


async def main():
    """Run complete enrichment pipeline."""

    print("\n" + "=" * 60)
    print("🚀 ABBK LEADENGINE — DEEP ENRICHMENT PIPELINE")
    print("=" * 60)
    print("\nThis will:")
    print("  1. Clean junk companies")
    print("  2. Mark unverified leads (no website)")
    print("  3. Deep enrich all companies with websites")
    print("  4. Recalculate all scores")
    print("  5. Show statistics and top leads")
    print("\nThis creates the CORE VALUE of the platform.\n")

    try:
        total_after_clean = await step1_clean_junk()
        unverified_count = await step2_mark_unverified()
        enriched_count = await step3_deep_enrichment()
        scores_count = await step4_recalculate_scores()
        await step5_show_statistics()

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

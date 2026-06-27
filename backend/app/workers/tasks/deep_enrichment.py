#!/usr/bin/env python3
"""
Deep Company Enrichment Tasks

Runs deep enrichment spider on all companies with websites.
Stores rich company intelligence in lead.scraped_data.
"""

import asyncio
from datetime import datetime
from typing import List, Dict, Any

from celery import shared_task
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.models.models import Lead, LeadSignal
from app.scrapers.utils.deep_enricher import DeepCompanyEnricher


@shared_task(name="deep_enrichment.enrich_single_company")
def enrich_single_company_task(lead_id: int) -> Dict[str, Any]:
    """
    Deep enrichment for a single company.

    Args:
        lead_id: Lead ID to enrich

    Returns:
        Dict with enrichment results
    """
    return asyncio.run(_enrich_single_company(lead_id))


async def _enrich_single_company(lead_id: int) -> Dict[str, Any]:
    """Async implementation of single company enrichment."""

    async with AsyncSessionLocal() as db:
        # Get lead
        result = await db.execute(
            select(Lead).where(Lead.id == lead_id)
        )
        lead = result.scalar_one_or_none()

        if not lead:
            return {"error": f"Lead {lead_id} not found"}

        if not lead.website:
            return {"error": f"Lead {lead.company_name} has no website"}

        # Run enrichment
        enricher = DeepCompanyEnricher()
        enrichment_data = await enricher.enrich_company(
            company_id=lead.id,
            company_name=lead.company_name,
            website=lead.website
        )

        # Store in database
        if not lead.scraped_data:
            lead.scraped_data = {}

        lead.scraped_data["deep_enrichment"] = enrichment_data
        lead.scraped_data["deep_enrichment"]["enriched_at"] = datetime.utcnow().isoformat()

        # Update lead flags from enrichment signals
        signals = enrichment_data.get("signals", {})

        if signals.get("is_multinational"):
            lead.is_multinational = True

        if signals.get("is_exporter"):
            lead.is_exporter = True

        if signals.get("has_iso_certification"):
            lead.under_audit = True

        if signals.get("employee_count"):
            lead.employee_count = signals["employee_count"]

        # Create signals for detected events
        signals_to_create = []

        if signals.get("is_hiring_engineers"):
            for job in signals.get("job_openings", [])[:5]:  # Max 5
                signals_to_create.append(
                    LeadSignal(
                        lead_id=lead.id,
                        signal_type="new_hire",
                        title=f"Hiring: {job['title']}",
                        detail=f"Job opening detected on company website",
                        source_url=enrichment_data.get("jobs", {}).get("url", lead.website),
                        detected_at=datetime.utcnow()
                    )
                )

        if signals.get("has_engineering"):
            signals_to_create.append(
                LeadSignal(
                    lead_id=lead.id,
                    signal_type="engineering_detected",
                    title="Engineering/CAD activity detected",
                    detail="Company website mentions engineering, CAD, or simulation",
                    source_url=lead.website,
                    detected_at=datetime.utcnow()
                )
            )

        if signals.get("has_iso_certification"):
            signals_to_create.append(
                LeadSignal(
                    lead_id=lead.id,
                    signal_type="audit_signal",
                    title="ISO certification detected",
                    detail="Company has ISO certification or mentions quality audit",
                    source_url=enrichment_data.get("about", {}).get("url", lead.website),
                    detected_at=datetime.utcnow()
                )
            )

        # Bulk insert signals
        if signals_to_create:
            db.add_all(signals_to_create)

        await db.commit()

        return {
            "lead_id": lead.id,
            "company_name": lead.company_name,
            "website": lead.website,
            "signals_detected": len(signals_to_create),
            "has_engineering": signals.get("has_engineering", False),
            "has_cad_software": signals.get("has_cad_software", False),
            "is_hiring": signals.get("is_hiring_engineers", False),
            "employee_count": signals.get("employee_count"),
            "enriched": True
        }


@shared_task(name="deep_enrichment.enrich_all_companies")
def enrich_all_companies_task() -> Dict[str, Any]:
    """
    Deep enrichment for ALL companies with websites.

    This is the main task that should run to build real company intelligence.
    """
    return asyncio.run(_enrich_all_companies())


async def _enrich_all_companies() -> Dict[str, Any]:
    """Async implementation of all companies enrichment."""

    async with AsyncSessionLocal() as db:
        # Get all companies WITH websites
        result = await db.execute(
            select(Lead).where(Lead.website.isnot(None))
        )
        leads = result.scalars().all()

        total = len(leads)
        enriched = 0
        errors = 0

        print(f"\n🔍 Starting deep enrichment for {total} companies with websites\n")

        enricher = DeepCompanyEnricher()

        for i, lead in enumerate(leads, 1):
            try:
                print(f"[{i}/{total}] Enriching {lead.company_name}...")

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
                lead.scraped_data["deep_enrichment"]["enriched_at"] = datetime.utcnow().isoformat()

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
                    for job in signals.get("job_openings", [])[:5]:
                        db.add(
                            LeadSignal(
                                lead_id=lead.id,
                                signal_type="new_hire",
                                title=f"Hiring: {job['title']}",
                                detail=f"Job opening detected on website",
                                source_url=enrichment_data.get("jobs", {}).get("url", lead.website),
                                detected_at=datetime.utcnow()
                            )
                        )
                        signals_created += 1

                if signals.get("has_engineering"):
                    db.add(
                        LeadSignal(
                            lead_id=lead.id,
                            signal_type="engineering_detected",
                            title="Engineering/CAD activity detected",
                            detail="Company mentions engineering, CAD, or simulation",
                            source_url=lead.website,
                            detected_at=datetime.utcnow()
                        )
                    )
                    signals_created += 1

                if signals.get("has_iso_certification"):
                    db.add(
                        LeadSignal(
                            lead_id=lead.id,
                            signal_type="audit_signal",
                            title="ISO certification detected",
                            detail="Company has ISO or quality certification",
                            source_url=lead.website,
                            detected_at=datetime.utcnow()
                        )
                    )
                    signals_created += 1

                await db.commit()

                enriched += 1

                print(f"  ✅ Enriched! Signals: {signals_created}")

                # Rate limiting
                await asyncio.sleep(3)  # 3 seconds between companies

            except Exception as e:
                print(f"  ❌ Error: {e}")
                errors += 1
                continue

        print(f"\n✅ Deep enrichment complete!")
        print(f"   Total: {total}")
        print(f"   Enriched: {enriched}")
        print(f"   Errors: {errors}")

        return {
            "total": total,
            "enriched": enriched,
            "errors": errors,
            "success_rate": f"{enriched / total * 100:.1f}%" if total > 0 else "0%"
        }


@shared_task(name="deep_enrichment.mark_unverified_leads")
def mark_unverified_leads_task() -> Dict[str, Any]:
    """
    Mark companies WITHOUT websites as 'unverified' status.
    These are low-priority leads that need manual verification.
    """
    return asyncio.run(_mark_unverified_leads())


async def _mark_unverified_leads() -> Dict[str, Any]:
    """Async implementation of marking unverified leads."""

    async with AsyncSessionLocal() as db:
        # Update all leads without websites to 'unverified' status
        result = await db.execute(
            update(Lead)
            .where(Lead.website.is_(None))
            .values(status="unverified")
        )

        count = result.rowcount
        await db.commit()

        print(f"✅ Marked {count} companies without websites as 'unverified'")

        return {
            "marked_unverified": count
        }

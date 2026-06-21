#!/usr/bin/env python3
"""
Test script for company enrichment.

Tests enrichment on existing leads.
"""
import sys
import os
import asyncio

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from app.db.session import AsyncSessionLocal
from app.models.models import Lead
from app.workers.tasks.company_enrichment import enrich_single_lead
from sqlalchemy import select


async def main():
    print("=" * 80)
    print("  ABBK LeadEngine — Company Enrichment Test")
    print("=" * 80)
    print()
    print("Enrichment data added:")
    print("  - Employee count (from LinkedIn)")
    print("  - Recent hires (last 90 days)")
    print("  - Recent news (last 6 months)")
    print("  - Fiscal sector classification")
    print("  - Registre de commerce (if available)")
    print("  - Company age/maturity")
    print("  - Growth indicators")
    print("  - Compliance flags")
    print()
    print("Starting enrichment test...")
    print("-" * 80)
    print()

    async with AsyncSessionLocal() as db:
        # Get first 5 leads
        result = await db.execute(select(Lead).limit(5))
        leads = result.scalars().all()

        print(f"Testing enrichment on {len(leads)} leads:")
        print()

        for lead in leads:
            print(f"Enriching: {lead.company_name}")
            result = await enrich_single_lead(db, lead)

            if result['success']:
                print(f"  ✅ Success: {result['fields_added']} fields added")
                if result['changes_made']:
                    print(f"  📝 Changes saved to database")
                else:
                    print(f"  ℹ️  No new data to add")
            else:
                print(f"  ❌ Error: {result.get('error')}")
            print()

    print("=" * 80)
    print("  Enrichment test completed!")
    print("=" * 80)
    print()
    print("Check enriched data:")
    print("  SELECT scraped_data->'enrichment' FROM leads WHERE scraped_data ? 'enrichment';")
    print()


if __name__ == '__main__':
    asyncio.run(main())

"""
Standalone script to find and merge duplicate leads.
"""
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.config import settings
from app.models.models import Lead
from app.scrapers.utils.deduplication import DeduplicationEngine, deduplicate_companies


async def find_duplicates():
    """Find all duplicate leads in database."""
    print("=" * 70)
    print("ABBK LeadEngine — Duplicate Detection")
    print("=" * 70)

    engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        try:
            # Get all leads
            result = await session.execute(select(Lead))
            leads = result.scalars().all()

            print(f"\n📊 Analyzing {len(leads)} companies for duplicates...")
            print(f"Using similarity threshold: 0.85")
            print("-" * 70)

            # Convert to dict format
            leads_data = []
            for lead in leads:
                leads_data.append({
                    'id': lead.id,
                    'company_name': lead.company_name,
                    'website': lead.website,
                    'city': lead.city,
                    'sector': lead.sector,
                })

            # Find duplicates (without auto-merge)
            _, duplicates = deduplicate_companies(leads_data, threshold=0.85, auto_merge=False)

            if not duplicates:
                print("\n✅ No duplicates found!")
                print("All companies are unique.")
            else:
                print(f"\n⚠️  Found {len(duplicates)} duplicate pairs:")
                print()

                for i, dup in enumerate(duplicates, 1):
                    print(f"{i}. {dup['primary_name']}")
                    print(f"   ↔️  {dup['duplicate_name']}")
                    print(f"   Confidence: {dup['confidence']:.2%}")
                    print(f"   Reason: {dup['reason']}")
                    print()

                print("-" * 70)
                print(f"\n💡 To merge duplicates, update the script with auto_merge=True")
                print(f"   Or manually merge via database SQL")

            print("\n" + "=" * 70)

        finally:
            await engine.dispose()


if __name__ == '__main__':
    asyncio.run(find_duplicates())

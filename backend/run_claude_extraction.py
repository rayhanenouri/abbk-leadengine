#!/usr/bin/env python3
"""
Standalone script to run Claude API signal extraction on all leads.
Usage: python run_claude_extraction.py [--force] [--limit N]
"""

import asyncio
import sys
import argparse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.models.models import Lead
from app.services.claude_extractor import ClaudeSignalExtractor
from app.core.config import settings


async def main(force: bool = False, limit: int = None):
    """Run Claude extraction on all leads with scraped_data."""

    print("=" * 60)
    print("ABBK LeadEngine - Claude API Signal Extraction")
    print("=" * 60)
    print()

    # Check API key
    if not settings.ANTHROPIC_API_KEY:
        print("❌ ERROR: ANTHROPIC_API_KEY not set in .env file")
        print()
        print("Please add your Anthropic API key to .env:")
        print("ANTHROPIC_API_KEY=sk-ant-...")
        print()
        return

    print(f"✅ Anthropic API key configured")
    print(f"📍 Model: claude-sonnet-4-5")
    print(f"🔄 Force re-extraction: {force}")
    if limit:
        print(f"📊 Limit: {limit} leads")
    print()

    async with AsyncSessionLocal() as db:
        # Get leads with scraped_data
        query = select(Lead).where(Lead.scraped_data.isnot(None))
        if limit:
            query = query.limit(limit)

        result = await db.execute(query)
        leads = result.scalars().all()

        if not leads:
            print("⚠️  No leads with scraped_data found")
            return

        print(f"📦 Found {len(leads)} leads with scraped_data")
        print()

        extractor = ClaudeSignalExtractor()

        stats = {
            "total": len(leads),
            "processed": 0,
            "cached": 0,
            "extracted": 0,
            "failed": 0,
            "signals_found": {}
        }

        for i, lead in enumerate(leads, 1):
            print(f"[{i}/{len(leads)}] Processing: {lead.company_name}")

            # Check cache
            if not force and isinstance(lead.scraped_data, dict):
                if "claude_signals" in lead.scraped_data:
                    print(f"  ✓ Cached (skipping)")
                    stats["cached"] += 1
                    stats["processed"] += 1
                    print()
                    continue

            try:
                signals, was_cached = await extractor.extract_signals(db, lead)

                if signals:
                    if was_cached:
                        print(f"  ✓ Retrieved from cache")
                        stats["cached"] += 1
                    else:
                        print(f"  ✓ Extracted new signals")
                        stats["extracted"] += 1

                    # Count true signals
                    true_signals = [k for k, v in signals.items() if isinstance(v, bool) and v is True]
                    if true_signals:
                        print(f"  📊 Found {len(true_signals)} signals: {', '.join(true_signals[:3])}")
                        for sig in true_signals:
                            stats["signals_found"][sig] = stats["signals_found"].get(sig, 0) + 1
                    else:
                        print(f"  📊 No buying signals detected")

                    if "reasoning" in signals:
                        print(f"  💡 {signals['reasoning'][:80]}...")

                else:
                    print(f"  ❌ Extraction failed")
                    stats["failed"] += 1

            except Exception as e:
                print(f"  ❌ Error: {e}")
                stats["failed"] += 1

            stats["processed"] += 1
            print()

        # Print summary
        print()
        print("=" * 60)
        print("EXTRACTION SUMMARY")
        print("=" * 60)
        print(f"Total leads:        {stats['total']}")
        print(f"Processed:          {stats['processed']}")
        print(f"Cached (skipped):   {stats['cached']}")
        print(f"Newly extracted:    {stats['extracted']}")
        print(f"Failed:             {stats['failed']}")
        print()

        if stats["signals_found"]:
            print("SIGNAL BREAKDOWN:")
            sorted_signals = sorted(stats["signals_found"].items(), key=lambda x: x[1], reverse=True)
            for signal, count in sorted_signals:
                print(f"  {signal:30s} {count:3d} companies")
            print()

        print("✅ Extraction complete!")
        print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Claude API signal extraction")
    parser.add_argument("--force", action="store_true", help="Force re-extraction even if cached")
    parser.add_argument("--limit", type=int, help="Limit number of leads to process")

    args = parser.parse_args()

    asyncio.run(main(force=args.force, limit=args.limit))

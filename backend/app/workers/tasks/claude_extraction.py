"""
Celery tasks for Claude API signal extraction.
Runs extraction on leads with scraped_data.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.workers.celery_app import celery_app
from app.db.session import AsyncSessionLocal
from app.models.models import Lead
from app.services.claude_extractor import ClaudeSignalExtractor


@celery_app.task(name="extract_claude_signals_single")
def extract_claude_signals_single(lead_id: int) -> dict:
    """
    Extract Claude signals for a single lead.

    Args:
        lead_id: Lead ID to process

    Returns:
        Dict with extraction results
    """
    import asyncio

    async def _extract():
        async with AsyncSessionLocal() as db:
            try:
                # Get lead
                query = select(Lead).where(Lead.id == lead_id)
                result = await db.execute(query)
                lead = result.scalar_one_or_none()

                if not lead:
                    return {"success": False, "error": "Lead not found"}

                if not lead.scraped_data:
                    return {"success": False, "error": "No scraped_data"}

                # Extract signals
                extractor = ClaudeSignalExtractor()
                signals, was_cached = await extractor.extract_signals(db, lead)

                if signals:
                    return {
                        "success": True,
                        "lead_id": lead_id,
                        "company_name": lead.company_name,
                        "signals": signals,
                        "was_cached": was_cached
                    }
                else:
                    return {"success": False, "error": "Extraction failed"}

            except Exception as e:
                return {"success": False, "error": str(e)}

    return asyncio.run(_extract())


@celery_app.task(name="extract_claude_signals_batch")
def extract_claude_signals_batch(limit: int = 50, skip_cached: bool = True) -> dict:
    """
    Extract Claude signals for multiple leads in batch.

    Args:
        limit: Maximum number of leads to process
        skip_cached: Skip leads that already have cached signals

    Returns:
        Dict with batch extraction statistics
    """
    import asyncio

    async def _extract_batch():
        async with AsyncSessionLocal() as db:
            try:
                # Get leads with scraped_data
                query = select(Lead).where(Lead.scraped_data.isnot(None)).limit(limit)
                result = await db.execute(query)
                leads = result.scalars().all()

                extractor = ClaudeSignalExtractor()

                stats = {
                    "total_leads": len(leads),
                    "processed": 0,
                    "cached": 0,
                    "extracted": 0,
                    "failed": 0,
                    "results": []
                }

                for lead in leads:
                    # Skip cached if requested
                    if skip_cached and isinstance(lead.scraped_data, dict):
                        if "claude_signals" in lead.scraped_data:
                            stats["cached"] += 1
                            continue

                    signals, was_cached = await extractor.extract_signals(db, lead)

                    if signals:
                        if was_cached:
                            stats["cached"] += 1
                        else:
                            stats["extracted"] += 1

                        stats["results"].append({
                            "lead_id": lead.id,
                            "company_name": lead.company_name,
                            "signals_count": sum(1 for v in signals.values() if v is True),
                            "was_cached": was_cached
                        })
                    else:
                        stats["failed"] += 1

                    stats["processed"] += 1

                return stats

            except Exception as e:
                return {"success": False, "error": str(e)}

    return asyncio.run(_extract_batch())


@celery_app.task(name="extract_claude_signals_all")
def extract_claude_signals_all(force: bool = False) -> dict:
    """
    Extract Claude signals for ALL leads with scraped_data.
    Use with caution - can make many API calls.

    Args:
        force: If True, re-extract even if cached

    Returns:
        Dict with full extraction statistics
    """
    import asyncio

    async def _extract_all():
        async with AsyncSessionLocal() as db:
            try:
                extractor = ClaudeSignalExtractor()
                stats = await extractor.reextract_all(db, force=force)
                return stats
            except Exception as e:
                return {"success": False, "error": str(e)}

    return asyncio.run(_extract_all())

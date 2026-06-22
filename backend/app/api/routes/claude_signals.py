"""
API routes for Claude signal extraction.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Optional

from app.db.session import get_db
from app.models.models import Lead
from app.api.routes.auth import get_current_user
from app.services.claude_extractor import ClaudeSignalExtractor, get_claude_signals
from app.workers.tasks.claude_extraction import (
    extract_claude_signals_single,
    extract_claude_signals_batch,
    extract_claude_signals_all
)

router = APIRouter()


@router.post("/claude/extract/{lead_id}")
async def extract_signals_for_lead(
    lead_id: int,
    force: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
) -> Dict:
    """
    Extract Claude signals for a single lead.

    Args:
        lead_id: Lead ID to process
        force: If True, re-extract even if cached
        db: Database session
        current_user: Authenticated user

    Returns:
        Dict with extraction results and signals
    """
    # Get lead
    query = select(Lead).where(Lead.id == lead_id)
    result = await db.execute(query)
    lead = result.scalar_one_or_none()

    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    if not lead.scraped_data:
        raise HTTPException(status_code=400, detail="Lead has no scraped_data to extract from")

    # Check cache
    if not force and isinstance(lead.scraped_data, dict):
        if "claude_signals" in lead.scraped_data:
            return {
                "lead_id": lead_id,
                "company_name": lead.company_name,
                "signals": lead.scraped_data["claude_signals"],
                "was_cached": True,
                "extracted_at": lead.scraped_data.get("claude_extracted_at")
            }

    # Extract signals
    try:
        extractor = ClaudeSignalExtractor()
        signals, was_cached = await extractor.extract_signals(db, lead)

        if not signals:
            raise HTTPException(status_code=500, detail="Signal extraction failed")

        return {
            "lead_id": lead_id,
            "company_name": lead.company_name,
            "signals": signals,
            "was_cached": was_cached,
            "extracted_at": lead.scraped_data.get("claude_extracted_at")
        }

    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/claude/signals/{lead_id}")
async def get_lead_claude_signals(
    lead_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
) -> Dict:
    """
    Get cached Claude signals for a lead (no extraction).

    Args:
        lead_id: Lead ID
        db: Database session
        current_user: Authenticated user

    Returns:
        Dict with cached signals or None
    """
    signals = await get_claude_signals(db, lead_id)

    if signals is None:
        raise HTTPException(status_code=404, detail="No Claude signals found for this lead")

    return {
        "lead_id": lead_id,
        "signals": signals
    }


@router.post("/claude/extract-batch")
async def extract_signals_batch(
    limit: int = 50,
    skip_cached: bool = True,
    current_user = Depends(get_current_user)
) -> Dict:
    """
    Trigger batch extraction for multiple leads (async task).

    Args:
        limit: Maximum number of leads to process
        skip_cached: Skip leads with cached signals
        current_user: Authenticated user

    Returns:
        Task ID for tracking
    """
    task = extract_claude_signals_batch.delay(limit=limit, skip_cached=skip_cached)

    return {
        "task_id": task.id,
        "status": "processing",
        "message": f"Extracting signals for up to {limit} leads"
    }


@router.post("/claude/extract-all")
async def extract_signals_all(
    force: bool = False,
    current_user = Depends(get_current_user)
) -> Dict:
    """
    Trigger extraction for ALL leads with scraped_data (async task).
    WARNING: Can make many API calls and incur costs.

    Args:
        force: If True, re-extract even if cached
        current_user: Authenticated user

    Returns:
        Task ID for tracking
    """
    task = extract_claude_signals_all.delay(force=force)

    return {
        "task_id": task.id,
        "status": "processing",
        "message": "Extracting signals for all leads with scraped_data",
        "warning": "This may make many API calls"
    }


@router.get("/claude/stats")
async def get_claude_extraction_stats(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
) -> Dict:
    """
    Get statistics about Claude signal extraction coverage.

    Args:
        db: Database session
        current_user: Authenticated user

    Returns:
        Dict with extraction statistics
    """
    # Total leads
    total_query = select(Lead.id)
    total_result = await db.execute(total_query)
    total_leads = len(total_result.all())

    # Leads with scraped_data
    scraped_query = select(Lead).where(Lead.scraped_data.isnot(None))
    scraped_result = await db.execute(scraped_query)
    leads_with_scraped = scraped_result.scalars().all()

    # Leads with Claude signals
    extracted_count = 0
    signal_summary = {}

    for lead in leads_with_scraped:
        if isinstance(lead.scraped_data, dict) and "claude_signals" in lead.scraped_data:
            extracted_count += 1

            # Count true signals
            signals = lead.scraped_data["claude_signals"]
            for key, value in signals.items():
                if isinstance(value, bool) and value is True:
                    signal_summary[key] = signal_summary.get(key, 0) + 1

    return {
        "total_leads": total_leads,
        "leads_with_scraped_data": len(leads_with_scraped),
        "leads_with_claude_signals": extracted_count,
        "extraction_coverage": round((extracted_count / len(leads_with_scraped) * 100), 1) if leads_with_scraped else 0,
        "signal_summary": signal_summary,
        "pending_extraction": len(leads_with_scraped) - extracted_count
    }

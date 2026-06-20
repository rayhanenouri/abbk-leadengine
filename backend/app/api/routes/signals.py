"""
Signals routes: get signals for a lead.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.schemas.signals import SignalResponse
from app.models.models import LeadSignal
from app.core.deps import get_db, get_current_user
from app.models.models import User


router = APIRouter()


@router.get("/{lead_id}", response_model=List[SignalResponse])
async def get_lead_signals(
    lead_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get all signals for a specific lead.

    Returns signals sorted by detected_at descending (newest first).
    """
    result = await db.execute(
        select(LeadSignal)
        .where(LeadSignal.lead_id == lead_id)
        .order_by(LeadSignal.detected_at.desc())
    )
    signals = result.scalars().all()

    return signals

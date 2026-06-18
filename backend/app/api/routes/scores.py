"""
Scores management routes: get scores, ranked leads, recalculate.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.schemas.scores import ScoreResponse, LeadWithScoresResponse, RankedLeadResponse
from app.models.models import Lead, LeadScore, Service
from app.core.deps import get_db, get_current_user
from app.models.models import User
from app.services.scoring_engine import score_lead


router = APIRouter()


@router.get("/ranked", response_model=List[RankedLeadResponse])
async def get_ranked_leads(
    limit: int = Query(default=20, le=100),
    min_score: float = Query(default=0, ge=0, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get ranked list of leads by their best score.

    Returns leads sorted by highest score descending.
    Each lead shows its best-scoring service.

    Query params:
    - limit: Max number of leads to return (default 20, max 100)
    - min_score: Only show leads with score >= this (default 0)
    """
    # Subquery to get best score per lead
    best_scores_subq = (
        select(
            LeadScore.lead_id,
            func.max(LeadScore.score).label('best_score')
        )
        .group_by(LeadScore.lead_id)
        .subquery()
    )

    # Get lead scores that match the best score for each lead
    query = (
        select(Lead, LeadScore)
        .join(LeadScore, Lead.id == LeadScore.lead_id)
        .join(
            best_scores_subq,
            and_(
                LeadScore.lead_id == best_scores_subq.c.lead_id,
                LeadScore.score == best_scores_subq.c.best_score
            )
        )
        .where(LeadScore.score >= min_score)
        .order_by(LeadScore.score.desc())
        .limit(limit)
    )

    result = await db.execute(query)
    rows = result.all()

    ranked_leads = []
    for lead, score in rows:
        ranked_leads.append(RankedLeadResponse(
            lead_id=lead.id,
            company_name=lead.company_name,
            sector=lead.sector,
            city=lead.city,
            best_score=score.score,
            best_service=score.service_name,
            best_reasoning=score.reasoning
        ))

    return ranked_leads


@router.get("/{lead_id}", response_model=LeadWithScoresResponse)
async def get_lead_scores(
    lead_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get all scores for a specific lead.

    Returns the lead with all its service scores,
    plus the best score and best service recommendation.
    """
    # Get lead
    lead_result = await db.execute(
        select(Lead).where(Lead.id == lead_id)
    )
    lead = lead_result.scalar_one_or_none()

    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )

    # Get all scores for this lead
    scores_result = await db.execute(
        select(LeadScore)
        .where(LeadScore.lead_id == lead_id)
        .order_by(LeadScore.score.desc())
    )
    scores = scores_result.scalars().all()

    if not scores:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No scores found for this lead. Run scoring first."
        )

    # Convert to response models
    score_responses = [ScoreResponse.model_validate(score) for score in scores]

    # Best score is first (already sorted DESC)
    best = scores[0]

    return LeadWithScoresResponse(
        lead_id=lead.id,
        company_name=lead.company_name,
        sector=lead.sector,
        city=lead.city,
        website=lead.website,
        scores=score_responses,
        best_score=best.score,
        best_service=best.service_name
    )


@router.post("/{lead_id}/recalculate")
async def recalculate_score(
    lead_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Recalculate scores for a specific lead.

    Deletes old scores and creates new ones with current scoring rules.
    """
    # Get lead
    lead_result = await db.execute(
        select(Lead).where(Lead.id == lead_id)
    )
    lead = lead_result.scalar_one_or_none()

    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )

    # Delete old scores
    await db.execute(
        select(LeadScore).where(LeadScore.lead_id == lead_id)
    )
    await db.commit()

    # Get active services
    services_result = await db.execute(
        select(Service).where(Service.is_active == True)
    )
    services = services_result.scalars().all()

    # Calculate new scores
    new_scores = await score_lead(lead, services, db)
    await db.commit()

    return {
        "message": f"Recalculated {len(new_scores)} scores for {lead.company_name}",
        "scores_created": len(new_scores)
    }

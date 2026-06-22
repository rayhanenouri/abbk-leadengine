"""
Leads management routes: import, list, get, update.
"""
import csv
import io
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func, and_
from sqlalchemy.orm import selectinload

from app.schemas.leads import (
    LeadResponse, CSVImportResponse, LeadWithSignalsResponse,
    PaginatedLeadsResponse, LeadStatusUpdate, LeadStatusHistoryResponse,
    LeadDetailResponse
)
from app.models.models import Lead, LeadStatus, LeadSignal, LeadScore, LeadStatusHistory
from app.core.deps import get_db, get_current_user
from app.models.models import User


router = APIRouter()


@router.post("/import", response_model=CSVImportResponse)
async def import_csv(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Import leads from CSV file.

    Expected CSV columns: company_name, website, phone, sector, city, country

    Checks for duplicates by website and company_name before inserting.
    Returns count of imported and skipped companies.

    Example CSV:
    ```
    company_name,website,phone,sector,city,country
    Poulina Group,https://www.poulina.com.tn,+216 71 862 000,Diversified,Tunis,Tunisia
    ```
    """
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a CSV"
        )

    # Read CSV content
    content = await file.read()
    csv_text = content.decode('utf-8')
    csv_reader = csv.DictReader(io.StringIO(csv_text))

    imported = 0
    skipped = 0
    total = 0

    for row in csv_reader:
        total += 1

        # Extract data from CSV row
        company_name = row.get('company_name', '').strip()
        website = row.get('website', '').strip() or None
        sector = row.get('sector', '').strip() or None
        city = row.get('city', '').strip() or None
        country = row.get('country', '').strip() or None
        phone = row.get('phone', '').strip() or None

        # Skip if company_name is empty
        if not company_name:
            skipped += 1
            continue

        # Check for duplicates by website OR company_name
        duplicate_query = select(Lead).where(
            or_(
                Lead.website == website if website else False,
                Lead.company_name == company_name
            )
        )
        result = await db.execute(duplicate_query)
        existing_lead = result.scalar_one_or_none()

        if existing_lead:
            skipped += 1
            continue

        # Create new lead
        new_lead = Lead(
            company_name=company_name,
            website=website,
            country=country,
            city=city,
            sector=sector,
            status=LeadStatus.new,
            scraped_data={
                "csv_import": {
                    "phone": phone,
                    "imported_at": str(datetime.utcnow()),
                    "imported_by": current_user.email
                }
            }
        )

        db.add(new_lead)
        imported += 1

    # Commit all new leads
    await db.commit()

    return CSVImportResponse(
        imported=imported,
        skipped=skipped,
        total=total,
        message=f"Successfully imported {imported} companies, skipped {skipped} duplicates"
    )


@router.get("/", response_model=PaginatedLeadsResponse)
async def get_leads(
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=50, ge=1, le=1000, description="Max records to return"),
    sector: Optional[str] = Query(default=None, description="Filter by sector"),
    city: Optional[str] = Query(default=None, description="Filter by city"),
    country: Optional[str] = Query(default=None, description="Filter by country"),
    is_multinational: Optional[bool] = Query(default=None, description="Filter multinational companies"),
    is_exporter: Optional[bool] = Query(default=None, description="Filter exporters"),
    under_audit: Optional[bool] = Query(default=None, description="Filter companies under audit"),
    has_signals: Optional[bool] = Query(default=None, description="Filter leads with signals"),
    min_score: Optional[float] = Query(default=None, ge=0, le=100, description="Minimum score filter"),
    search: Optional[str] = Query(default=None, description="Search by company name"),
    sort_by: str = Query(default="created_at", description="Sort field: created_at, company_name, score"),
    sort_order: str = Query(default="desc", description="Sort order: asc or desc"),
    include_signals: bool = Query(default=False, description="Include signals in response"),
    include_scores: bool = Query(default=False, description="Include scores in response"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get leads with advanced filtering, pagination, sorting, and optional signals/scores.

    Query parameters:
    - skip, limit: Pagination
    - sector, city, country: Basic filters
    - is_multinational, is_exporter, under_audit: Boolean flags
    - has_signals: Only leads with detected signals
    - min_score: Filter by minimum score
    - search: Search company name (case-insensitive)
    - sort_by: created_at, company_name, or score
    - sort_order: asc or desc
    - include_signals: Add signals array to each lead
    - include_scores: Add scores array to each lead

    Returns:
    - leads: Array of lead objects
    - total: Total count (before pagination)
    - skip, limit: Pagination params
    - has_more: Whether more results exist
    """
    # Build base query
    query = select(Lead)

    # Apply filters
    filters = []

    if sector:
        filters.append(Lead.sector.ilike(f"%{sector}%"))

    if city:
        filters.append(Lead.city.ilike(f"%{city}%"))

    if country:
        filters.append(Lead.country.ilike(f"%{country}%"))

    if is_multinational is not None:
        filters.append(Lead.is_multinational == is_multinational)

    if is_exporter is not None:
        filters.append(Lead.is_exporter == is_exporter)

    if under_audit is not None:
        filters.append(Lead.under_audit == under_audit)

    if search:
        filters.append(Lead.company_name.ilike(f"%{search}%"))

    if filters:
        query = query.where(and_(*filters))

    # Filter by signals
    if has_signals is not None:
        if has_signals:
            # Only leads with at least one signal
            query = query.join(LeadSignal).group_by(Lead.id)
        else:
            # Only leads without signals
            subq = select(LeadSignal.lead_id).distinct()
            query = query.where(Lead.id.notin_(subq))

    # Filter by minimum score
    if min_score is not None:
        # Join with scores and filter by max score
        score_subq = (
            select(LeadScore.lead_id)
            .where(LeadScore.score >= min_score)
            .group_by(LeadScore.lead_id)
            .subquery()
        )
        query = query.where(Lead.id.in_(select(score_subq.c.lead_id)))

    # Get total count before pagination
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply sorting
    if sort_by == "company_name":
        order_col = Lead.company_name
    elif sort_by == "score":
        # Sort by best score (requires subquery)
        score_subq = (
            select(LeadScore.lead_id, func.max(LeadScore.score).label('best_score'))
            .group_by(LeadScore.lead_id)
            .subquery()
        )
        query = query.outerjoin(score_subq, Lead.id == score_subq.c.lead_id)
        order_col = score_subq.c.best_score
    else:  # created_at or default
        order_col = Lead.created_at

    if sort_order.lower() == "asc":
        query = query.order_by(order_col.asc())
    else:
        query = query.order_by(order_col.desc())

    # Apply pagination
    query = query.offset(skip).limit(limit)

    # Execute query
    result = await db.execute(query)
    leads = result.scalars().all()

    # Optionally load signals and scores
    response_leads = []
    for lead in leads:
        lead_data = {
            "id": lead.id,
            "company_name": lead.company_name,
            "website": lead.website,
            "linkedin_url": lead.linkedin_url,
            "country": lead.country,
            "city": lead.city,
            "sector": lead.sector,
            "employee_count": lead.employee_count,
            "is_multinational": lead.is_multinational,
            "is_exporter": lead.is_exporter,
            "under_audit": lead.under_audit,
            "scraped_data": lead.scraped_data,
            "status": lead.status,
            "created_at": lead.created_at,
            "updated_at": lead.updated_at,
        }

        if include_signals:
            signals_result = await db.execute(
                select(LeadSignal)
                .where(LeadSignal.lead_id == lead.id)
                .order_by(LeadSignal.detected_at.desc())
            )
            lead_data["signals"] = signals_result.scalars().all()

        if include_scores:
            scores_result = await db.execute(
                select(LeadScore)
                .where(LeadScore.lead_id == lead.id)
                .order_by(LeadScore.score.desc())
            )
            lead_data["scores"] = scores_result.scalars().all()

        response_leads.append(lead_data)

    return PaginatedLeadsResponse(
        leads=response_leads,
        total=total,
        skip=skip,
        limit=limit,
        has_more=(skip + limit) < total,
    )


@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get single lead by ID."""
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()

    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )

    return lead


@router.post("/{lead_id}/enrich-linkedin")
async def enrich_lead_linkedin(
    lead_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Trigger LinkedIn enrichment for a single lead.

    This endpoint queues an Apify LinkedIn scraping task for the lead.
    Requires APIFY_API_TOKEN to be set in environment.

    Returns task ID for tracking.
    """
    # Check if lead exists
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()

    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )

    if not lead.linkedin_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lead has no LinkedIn URL"
        )

    # Import and trigger Celery task
    from app.workers.tasks.apify_linkedin import enrich_single_lead_task

    task = enrich_single_lead_task.delay(lead_id)

    return {
        "message": f"LinkedIn enrichment queued for {lead.company_name}",
        "task_id": task.id,
        "lead_id": lead_id,
        "linkedin_url": lead.linkedin_url
    }


# ─── Status Management ────────────────────────────────────────────────────────


@router.patch("/{lead_id}/status", response_model=LeadDetailResponse)
async def update_lead_status(
    lead_id: int,
    status_update: LeadStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update lead status with audit trail.

    Creates a status history record and updates lead fields:
    - status: new status value
    - status_notes: latest notes about this lead
    - assigned_to_id: who is responsible for this lead
    - last_contacted: auto-set to now if status is 'contacted'
    - updated_at: auto-updated

    Returns updated lead with all status tracking fields.
    """
    # Load lead
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()

    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lead {lead_id} not found"
        )

    # Save old status for history
    old_status = lead.status

    # Update lead fields
    lead.status = status_update.status

    if status_update.notes:
        lead.status_notes = status_update.notes

    if status_update.assigned_to_id is not None:
        # Verify user exists
        user_result = await db.execute(
            select(User).where(User.id == status_update.assigned_to_id)
        )
        if not user_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User {status_update.assigned_to_id} not found"
            )
        lead.assigned_to_id = status_update.assigned_to_id

    # Auto-set last_contacted if status is 'contacted'
    if status_update.status == LeadStatus.contacted:
        lead.last_contacted = datetime.utcnow()

    # Create status history record
    history = LeadStatusHistory(
        lead_id=lead_id,
        old_status=old_status,
        new_status=status_update.status,
        changed_by_id=current_user.id,
        notes=status_update.notes
    )
    db.add(history)

    await db.commit()
    await db.refresh(lead)

    return lead


@router.get("/{lead_id}/status/history", response_model=List[LeadStatusHistoryResponse])
async def get_lead_status_history(
    lead_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get complete status history for a lead.

    Returns all status changes in chronological order (oldest first).
    Useful for seeing full sales pipeline journey.
    """
    # Verify lead exists
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()

    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lead {lead_id} not found"
        )

    # Load status history
    result = await db.execute(
        select(LeadStatusHistory)
        .where(LeadStatusHistory.lead_id == lead_id)
        .order_by(LeadStatusHistory.changed_at.asc())
    )
    history = result.scalars().all()

    return history


@router.get("/{lead_id}/detail", response_model=LeadDetailResponse)
async def get_lead_detail(
    lead_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get full lead details including status tracking fields.

    Returns:
    - All basic lead fields
    - Status and status_notes
    - assigned_to_id (who owns this lead)
    - last_contacted (when they were last contacted)
    """
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()

    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lead {lead_id} not found"
        )

    return lead


@router.get("/search/quick")
async def quick_search(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(default=10, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Quick search for leads by company name.

    Returns minimal lead info for autocomplete/typeahead.
    Searches company name only for fast response.
    """
    query = (
        select(Lead.id, Lead.company_name, Lead.city, Lead.sector)
        .where(Lead.company_name.ilike(f"%{q}%"))
        .limit(limit)
    )

    result = await db.execute(query)
    leads = result.all()

    return [
        {
            "id": lead.id,
            "company_name": lead.company_name,
            "city": lead.city,
            "sector": lead.sector,
        }
        for lead in leads
    ]


@router.get("/filters/options")
async def get_filter_options(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get all available filter options for dropdown menus.

    Returns unique values for:
    - sectors
    - cities
    - countries
    - statuses

    Used to populate filter dropdowns in UI.
    """
    # Get unique sectors
    sectors_result = await db.execute(
        select(Lead.sector).distinct().where(Lead.sector.isnot(None)).order_by(Lead.sector)
    )
    sectors = [s[0] for s in sectors_result.all()]

    # Get unique cities
    cities_result = await db.execute(
        select(Lead.city).distinct().where(Lead.city.isnot(None)).order_by(Lead.city)
    )
    cities = [c[0] for c in cities_result.all()]

    # Get unique countries
    countries_result = await db.execute(
        select(Lead.country).distinct().where(Lead.country.isnot(None)).order_by(Lead.country)
    )
    countries = [c[0] for c in countries_result.all()]

    # Statuses (from enum)
    statuses = [status.value for status in LeadStatus]

    return {
        "sectors": sectors,
        "cities": cities,
        "countries": countries,
        "statuses": statuses,
    }

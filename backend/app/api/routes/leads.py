"""
Leads management routes: import, list, get, update.
"""
import csv
import io
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.schemas.leads import LeadResponse, CSVImportResponse
from app.models.models import Lead, LeadStatus
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


@router.get("/", response_model=List[LeadResponse])
async def get_leads(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all leads (paginated in future)."""
    result = await db.execute(select(Lead))
    leads = result.scalars().all()
    return leads


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

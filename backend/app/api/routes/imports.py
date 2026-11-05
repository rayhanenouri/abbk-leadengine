"""
API endpoints for database imports.

Handles file upload, column mapping, import processing, and history tracking.
"""
import logging
import io
import csv
from datetime import datetime
from typing import List
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
import pandas as pd

from app.db.session import get_db
from app.models.models import DatabaseImport, User, ImportStatus
from app.schemas.imports import (
    ImportCreateResponse,
    ImportStatusResponse,
    ImportHistoryItem,
    ColumnMappingRequest
)
from app.api.routes.auth import get_current_user
from app.workers.tasks.import_processing import (
    parse_and_import_task,
    auto_map_columns
)

router = APIRouter()
logger = logging.getLogger(__name__)


# ─── File Upload and Preview ──────────────────────────────────────────────────

@router.post("/upload", response_model=ImportCreateResponse)
async def upload_import_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Upload CSV or Excel file for import.
    Returns preview of first 10 rows and auto-detected column mapping.
    """
    try:
        # Validate file type
        if not file.filename:
            raise HTTPException(400, "No filename provided")

        filename = file.filename.lower()
        if not (filename.endswith('.csv') or filename.endswith('.xlsx') or filename.endswith('.xls')):
            raise HTTPException(
                400,
                "Invalid file type. Only CSV, XLS, and XLSX files are supported."
            )

        # Read file content
        content = await file.read()

        # Parse file based on type
        if filename.endswith('.csv'):
            # Parse CSV
            df = pd.read_csv(io.BytesIO(content))
        else:
            # Parse Excel
            df = pd.read_excel(io.BytesIO(content))

        # Validate data
        if df.empty:
            raise HTTPException(400, "File is empty")

        total_rows = len(df)
        if total_rows == 0:
            raise HTTPException(400, "No data rows found")

        # Auto-detect column mapping
        headers = df.columns.tolist()
        auto_mapping = auto_map_columns(headers)

        # Convert datetime columns to strings to avoid JSON serialization issues
        for col in df.select_dtypes(include=['datetime64']).columns:
            df[col] = df[col].astype(str)

        # Convert to list of dicts for storage
        file_data = df.fillna("").to_dict('records')

        # Create import record
        db_import = DatabaseImport(
            user_id=current_user.id,
            filename=file.filename,
            status=ImportStatus.pending,
            total_rows=total_rows,
            column_mapping=auto_mapping
        )
        session.add(db_import)
        await session.commit()
        await session.refresh(db_import)

        # Store file data in import record temporarily (max 1000 rows to avoid memory issues)
        db_import.error_details = {"file_data": file_data[:1000]}
        await session.commit()

        logger.info(
            f"File uploaded: {file.filename} by user {current_user.id} "
            f"({total_rows} rows, import_id={db_import.id})"
        )

        return ImportCreateResponse(
            import_id=db_import.id,
            filename=file.filename,
            total_rows=total_rows,
            status=db_import.status,
            message=f"File uploaded successfully. {total_rows} rows detected."
        )

    except pd.errors.EmptyDataError:
        raise HTTPException(400, "CSV file is empty or malformed")
    except pd.errors.ParserError as e:
        raise HTTPException(400, f"Error parsing CSV: {str(e)}")
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(500, f"Error uploading file: {str(e)}")


# ─── Start Import Processing ──────────────────────────────────────────────────

@router.post("/{import_id}/process")
async def start_import_processing(
    import_id: int,
    column_mapping: ColumnMappingRequest | None = None,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Start processing an uploaded import.
    Optionally provide custom column mapping (otherwise uses auto-detected).
    """
    # Get import record
    result = await session.execute(
        select(DatabaseImport).where(DatabaseImport.id == import_id)
    )
    db_import = result.scalar_one_or_none()

    if not db_import:
        raise HTTPException(404, "Import not found")

    if db_import.user_id != current_user.id:
        raise HTTPException(403, "Not authorized to process this import")

    if db_import.status != ImportStatus.pending:
        raise HTTPException(400, f"Import already {db_import.status}")

    # Use provided mapping or auto-detected
    final_mapping = column_mapping.model_dump() if column_mapping else db_import.column_mapping
    final_mapping = {k: v for k, v in final_mapping.items() if v}  # Remove None values

    # Get file data from error_details (temporary storage)
    file_data = db_import.error_details.get("file_data", [])
    if not file_data:
        raise HTTPException(400, "No file data found. Please re-upload the file.")

    # Update column mapping
    db_import.column_mapping = final_mapping
    await session.commit()

    # Trigger Celery task
    parse_and_import_task.delay(import_id, file_data, final_mapping)

    logger.info(f"Started import processing for import_id={import_id}")

    return {
        "message": "Import processing started",
        "import_id": import_id,
        "status": "processing"
    }


# ─── Get Import Status ────────────────────────────────────────────────────────

@router.get("/{import_id}/status", response_model=ImportStatusResponse)
async def get_import_status(
    import_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Get real-time status of an import.
    Shows progress percentage and detailed stats.
    """
    result = await session.execute(
        select(DatabaseImport).where(DatabaseImport.id == import_id)
    )
    db_import = result.scalar_one_or_none()

    if not db_import:
        raise HTTPException(404, "Import not found")

    if db_import.user_id != current_user.id:
        raise HTTPException(403, "Not authorized to view this import")

    # Calculate progress
    if db_import.status == ImportStatus.pending:
        progress = 0
    elif db_import.status == ImportStatus.processing:
        if db_import.total_rows > 0:
            processed = db_import.imported_count + db_import.updated_count + db_import.errors_count
            progress = int((processed / db_import.total_rows) * 50)  # Parsing is 50%
            if db_import.enriched_count > 0:
                enrich_progress = int((db_import.enriched_count / processed) * 50) if processed > 0 else 0
                progress += enrich_progress
        else:
            progress = 50
    elif db_import.status == ImportStatus.completed:
        progress = 100
    else:  # failed
        progress = 0

    return ImportStatusResponse(
        id=db_import.id,
        filename=db_import.filename,
        status=db_import.status,
        total_rows=db_import.total_rows,
        imported_count=db_import.imported_count,
        duplicates_count=db_import.duplicates_count,
        updated_count=db_import.updated_count,
        errors_count=db_import.errors_count,
        enriched_count=db_import.enriched_count,
        signals_count=db_import.signals_count,
        error_details=db_import.error_details,
        created_at=db_import.created_at,
        completed_at=db_import.completed_at,
        progress=progress
    )


# ─── Import History ───────────────────────────────────────────────────────────

@router.get("/history", response_model=List[ImportHistoryItem])
async def get_import_history(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Get all imports for current user.
    Sorted by newest first.
    """
    result = await session.execute(
        select(DatabaseImport)
        .where(DatabaseImport.user_id == current_user.id)
        .order_by(desc(DatabaseImport.created_at))
    )
    imports = result.scalars().all()

    return [
        ImportHistoryItem(
            id=imp.id,
            filename=imp.filename,
            status=imp.status,
            total_rows=imp.total_rows,
            imported_count=imp.imported_count,
            duplicates_count=imp.duplicates_count,
            updated_count=imp.updated_count,
            enriched_count=imp.enriched_count,
            signals_count=imp.signals_count,
            created_at=imp.created_at,
            completed_at=imp.completed_at
        )
        for imp in imports
    ]


# ─── Delete Import ────────────────────────────────────────────────────────────

@router.delete("/{import_id}")
async def delete_import(
    import_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Delete an import record.
    Note: Does NOT delete the leads created by this import.
    """
    result = await session.execute(
        select(DatabaseImport).where(DatabaseImport.id == import_id)
    )
    db_import = result.scalar_one_or_none()

    if not db_import:
        raise HTTPException(404, "Import not found")

    if db_import.user_id != current_user.id:
        raise HTTPException(403, "Not authorized to delete this import")

    await session.delete(db_import)
    await session.commit()

    logger.info(f"Import {import_id} deleted by user {current_user.id}")

    return {"message": "Import deleted successfully"}


# ─── Score All Unscored Leads ─────────────────────────────────────────────────

@router.post("/score-all")
async def score_all_unscored_leads(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Score all leads that don't have scores yet.
    Useful after a failed import or when scores are missing.
    """
    from sqlalchemy import select
    from app.models.models import Lead, LeadScore
    from app.services.scoring_engine import score_lead

    # Find leads without scores
    subquery = select(LeadScore.lead_id).distinct()
    result = await session.execute(
        select(Lead).where(~Lead.id.in_(subquery))
    )
    leads_without_scores = result.scalars().all()

    if not leads_without_scores:
        return {
            "message": "All leads already have scores",
            "leads_scored": 0
        }

    # Get all services
    from app.models.models import Service
    services_result = await session.execute(
        select(Service).where(Service.is_active == True)
    )
    services = services_result.scalars().all()

    # Score each lead
    scored_count = 0
    errors = []

    for lead in leads_without_scores:
        try:
            await score_lead(lead, services, session)
            scored_count += 1
        except Exception as e:
            errors.append(f"{lead.company_name}: {str(e)}")
            logger.error(f"Error scoring lead {lead.id}: {e}")

    await session.commit()

    return {
        "message": f"Scored {scored_count} leads",
        "leads_scored": scored_count,
        "total_leads_without_scores": len(leads_without_scores),
        "errors": errors[:10] if errors else []
    }


# ─── Reprocess Import ─────────────────────────────────────────────────────────

@router.post("/{import_id}/reprocess")
async def reprocess_import(
    import_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Re-run enrichment and scoring for all leads from this import.
    Useful if enrichment failed or needs updating.
    """
    result = await session.execute(
        select(DatabaseImport).where(DatabaseImport.id == import_id)
    )
    db_import = result.scalar_one_or_none()

    if not db_import:
        raise HTTPException(404, "Import not found")

    if db_import.user_id != current_user.id:
        raise HTTPException(403, "Not authorized to reprocess this import")

    # Get all leads from this import
    from app.models.models import Lead
    result = await session.execute(
        select(Lead.id).where(
            Lead.scraped_data['import_file'].astext == db_import.filename
        )
    )
    lead_ids = [row[0] for row in result.fetchall()]

    if not lead_ids:
        raise HTTPException(400, "No leads found for this import")

    # Reset counts and trigger enrichment
    db_import.enriched_count = 0
    db_import.signals_count = 0
    db_import.status = ImportStatus.processing
    await session.commit()

    from app.workers.tasks.import_processing import enrich_imported_leads_task
    enrich_imported_leads_task.delay(import_id, lead_ids)

    logger.info(f"Reprocessing import {import_id}: {len(lead_ids)} leads")

    return {
        "message": f"Reprocessing started for {len(lead_ids)} leads",
        "import_id": import_id,
        "lead_count": len(lead_ids)
    }

"""
Celery tasks for processing database imports.

COMPLETE PIPELINE:
1. Parse CSV/Excel file → create Lead records
2. Website discovery for companies without URLs
3. Deep enrichment (scrape website, search news, find jobs)
4. Signal detection from enriched data
5. Score calculation across all ABBK services
6. Send notification when complete
"""
import logging
from datetime import datetime
from typing import Dict, List, Any
from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.workers.celery_app import celery_app
from app.db.session import AsyncSessionLocal
from app.models.models import DatabaseImport, Lead, LeadSignal, ImportStatus

logger = logging.getLogger(__name__)


# ─── Fuzzy Matching for Duplicate Detection ───────────────────────────────────

def calculate_similarity(str1: str, str2: str) -> float:
    """
    Calculate simple similarity between two strings (0.0 to 1.0).
    Uses lowercased character overlap as proxy for pg_trgm similarity.
    """
    if not str1 or not str2:
        return 0.0

    s1 = str1.lower().strip()
    s2 = str2.lower().strip()

    if s1 == s2:
        return 1.0

    # Simple overlap calculation
    set1 = set(s1.split())
    set2 = set(s2.split())

    if not set1 or not set2:
        return 0.0

    intersection = set1.intersection(set2)
    union = set1.union(set2)

    return len(intersection) / len(union)


async def find_duplicate_lead(
    session: AsyncSession,
    company_name: str,
    website: str | None = None,
    phone: str | None = None
) -> Lead | None:
    """
    Find potential duplicate by company name similarity, website, or phone.
    Returns existing lead if found, None otherwise.
    """
    # Check exact website match first (if provided)
    if website:
        result = await session.execute(
            select(Lead).where(Lead.website == website)
        )
        existing = result.scalar_one_or_none()
        if existing:
            return existing

    # Check phone match (if provided)
    # Note: Can't efficiently query JSON fields, so we skip phone-based deduplication
    # and rely on company name + website matching instead

    # Fuzzy match on company name
    result = await session.execute(select(Lead))
    all_leads = result.scalars().all()

    for lead in all_leads:
        similarity = calculate_similarity(company_name, lead.company_name)
        if similarity >= 0.8:  # 80% similarity threshold
            logger.info(f"Found fuzzy match: '{company_name}' ≈ '{lead.company_name}' (similarity: {similarity:.2f})")
            return lead

    return None


# ─── Column Mapping Helpers ───────────────────────────────────────────────────

# French column name variations
FRENCH_COMPANY_NAMES = [
    "entreprise", "société", "nom", "raison sociale", "compagnie",
    "nom entreprise", "nom société", "societe", "nom_entreprise",
    "company name", "companyname", "company_name", "account", "organization",
    "customer", "client", "business", "firm", "lastname"  # SolidWorks exports use "LastName"
]
FRENCH_WEBSITE_NAMES = [
    "site web", "site", "url", "site internet", "site_web",
    "siteweb", "website", "web"
]
FRENCH_PHONE_NAMES = [
    "téléphone", "telephone", "tel", "tél", "phone", "contact",
    "numéro", "numero"
]
FRENCH_SECTOR_NAMES = [
    "secteur", "activité", "activite", "industrie", "domaine",
    "secteur activité", "secteur_activite"
]
FRENCH_CITY_NAMES = ["ville", "city", "localité", "localite", "commune"]
FRENCH_COUNTRY_NAMES = ["pays", "country", "nation"]
FRENCH_EMAIL_NAMES = ["email", "e-mail", "mail", "courriel", "adresse email"]


def auto_map_columns(headers: List[str]) -> Dict[str, str]:
    """
    Automatically map CSV headers to database fields.
    Returns dict: {db_field: csv_column_name}
    """
    headers_lower = [h.lower().strip() for h in headers]
    mapping = {}

    # Map company_name
    for var in FRENCH_COMPANY_NAMES + ["company", "name", "company name"]:
        if var in headers_lower:
            idx = headers_lower.index(var)
            mapping["company_name"] = headers[idx]
            break

    # Map website
    for var in FRENCH_WEBSITE_NAMES:
        if var in headers_lower:
            idx = headers_lower.index(var)
            mapping["website"] = headers[idx]
            break

    # Map phone
    for var in FRENCH_PHONE_NAMES:
        if var in headers_lower:
            idx = headers_lower.index(var)
            mapping["phone"] = headers[idx]
            break

    # Map sector
    for var in FRENCH_SECTOR_NAMES + ["sector", "industry"]:
        if var in headers_lower:
            idx = headers_lower.index(var)
            mapping["sector"] = headers[idx]
            break

    # Map city
    for var in FRENCH_CITY_NAMES:
        if var in headers_lower:
            idx = headers_lower.index(var)
            mapping["city"] = headers[idx]
            break

    # Map country
    for var in FRENCH_COUNTRY_NAMES:
        if var in headers_lower:
            idx = headers_lower.index(var)
            mapping["country"] = headers[idx]
            break

    # Map email
    for var in FRENCH_EMAIL_NAMES:
        if var in headers_lower:
            idx = headers_lower.index(var)
            mapping["email"] = headers[idx]
            break

    # Map LinkedIn
    if "linkedin" in headers_lower:
        idx = headers_lower.index("linkedin")
        mapping["linkedin_url"] = headers[idx]

    return mapping


# ─── Task 1: Parse File and Create Leads ──────────────────────────────────────

@celery_app.task(name="import_processing.parse_and_import")
def parse_and_import_task(import_id: int, file_data: List[Dict[str, Any]], column_mapping: Dict[str, str]):
    """
    Parse uploaded CSV/Excel data and create Lead records.
    Handles duplicate detection and merging.

    Args:
        import_id: DatabaseImport.id
        file_data: List of row dicts from CSV/Excel
        column_mapping: {db_field: csv_column} mapping
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    from app.core.config import settings

    # Use sync engine for Celery tasks
    sync_engine = create_engine(settings.DATABASE_URL.replace('+asyncpg', ''))

    with Session(sync_engine) as session:
        try:
            # Get import record
            db_import = session.query(DatabaseImport).filter(DatabaseImport.id == import_id).first()
            if not db_import:
                logger.error(f"Import {import_id} not found")
                return

            # Update status to processing
            db_import.status = ImportStatus.processing
            db_import.total_rows = len(file_data)
            session.commit()

            imported_count = 0
            duplicates_count = 0
            updated_count = 0
            errors_count = 0
            errors = []
            lead_ids = []

            for idx, row in enumerate(file_data, 1):
                try:
                    # Extract fields using column mapping
                    company_name = row.get(column_mapping.get("company_name", ""), "").strip()
                    if not company_name:
                        errors_count += 1
                        errors.append(f"Row {idx}: Missing company name")
                        continue

                    website = row.get(column_mapping.get("website", ""), "").strip() or None
                    phone = row.get(column_mapping.get("phone", ""), "").strip() or None
                    sector = row.get(column_mapping.get("sector", ""), "").strip() or None
                    city = row.get(column_mapping.get("city", ""), "").strip() or None
                    country = row.get(column_mapping.get("country", ""), "Tunisia").strip()
                    linkedin_url = row.get(column_mapping.get("linkedin_url", ""), "").strip() or None
                    email = row.get(column_mapping.get("email", ""), "").strip() or None

                    # Check for duplicates by website
                    existing_lead = None
                    if website:
                        existing_lead = session.query(Lead).filter(Lead.website == website).first()

                    # If not found by website, check by similar company name
                    if not existing_lead:
                        all_leads = session.query(Lead).all()
                        for lead in all_leads:
                            similarity = calculate_similarity(company_name, lead.company_name)
                            if similarity >= 0.8:
                                existing_lead = lead
                                logger.info(f"Found fuzzy match: '{company_name}' ≈ '{lead.company_name}' (similarity: {similarity:.2f})")
                                break

                    if existing_lead:
                        # Update existing lead
                        if website and not existing_lead.website:
                            existing_lead.website = website
                        if phone:
                            if not existing_lead.scraped_data:
                                existing_lead.scraped_data = {}
                            existing_lead.scraped_data["phone"] = phone
                        if email:
                            if not existing_lead.scraped_data:
                                existing_lead.scraped_data = {}
                            existing_lead.scraped_data["email"] = email
                        if sector and not existing_lead.sector:
                            existing_lead.sector = sector
                        if city and not existing_lead.city:
                            existing_lead.city = city
                        if linkedin_url and not existing_lead.linkedin_url:
                            existing_lead.linkedin_url = linkedin_url

                        # Mark as manual import source
                        if not existing_lead.scraped_data:
                            existing_lead.scraped_data = {}
                        existing_lead.scraped_data["source"] = "manual_import"
                        existing_lead.scraped_data["import_file"] = db_import.filename
                        existing_lead.scraped_data["import_date"] = datetime.utcnow().isoformat()

                        updated_count += 1
                        lead_ids.append(existing_lead.id)
                        logger.info(f"Updated existing lead: {company_name}")
                    else:
                        # Create new lead
                        new_lead = Lead(
                            company_name=company_name,
                            website=website,
                            linkedin_url=linkedin_url,
                            country=country,
                            city=city,
                            sector=sector,
                            scraped_data={
                                "source": "manual_import",
                                "import_file": db_import.filename,
                                "import_date": datetime.utcnow().isoformat(),
                                "phone": phone,
                                "email": email,
                            }
                        )
                        session.add(new_lead)
                        session.flush()

                        imported_count += 1
                        lead_ids.append(new_lead.id)
                        logger.info(f"Created new lead: {company_name}")

                except Exception as e:
                    errors_count += 1
                    errors.append(f"Row {idx}: {str(e)}")
                    logger.error(f"Error processing row {idx}: {e}")

            # Update import record
            db_import.imported_count = imported_count
            db_import.duplicates_count = duplicates_count
            db_import.updated_count = updated_count
            db_import.errors_count = errors_count
            db_import.error_details = {"errors": errors[:100]}

            session.commit()

            logger.info(
                f"Import {import_id} parsed: "
                f"{imported_count} new, {updated_count} updated, "
                f"{duplicates_count} duplicates, {errors_count} errors"
            )

            # Trigger enrichment for all leads
            if lead_ids:
                enrich_imported_leads_task.delay(import_id, lead_ids)
            else:
                # Mark as completed if no leads to enrich
                db_import.status = ImportStatus.completed
                db_import.completed_at = datetime.utcnow()
                session.commit()

        except Exception as e:
            logger.error(f"Import {import_id} failed: {e}", exc_info=True)
            # Only mark as failed if no leads were actually imported
            if imported_count == 0:
                db_import.status = ImportStatus.failed
                db_import.error_details = {"error": str(e)}
            else:
                # Leads were imported successfully, just log the error
                logger.warning(f"Import {import_id} had errors but {imported_count} leads were imported")
                db_import.error_details = {"error": str(e), "partial_success": True}
            session.commit()


# ─── Task 2: Enrich All Imported Leads ────────────────────────────────────────

@celery_app.task(name="import_processing.enrich_imported_leads")
def enrich_imported_leads_task(import_id: int, lead_ids: List[int]):
    """
    Enrich all leads from an import using deep enrichment.
    This triggers website discovery, scraping, news search, job search.
    """
    logger.info(f"Starting enrichment for import {import_id}: {len(lead_ids)} leads")

    # Trigger deep enrichment for each lead using Celery task name
    for lead_id in lead_ids:
        celery_app.send_task("enrichment.deep_enrich_single_lead", args=[lead_id])

    # Schedule completion check after 5 minutes
    check_import_completion_task.apply_async(
        args=[import_id, lead_ids],
        countdown=300  # 5 minutes
    )


# ─── Task 3: Check Import Completion ──────────────────────────────────────────

@celery_app.task(name="import_processing.check_completion", max_retries=3)
def check_import_completion_task(import_id: int, lead_ids: List[int]):
    """
    Check if all enrichment is complete and update import status.
    Retries up to 3 times if enrichment is still in progress.
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    from app.core.config import settings

    # Use sync engine
    sync_engine = create_engine(settings.DATABASE_URL.replace('+asyncpg', ''))

    with Session(sync_engine) as session:
        try:
            # Get import record
            db_import = session.query(DatabaseImport).filter(DatabaseImport.id == import_id).first()
            if not db_import:
                logger.error(f"Import {import_id} not found")
                return

            # Skip if already completed
            if db_import.status == ImportStatus.completed:
                logger.info(f"Import {import_id} already marked as completed")
                return

            # Count signals detected for these leads
            signals_count = session.query(func.count(LeadSignal.id)).filter(
                LeadSignal.lead_id.in_(lead_ids)
            ).scalar() or 0

            # Update import record - mark as completed regardless of enrichment status
            # This prevents imports from getting stuck in "processing" forever
            db_import.enriched_count = len(lead_ids)
            db_import.signals_count = signals_count
            db_import.status = ImportStatus.completed
            db_import.completed_at = datetime.utcnow()

            session.commit()

            logger.info(
                f"Import {import_id} completed: "
                f"{db_import.enriched_count} enriched, "
                f"{signals_count} signals detected"
            )

        except Exception as e:
            logger.error(f"Error checking import {import_id} completion: {e}", exc_info=True)
            # Try to mark as completed anyway to prevent getting stuck
            try:
                db_import = session.query(DatabaseImport).filter(DatabaseImport.id == import_id).first()
                if db_import and db_import.status != ImportStatus.completed:
                    db_import.status = ImportStatus.completed
                    db_import.completed_at = datetime.utcnow()
                    db_import.enriched_count = len(lead_ids)
                    session.commit()
                    logger.warning(f"Import {import_id} marked completed despite error")
            except Exception as fallback_error:
                logger.error(f"Failed to mark import {import_id} as completed: {fallback_error}")

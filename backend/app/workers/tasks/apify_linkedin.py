"""
Apify LinkedIn enrichment tasks.
Uses Apify LinkedIn Company Scraper to extract:
- Employee count
- Description
- Specialties
- Industry
- Recent hires and job titles
- Engineering roles detection
"""

import os
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.workers.celery_app import celery_app
from app.db.session import AsyncSessionLocal
from app.models.models import Lead, LeadSignal

logger = logging.getLogger(__name__)

APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN")
APIFY_LINKEDIN_ACTOR_ID = "apify/linkedin-company-scraper"


async def enrich_lead_with_linkedin(db: AsyncSession, lead: Lead) -> bool:
    """
    Enrich a single lead with LinkedIn data.

    Args:
        db: Database session
        lead: Lead to enrich

    Returns:
        True if enrichment succeeded, False otherwise
    """
    if not APIFY_API_TOKEN:
        logger.warning("APIFY_API_TOKEN not set - skipping LinkedIn enrichment")
        return False

    if not lead.linkedin_url:
        logger.info(f"Lead {lead.id} has no LinkedIn URL - skipping")
        return False

    try:
        # Import apify client
        try:
            from apify_client import ApifyClient
        except ImportError:
            logger.error("apify-client not installed. Run: pip install apify-client")
            return False

        client = ApifyClient(APIFY_API_TOKEN)

        # Prepare input for LinkedIn Company Scraper
        run_input = {
            "startUrls": [{"url": lead.linkedin_url}],
            "maxEmployees": 100,  # Scrape up to 100 employee profiles
        }

        logger.info(f"Starting Apify LinkedIn scrape for lead {lead.id}: {lead.linkedin_url}")

        # Run the Actor and wait for it to finish
        run = client.actor(APIFY_LINKEDIN_ACTOR_ID).call(run_input=run_input)

        # Fetch results from the Actor's dataset
        results = []
        for item in client.dataset(run["defaultDatasetId"]).iterate_items():
            results.append(item)

        if not results:
            logger.warning(f"No LinkedIn data returned for lead {lead.id}")
            return False

        company_data = results[0]  # First result is the company profile

        # Update lead with LinkedIn data
        scraped_data = lead.scraped_data or {}
        scraped_data["linkedin"] = {
            "scraped_at": datetime.utcnow().isoformat(),
            "employee_count": company_data.get("staffCount"),
            "description": company_data.get("description"),
            "specialties": company_data.get("specialties", []),
            "industry": company_data.get("industry"),
            "headquarters": company_data.get("headquarters"),
            "founded": company_data.get("founded"),
            "company_type": company_data.get("companyType"),
            "website": company_data.get("website"),
        }

        # Extract employee data
        employees = []
        for result in results[1:]:  # Skip first item (company profile)
            if result.get("firstName") or result.get("lastName"):
                employees.append({
                    "name": f"{result.get('firstName', '')} {result.get('lastName', '')}".strip(),
                    "title": result.get("title"),
                    "location": result.get("location"),
                    "profile_url": result.get("url"),
                })

        scraped_data["linkedin"]["employees"] = employees

        # Update employee count if we got it
        if company_data.get("staffCount"):
            lead.employee_count = company_data.get("staffCount")

        # Update lead scraped_data
        await db.execute(
            update(Lead)
            .where(Lead.id == lead.id)
            .values(
                scraped_data=scraped_data,
                employee_count=company_data.get("staffCount") or lead.employee_count,
                updated_at=datetime.utcnow()
            )
        )

        # Detect engineering roles
        engineering_keywords = [
            "ingénieur", "engineer", "conception", "design", "CAD", "bureau d'études",
            "R&D", "recherche", "développement", "mécanique", "mechanical", "production",
            "simulation", "calcul", "fabrication", "manufacturing", "industriel"
        ]

        engineering_roles = []
        for emp in employees:
            title = emp.get("title", "").lower()
            if any(keyword.lower() in title for keyword in engineering_keywords):
                engineering_roles.append(emp)

        # Create signals for engineering roles detected
        if engineering_roles:
            role_names = [f"{emp['name']} - {emp['title']}" for emp in engineering_roles[:5]]
            signal = LeadSignal(
                lead_id=lead.id,
                signal_type="role_detected",
                title=f"{len(engineering_roles)} engineering roles found on LinkedIn",
                detail=f"Engineering roles: {', '.join(role_names)}",
                source_url=lead.linkedin_url,
                detected_at=datetime.utcnow()
            )
            db.add(signal)

        # Detect recent hires (if we can determine hire date - Apify may provide this)
        # This would require additional logic based on Apify's output format

        await db.commit()
        logger.info(f"Successfully enriched lead {lead.id} with LinkedIn data: {len(employees)} employees, {len(engineering_roles)} engineering roles")
        return True

    except Exception as e:
        logger.error(f"Failed to enrich lead {lead.id} with LinkedIn: {str(e)}")
        await db.rollback()
        return False


@celery_app.task(name="apify_linkedin.enrich_all_leads")
def enrich_all_leads_task() -> Dict[str, Any]:
    """
    Celery task to enrich all leads with LinkedIn URLs.
    Runs periodically via Celery Beat.

    Returns:
        Dictionary with task results
    """
    import asyncio

    async def _enrich():
        async with AsyncSessionLocal() as db:
            # Find all leads with LinkedIn URLs that haven't been enriched recently
            result = await db.execute(
                select(Lead).where(
                    Lead.linkedin_url.isnot(None),
                    Lead.linkedin_url != ""
                )
            )
            leads = result.scalars().all()

            logger.info(f"Found {len(leads)} leads with LinkedIn URLs")

            enriched_count = 0
            failed_count = 0
            skipped_count = 0

            for lead in leads:
                # Check if already enriched recently (last 7 days)
                if lead.scraped_data and "linkedin" in lead.scraped_data:
                    scraped_at = lead.scraped_data["linkedin"].get("scraped_at")
                    if scraped_at:
                        scraped_date = datetime.fromisoformat(scraped_at)
                        days_old = (datetime.utcnow() - scraped_date).days
                        if days_old < 7:
                            logger.info(f"Lead {lead.id} LinkedIn data is {days_old} days old - skipping")
                            skipped_count += 1
                            continue

                success = await enrich_lead_with_linkedin(db, lead)
                if success:
                    enriched_count += 1
                else:
                    failed_count += 1

                # Rate limiting: wait between requests to avoid overwhelming Apify
                await asyncio.sleep(2)

            return {
                "total_leads": len(leads),
                "enriched": enriched_count,
                "failed": failed_count,
                "skipped": skipped_count,
                "timestamp": datetime.utcnow().isoformat()
            }

    loop = asyncio.get_event_loop()
    if loop.is_running():
        # If event loop is already running (shouldn't happen in Celery worker)
        logger.warning("Event loop already running - creating new loop")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(_enrich())


@celery_app.task(name="apify_linkedin.enrich_single_lead")
def enrich_single_lead_task(lead_id: int) -> Dict[str, Any]:
    """
    Celery task to enrich a single lead with LinkedIn data.
    Can be triggered on-demand when a new lead is created.

    Args:
        lead_id: ID of lead to enrich

    Returns:
        Dictionary with task results
    """
    import asyncio

    async def _enrich():
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Lead).where(Lead.id == lead_id))
            lead = result.scalar_one_or_none()

            if not lead:
                return {"success": False, "error": f"Lead {lead_id} not found"}

            success = await enrich_lead_with_linkedin(db, lead)

            return {
                "success": success,
                "lead_id": lead_id,
                "company_name": lead.company_name,
                "timestamp": datetime.utcnow().isoformat()
            }

    loop = asyncio.get_event_loop()
    if loop.is_running():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(_enrich())

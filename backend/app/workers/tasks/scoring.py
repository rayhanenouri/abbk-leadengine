"""
Celery tasks for lead scoring.

Handles automatic score calculation and recalculation triggered by:
- New signals detected (real-time recalculation)
- Scheduled batch recalculation (daily at 4am)
- Manual recalculation via API
"""
import asyncio
from typing import Dict
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.workers.celery_app import celery_app
from app.db.session import AsyncSessionLocal
from app.models.models import Lead, Service
from app.services.scoring_engine import score_lead

logger = logging.getLogger(__name__)


async def _recalculate_all_scores_async() -> Dict:
    """
    Recalculate scores for all leads in the database.

    Called by scheduled task (daily at 4am) and on-demand via API.

    Returns:
        Dict with statistics about recalculation
    """
    logger.info("Starting batch score recalculation for all leads")

    async with AsyncSessionLocal() as db_session:
        try:
            # Load all active services once
            result = await db_session.execute(
                select(Service).where(Service.is_active == True)
            )
            services = result.scalars().all()

            if not services:
                logger.warning("No active services found - cannot calculate scores")
                return {"status": "error", "message": "No active services"}

            # Load all leads
            result = await db_session.execute(select(Lead))
            leads = result.scalars().all()

            logger.info(f"Recalculating scores for {len(leads)} leads across {len(services)} services")

            total_scores = 0
            leads_processed = 0

            for lead in leads:
                try:
                    # Score this lead against all services
                    scores_created = await score_lead(lead, services, db_session)
                    total_scores += len(scores_created)
                    leads_processed += 1

                    if leads_processed % 10 == 0:
                        logger.info(f"Processed {leads_processed}/{len(leads)} leads")

                except Exception as e:
                    logger.error(f"Error scoring lead {lead.id} ({lead.company_name}): {e}")
                    continue

            await db_session.commit()

            logger.info(
                f"✅ Batch recalculation complete: {total_scores} scores for {leads_processed} leads"
            )

            return {
                "status": "success",
                "leads_processed": leads_processed,
                "total_scores": total_scores,
                "services_count": len(services)
            }

        except Exception as e:
            logger.error(f"Error in batch recalculation: {e}")
            await db_session.rollback()
            return {"status": "error", "message": str(e)}


async def _calculate_lead_score_async(lead_id: int) -> Dict:
    """
    Calculate score for a specific lead.

    Called automatically when:
    - New signal is detected for this lead
    - Lead data is enriched
    - Manual recalculation requested

    Args:
        lead_id: ID of lead to recalculate

    Returns:
        Dict with calculation results
    """
    logger.info(f"Recalculating scores for lead {lead_id}")

    async with AsyncSessionLocal() as db_session:
        try:
            # Load lead
            result = await db_session.execute(
                select(Lead).where(Lead.id == lead_id)
            )
            lead = result.scalar_one_or_none()

            if not lead:
                logger.warning(f"Lead {lead_id} not found")
                return {"status": "error", "message": f"Lead {lead_id} not found"}

            # Load all active services
            result = await db_session.execute(
                select(Service).where(Service.is_active == True)
            )
            services = result.scalars().all()

            if not services:
                logger.warning("No active services found")
                return {"status": "error", "message": "No active services"}

            # Score this lead
            scores_created = await score_lead(lead, services, db_session)
            await db_session.commit()

            logger.info(
                f"✅ Recalculated {len(scores_created)} scores for lead {lead_id} ({lead.company_name})"
            )

            return {
                "status": "success",
                "lead_id": lead_id,
                "company_name": lead.company_name,
                "scores_created": len(scores_created)
            }

        except Exception as e:
            logger.error(f"Error calculating score for lead {lead_id}: {e}")
            await db_session.rollback()
            return {"status": "error", "lead_id": lead_id, "message": str(e)}


@celery_app.task(name="app.workers.tasks.scoring.recalculate_all_scores")
def recalculate_all_scores():
    """
    Recalculate lead scores for all leads in the database.

    Scheduled to run daily at 4am via Celery Beat.
    Can also be triggered manually via API.
    """
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_recalculate_all_scores_async())


@celery_app.task(name="app.workers.tasks.scoring.calculate_lead_score")
def calculate_lead_score(lead_id: int):
    """
    Calculate score for a specific lead.

    Triggered automatically when:
    - New signal is detected for this lead
    - Lead data is enriched (multinational, exporter, audit flags)
    - Logo detection finds CAD software on website

    Args:
        lead_id: ID of lead to recalculate
    """
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_calculate_lead_score_async(lead_id))

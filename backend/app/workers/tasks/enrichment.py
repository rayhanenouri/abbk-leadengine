"""
Celery tasks for lead enrichment.

Tasks to detect:
- Multinational companies
- Exporters
- Companies under audit pressure
"""
from celery import shared_task
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
import asyncio
import logging

from app.core.config import settings
from app.models.models import Lead, LeadSignal
from app.scrapers.utils.detection import LeadDetector
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="enrichment.detect_all_flags")
def detect_all_flags_task():
    """
    Celery task wrapper for async enrichment.

    Scans all leads and updates is_multinational, is_exporter, under_audit flags.
    """
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(detect_all_flags())
    return result


async def detect_all_flags():
    """
    Scan all leads and update enrichment flags.

    Returns: dict with counts of detected flags
    """
    logger.info("Starting lead enrichment detection...")

    engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        try:
            # Get all leads
            result = await session.execute(select(Lead))
            leads = result.scalars().all()

            logger.info(f"Enriching {len(leads)} leads...")

            stats = {
                'total': len(leads),
                'multinational': 0,
                'exporter': 0,
                'under_audit': 0,
                'updated': 0,
            }

            for lead in leads:
                # Get website text from scraped_data if available
                website_text = ""
                if lead.scraped_data and isinstance(lead.scraped_data, dict):
                    website_text = str(lead.scraped_data.get('about', ''))
                    website_text += str(lead.scraped_data.get('description', ''))

                # Run detection
                enrichment = LeadDetector.enrich_lead(
                    company_name=lead.company_name,
                    scraped_data=lead.scraped_data or {},
                    sector=lead.sector or "",
                    website_text=website_text
                )

                # Track what changed
                changed = False

                # Update multinational flag
                if enrichment['is_multinational'] and not lead.is_multinational:
                    lead.is_multinational = True
                    stats['multinational'] += 1
                    changed = True

                    # Create signal
                    signal = LeadSignal(
                        lead_id=lead.id,
                        signal_type='multinational_signal',
                        title='Multinational company detected',
                        detail=enrichment['multinational_reason'],
                        source_url=lead.website,
                    )
                    session.add(signal)
                    logger.info(f"✅ Multinational: {lead.company_name}")

                # Update exporter flag
                if enrichment['is_exporter'] and not lead.is_exporter:
                    lead.is_exporter = True
                    stats['exporter'] += 1
                    changed = True

                    # Create signal
                    signal = LeadSignal(
                        lead_id=lead.id,
                        signal_type='export_signal',
                        title='International exporter detected',
                        detail=enrichment['exporter_reason'],
                        source_url=lead.website,
                    )
                    session.add(signal)
                    logger.info(f"✅ Exporter: {lead.company_name}")

                # Update audit flag
                if enrichment['under_audit'] and not lead.under_audit:
                    lead.under_audit = True
                    stats['under_audit'] += 1
                    changed = True

                    # Create signal
                    signal = LeadSignal(
                        lead_id=lead.id,
                        signal_type='audit_signal',
                        title='ISO/Audit certification detected',
                        detail=enrichment['audit_reason'],
                        source_url=lead.website,
                    )
                    session.add(signal)
                    logger.info(f"✅ Under Audit: {lead.company_name}")

                if changed:
                    stats['updated'] += 1

                    # Trigger score recalculation for this lead
                    # Import inside loop to avoid circular imports
                    from app.workers.tasks.scoring import calculate_lead_score
                    try:
                        calculate_lead_score.delay(lead.id)
                        logger.info(f"🔄 Triggered score recalculation for {lead.company_name}")
                    except Exception as e:
                        logger.warning(f"Failed to trigger score recalculation: {e}")

            # Commit all changes
            await session.commit()

            logger.info(
                f"Enrichment complete: {stats['multinational']} multinational, "
                f"{stats['exporter']} exporter, {stats['under_audit']} under audit, "
                f"{stats['updated']} total updated"
            )

            return stats

        except Exception as e:
            await session.rollback()
            logger.error(f"Error during enrichment: {e}")
            raise

        finally:
            await engine.dispose()


@celery_app.task(name="enrichment.detect_single_lead")
def detect_single_lead_task(lead_id: int):
    """
    Celery task to enrich a single lead.

    Args:
        lead_id: ID of lead to enrich
    """
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(detect_single_lead(lead_id))
    return result


async def detect_single_lead(lead_id: int):
    """
    Detect flags for a single lead.

    Returns: dict with detected flags
    """
    engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        try:
            # Get lead
            result = await session.execute(select(Lead).where(Lead.id == lead_id))
            lead = result.scalar_one_or_none()

            if not lead:
                return {'error': 'Lead not found'}

            # Get website text
            website_text = ""
            if lead.scraped_data and isinstance(lead.scraped_data, dict):
                website_text = str(lead.scraped_data.get('about', ''))
                website_text += str(lead.scraped_data.get('description', ''))

            # Run detection
            enrichment = LeadDetector.enrich_lead(
                company_name=lead.company_name,
                scraped_data=lead.scraped_data or {},
                sector=lead.sector or "",
                website_text=website_text
            )

            # Update flags
            lead.is_multinational = enrichment['is_multinational']
            lead.is_exporter = enrichment['is_exporter']
            lead.under_audit = enrichment['under_audit']

            await session.commit()

            logger.info(f"Enriched lead {lead.company_name}: {enrichment}")

            # Trigger score recalculation
            from app.workers.tasks.scoring import calculate_lead_score
            try:
                calculate_lead_score.delay(lead_id)
                logger.info(f"🔄 Triggered score recalculation for lead {lead_id}")
            except Exception as e:
                logger.warning(f"Failed to trigger score recalculation: {e}")

            return enrichment

        except Exception as e:
            await session.rollback()
            logger.error(f"Error enriching lead {lead_id}: {e}")
            raise

        finally:
            await engine.dispose()

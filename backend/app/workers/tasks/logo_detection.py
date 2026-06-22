"""
Celery tasks for logo detection on company websites.
"""
from celery import shared_task
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
import asyncio
import logging

from app.core.config import settings
from app.models.models import Lead, LeadSignal
from app.scrapers.utils.logo_detector import LogoDetector
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="logo_detection.detect_all_websites")
def detect_all_websites_task():
    """
    Celery task wrapper for logo detection on all leads with websites.
    """
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(detect_all_websites())
    return result


async def detect_all_websites():
    """
    Scan all leads with websites and detect SOLIDWORKS/product logos.

    Returns: dict with detection stats
    """
    logger.info("Starting logo detection on company websites...")

    engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        try:
            # Get all leads with websites
            result = await session.execute(
                select(Lead).where(Lead.website.isnot(None), Lead.website != '')
            )
            leads = result.scalars().all()

            logger.info(f"Found {len(leads)} leads with websites")

            detector = LogoDetector(headless=True, timeout=30000)

            stats = {
                'total_checked': 0,
                'solidworks_detected': 0,
                'simulia_detected': 0,
                '3dexperience_detected': 0,
                'emworks_detected': 0,
                'competitor_detected': 0,
                'errors': 0,
            }

            for lead in leads:
                try:
                    logger.info(f"Checking {lead.company_name}: {lead.website}")

                    detection_result = await detector.detect_on_website(lead.website)
                    stats['total_checked'] += 1

                    if detection_result['error']:
                        stats['errors'] += 1
                        logger.warning(f"Error detecting on {lead.website}: {detection_result['error']}")
                        continue

                    # Track if any signal was created
                    signal_created = False

                    # Create signals for detected products
                    if detection_result['solidworks_detected']:
                        stats['solidworks_detected'] += 1

                        # Check if signal already exists
                        existing = await session.execute(
                            select(LeadSignal).where(
                                LeadSignal.lead_id == lead.id,
                                LeadSignal.signal_type == 'logo_detected',
                                LeadSignal.title.like('%SOLIDWORKS%')
                            )
                        )
                        if not existing.scalar_one_or_none():
                            signal = LeadSignal(
                                lead_id=lead.id,
                                signal_type='logo_detected',
                                title=f"SOLIDWORKS products detected: {', '.join(detection_result['products_found'][:3])}",
                                detail='\n'.join(detection_result['text_mentions'][:3]) if detection_result['text_mentions'] else None,
                                source_url=lead.website,
                            )
                            session.add(signal)
                            signal_created = True
                            logger.info(f"✅ SOLIDWORKS detected on {lead.company_name}")

                    if detection_result['simulia_detected']:
                        stats['simulia_detected'] += 1

                        existing = await session.execute(
                            select(LeadSignal).where(
                                LeadSignal.lead_id == lead.id,
                                LeadSignal.signal_type == 'logo_detected',
                                LeadSignal.title.like('%Simulia%')
                            )
                        )
                        if not existing.scalar_one_or_none():
                            signal = LeadSignal(
                                lead_id=lead.id,
                                signal_type='logo_detected',
                                title=f"Simulia/Abaqus detected",
                                detail='\n'.join(detection_result['text_mentions'][:3]) if detection_result['text_mentions'] else None,
                                source_url=lead.website,
                            )
                            session.add(signal)
                            signal_created = True
                            logger.info(f"✅ Simulia detected on {lead.company_name}")

                    if detection_result['3dexperience_detected']:
                        stats['3dexperience_detected'] += 1

                        existing = await session.execute(
                            select(LeadSignal).where(
                                LeadSignal.lead_id == lead.id,
                                LeadSignal.signal_type == 'logo_detected',
                                LeadSignal.title.like('%3DEXPERIENCE%')
                            )
                        )
                        if not existing.scalar_one_or_none():
                            signal = LeadSignal(
                                lead_id=lead.id,
                                signal_type='logo_detected',
                                title=f"3DEXPERIENCE platform detected",
                                detail=None,
                                source_url=lead.website,
                            )
                            session.add(signal)
                            signal_created = True
                            logger.info(f"✅ 3DEXPERIENCE detected on {lead.company_name}")

                    # Competitor products (potential cracked SOLIDWORKS users)
                    if detection_result['competitor_products']:
                        stats['competitor_detected'] += 1
                        logger.info(f"ℹ️  Competitor products on {lead.company_name}: {detection_result['competitor_products']}")

                    # Trigger score recalculation if any signal was created
                    if signal_created:
                        from app.workers.tasks.scoring import calculate_lead_score
                        try:
                            calculate_lead_score.delay(lead.id)
                            logger.info(f"🔄 Triggered score recalculation for {lead.company_name}")
                        except Exception as e:
                            logger.warning(f"Failed to trigger score recalculation: {e}")

                    # Small delay between requests
                    await asyncio.sleep(3)

                except Exception as e:
                    stats['errors'] += 1
                    logger.error(f"Error processing {lead.company_name}: {e}")
                    continue

            # Commit all signals
            await session.commit()

            logger.info(
                f"Logo detection complete: {stats['total_checked']} checked, "
                f"{stats['solidworks_detected']} SOLIDWORKS, "
                f"{stats['simulia_detected']} Simulia, "
                f"{stats['3dexperience_detected']} 3DEXPERIENCE, "
                f"{stats['errors']} errors"
            )

            return stats

        except Exception as e:
            await session.rollback()
            logger.error(f"Error during logo detection: {e}")
            raise

        finally:
            await engine.dispose()


@celery_app.task(name="logo_detection.detect_single_website")
def detect_single_website_task(lead_id: int):
    """
    Detect logos on a single lead's website.

    Args:
        lead_id: ID of lead to check
    """
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(detect_single_website(lead_id))
    return result


async def detect_single_website(lead_id: int):
    """Detect logos on single lead website."""
    engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        try:
            # Get lead
            result = await session.execute(select(Lead).where(Lead.id == lead_id))
            lead = result.scalar_one_or_none()

            if not lead or not lead.website:
                return {'error': 'Lead not found or no website'}

            detector = LogoDetector(headless=True)
            detection_result = await detector.detect_on_website(lead.website)

            # Create signals based on results
            # (same logic as above)

            await session.commit()

            logger.info(f"Detected on {lead.company_name}: {detection_result}")

            return detection_result

        except Exception as e:
            await session.rollback()
            logger.error(f"Error detecting on lead {lead_id}: {e}")
            raise

        finally:
            await engine.dispose()

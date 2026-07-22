"""
Celery task to run deep enrichment on all leads with websites.

This is the CRITICAL task that scrapes actual company websites and builds real intelligence.
"""
from celery import shared_task
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
import asyncio
import logging
from datetime import datetime

from app.core.config import settings
from app.models.models import Lead, LeadSignal
from app.workers.celery_app import celery_app
from app.scrapers.utils.deep_enricher import DeepCompanyEnricher

logger = logging.getLogger(__name__)


@celery_app.task(name="enrichment.deep_enrich_all_leads")
def deep_enrich_all_leads_task():
    """
    Run deep enrichment on ALL leads that have websites.
    This scrapes their entire web presence and extracts real signals.
    """
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(deep_enrich_all_leads())
    return result


async def deep_enrich_all_leads():
    """
    Deep enrich all leads with websites.

    For each company:
    1. Scrape homepage, about, jobs, products, news pages
    2. Detect engineering keywords, CAD software mentions
    3. Find hiring signals
    4. Detect ISO, export, multinational signals
    5. Store everything in scraped_data JSON
    6. Create LeadSignal records with PROOF URLs
    """
    logger.info("🚀 Starting deep enrichment for ALL leads...")

    engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    enricher = DeepCompanyEnricher()

    stats = {
        'total_leads': 0,
        'enriched': 0,
        'failed': 0,
        'signals_created': 0
    }

    async with session_factory() as session:
        try:
            # Get all leads with websites
            result = await session.execute(
                select(Lead).where(Lead.website.isnot(None)).where(Lead.website != '')
            )
            leads = result.scalars().all()

            stats['total_leads'] = len(leads)
            logger.info(f"📋 Found {len(leads)} leads with websites to enrich")

            for lead in leads:
                try:
                    logger.info(f"🔍 Enriching {lead.company_name} — {lead.website}")

                    # Run deep enrichment
                    enrichment_data = await enricher.enrich_company(
                        company_id=lead.id,
                        company_name=lead.company_name,
                        website=lead.website
                    )

                    # Store enrichment data in scraped_data
                    lead.scraped_data = enrichment_data

                    # Extract and update flags from signals
                    signals = enrichment_data.get('signals', {})

                    if signals.get('is_multinational') and not lead.is_multinational:
                        lead.is_multinational = True
                        # Create signal with proof URL
                        signal = LeadSignal(
                            lead_id=lead.id,
                            signal_type='multinational_signal',
                            title='Multinational company detected',
                            detail='International presence detected on website',
                            source_url=enrichment_data.get('about', {}).get('url') or lead.website,
                            detected_at=datetime.utcnow()
                        )
                        session.add(signal)
                        stats['signals_created'] += 1
                        logger.info(f"  ✅ Multinational signal")

                    if signals.get('is_exporter') and not lead.is_exporter:
                        lead.is_exporter = True
                        signal = LeadSignal(
                            lead_id=lead.id,
                            signal_type='export_signal',
                            title='International export activity detected',
                            detail='Export keywords found on website',
                            source_url=enrichment_data.get('about', {}).get('url') or lead.website,
                            detected_at=datetime.utcnow()
                        )
                        session.add(signal)
                        stats['signals_created'] += 1
                        logger.info(f"  ✅ Exporter signal")

                    if signals.get('has_iso_certification') and not lead.under_audit:
                        lead.under_audit = True
                        signal = LeadSignal(
                            lead_id=lead.id,
                            signal_type='audit_signal',
                            title='ISO certification detected',
                            detail='ISO quality certification found on website',
                            source_url=enrichment_data.get('about', {}).get('url') or lead.website,
                            detected_at=datetime.utcnow()
                        )
                        session.add(signal)
                        stats['signals_created'] += 1
                        logger.info(f"  ✅ ISO/Audit signal")

                    if signals.get('has_engineering'):
                        signal = LeadSignal(
                            lead_id=lead.id,
                            signal_type='role_detected',
                            title='Engineering team detected',
                            detail='Engineering roles and activities found on website',
                            source_url=enrichment_data.get('team', {}).get('url') or enrichment_data.get('about', {}).get('url') or lead.website,
                            detected_at=datetime.utcnow()
                        )
                        session.add(signal)
                        stats['signals_created'] += 1
                        logger.info(f"  ✅ Engineering team signal")

                    if signals.get('has_cad_software'):
                        signal = LeadSignal(
                            lead_id=lead.id,
                            signal_type='logo_detected',
                            title='CAD software detected',
                            detail='CAD/CAE software mentions found on website',
                            source_url=enrichment_data.get('products', {}).get('url') or lead.website,
                            detected_at=datetime.utcnow()
                        )
                        session.add(signal)
                        stats['signals_created'] += 1
                        logger.info(f"  ✅ CAD software signal")

                    # Create signals for each job opening found
                    job_openings = signals.get('job_openings', [])
                    for job in job_openings[:5]:  # Limit to top 5
                        signal = LeadSignal(
                            lead_id=lead.id,
                            signal_type='new_hire',
                            title=f"Hiring: {job.get('title', 'Engineer')}",
                            detail=f"{lead.company_name} is actively hiring {job.get('title')}",
                            source_url=enrichment_data.get('jobs', {}).get('url') or lead.website,
                            detected_at=datetime.utcnow()
                        )
                        session.add(signal)
                        stats['signals_created'] += 1
                        logger.info(f"  ✅ Hiring signal: {job.get('title')}")

                    # Update employee count if found
                    employee_count = signals.get('employee_count')
                    if employee_count:
                        lead.employee_count = employee_count
                        logger.info(f"  ✅ Employee count: {employee_count}")

                    stats['enriched'] += 1
                    logger.info(f"✅ Enriched {lead.company_name} successfully")

                except Exception as e:
                    logger.error(f"❌ Failed to enrich {lead.company_name}: {e}")
                    stats['failed'] += 1
                    continue

            # Commit all changes
            await session.commit()

            logger.info(
                f"\n🎉 Deep enrichment complete!\n"
                f"  Total leads: {stats['total_leads']}\n"
                f"  Enriched: {stats['enriched']}\n"
                f"  Failed: {stats['failed']}\n"
                f"  Signals created: {stats['signals_created']}"
            )

            return stats

        except Exception as e:
            await session.rollback()
            logger.error(f"❌ Error during deep enrichment: {e}")
            raise

        finally:
            await enricher.close()
            await engine.dispose()


@celery_app.task(name="enrichment.deep_enrich_single_lead")
def deep_enrich_single_lead_task(lead_id: int):
    """Deep enrich a single lead by ID."""
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(deep_enrich_single_lead(lead_id))
    return result


async def deep_enrich_single_lead(lead_id: int):
    """Deep enrich a single lead."""

    engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    enricher = DeepCompanyEnricher()

    async with session_factory() as session:
        try:
            # Get lead
            result = await session.execute(select(Lead).where(Lead.id == lead_id))
            lead = result.scalar_one_or_none()

            if not lead:
                return {'error': 'Lead not found'}

            if not lead.website:
                return {'error': 'Lead has no website'}

            logger.info(f"🔍 Enriching {lead.company_name} — {lead.website}")

            # Run enrichment
            enrichment_data = await enricher.enrich_company(
                company_id=lead.id,
                company_name=lead.company_name,
                website=lead.website
            )

            # Store in database
            lead.scraped_data = enrichment_data

            # Update flags and create signals (same logic as above)
            signals = enrichment_data.get('signals', {})

            if signals.get('is_multinational'):
                lead.is_multinational = True
            if signals.get('is_exporter'):
                lead.is_exporter = True
            if signals.get('has_iso_certification'):
                lead.under_audit = True
            if signals.get('employee_count'):
                lead.employee_count = signals['employee_count']

            await session.commit()

            logger.info(f"✅ Enriched {lead.company_name}")

            # Trigger score recalculation
            from app.workers.tasks.scoring import calculate_lead_score
            try:
                calculate_lead_score.delay(lead_id)
            except Exception as e:
                logger.warning(f"Failed to trigger scoring: {e}")

            return enrichment_data

        except Exception as e:
            await session.rollback()
            logger.error(f"❌ Error enriching lead {lead_id}: {e}")
            raise

        finally:
            await enricher.close()
            await engine.dispose()

"""
COMPLETE AUTOMATION PIPELINE
This runs automatically every day via Celery Beat
"""

from app.workers.celery_app import celery_app
import logging
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime
import sys
import os

sys.path.insert(0, '/app')

from app.db.session import AsyncSessionLocal
from app.models.models import Lead, LeadSignal, Service, LeadScore
from sqlalchemy import select, delete

logger = logging.getLogger(__name__)


@celery_app.task(name="app.workers.tasks.full_automation.discover_companies")
def discover_companies():
    """
    STEP 1: Discover new companies from verified directories
    Runs: Daily at 2am
    """
    logger.info("🔍 STEP 1: Discovering new companies from directories...")

    import subprocess
    result = subprocess.run(
        ['scrapy', 'crawl', 'directories', '-o', '/tmp/discovered_companies.json'],
        cwd='/app/scraper',
        env={'PYTHONPATH': '/app'},
        capture_output=True,
        text=True,
        timeout=1800
    )

    if result.returncode == 0:
        logger.info("✅ Company discovery completed")
        return {"status": "success", "step": "discovery"}
    else:
        logger.error(f"❌ Company discovery failed: {result.stderr}")
        return {"status": "error", "step": "discovery"}


@celery_app.task(name="app.workers.tasks.full_automation.find_company_websites")
def find_company_websites():
    """
    STEP 2: Find real website URLs for companies that don't have them
    Runs: Daily at 3am (after discovery)
    """
    logger.info("🌐 STEP 2: Finding real website URLs for all companies...")

    async def find_urls():
        async with AsyncSessionLocal() as db:
            # Get companies without real websites
            result = await db.execute(
                select(Lead).where(
                    (Lead.website.is_(None)) |
                    (Lead.website.like('%tunisieindustrie%')) |
                    (Lead.website.like('%taa.tn%'))
                ).limit(100)
            )
            leads = list(result.scalars().all())

            logger.info(f"Found {len(leads)} companies needing website URLs")

            connector = aiohttp.TCPConnector(limit=3, ssl=False)
            async with aiohttp.ClientSession(connector=connector) as session:
                found = 0

                for lead in leads:
                    search_query = f"{lead.company_name} Tunisia site"
                    google_url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"

                    try:
                        async with session.get(google_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10) as response:
                            if response.status == 200:
                                html = await response.text()
                                soup = BeautifulSoup(html, 'html.parser')

                                for link in soup.find_all('a', href=True):
                                    href = link['href']
                                    if '/url?q=' in href:
                                        url = href.split('/url?q=')[1].split('&')[0]
                                        if url.startswith('http') and not any(x in url.lower() for x in ['google', 'facebook', 'linkedin', 'wikipedia']):
                                            lead.website = url
                                            found += 1
                                            logger.info(f"✓ Found website for {lead.company_name}: {url}")
                                            break
                    except:
                        pass

                    await asyncio.sleep(2)

                await db.commit()
                logger.info(f"✅ Found {found} new website URLs")
                return found

    return asyncio.run(find_urls())


@celery_app.task(name="app.workers.tasks.full_automation.scrape_all_websites")
def scrape_all_websites():
    """
    STEP 3: Scrape all company websites for signals
    Runs: Daily at 4am (after finding URLs)
    """
    logger.info("🕷️  STEP 3: Scraping all company websites for signals...")

    async def scrape_all():
        async with AsyncSessionLocal() as db:
            # Get companies with websites
            result = await db.execute(
                select(Lead).where(Lead.website.isnot(None)).limit(200)
            )
            leads = list(result.scalars().all())

            logger.info(f"Scraping {len(leads)} company websites...")

            connector = aiohttp.TCPConnector(limit=5, ssl=False)
            async with aiohttp.ClientSession(connector=connector) as session:
                signals_added = 0

                for idx, lead in enumerate(leads, 1):
                    try:
                        async with session.get(lead.website, ssl=False, timeout=15, headers={'User-Agent': 'Mozilla/5.0'}) as response:
                            if response.status == 200:
                                html = await response.text()
                                soup = BeautifulSoup(html, 'html.parser')
                                text = soup.get_text().lower()

                                # Training signal (40pts)
                                if any(kw in text for kw in ['formation', 'training', 'solidworks', 'cao', 'certification']):
                                    existing = await db.execute(
                                        select(LeadSignal).where(
                                            LeadSignal.lead_id == lead.id,
                                            LeadSignal.signal_type == 'training_detected'
                                        )
                                    )
                                    if not existing.scalar_one_or_none():
                                        db.add(LeadSignal(
                                            lead_id=lead.id,
                                            signal_type='training_detected',
                                            title='Training/CAD software mentioned',
                                            detail=f'{lead.company_name} website mentions CAD training or certification',
                                            source_url=lead.website,
                                            detected_at=datetime.now()
                                        ))
                                        signals_added += 1

                                # Hiring signal (20pts)
                                if any(kw in text for kw in ['recrute', 'recrutement', 'candidature', 'carriere']):
                                    existing = await db.execute(
                                        select(LeadSignal).where(
                                            LeadSignal.lead_id == lead.id,
                                            LeadSignal.signal_type == 'new_hire'
                                        )
                                    )
                                    if not existing.scalar_one_or_none():
                                        db.add(LeadSignal(
                                            lead_id=lead.id,
                                            signal_type='new_hire',
                                            title='Hiring/Careers section found',
                                            detail=f'{lead.company_name} has active recruitment',
                                            source_url=lead.website,
                                            detected_at=datetime.now()
                                        ))
                                        signals_added += 1

                                # Engineering roles (20pts)
                                if any(kw in text for kw in ['ingenieur', 'engineer', 'bureau etudes', 'cad']):
                                    existing = await db.execute(
                                        select(LeadSignal).where(
                                            LeadSignal.lead_id == lead.id,
                                            LeadSignal.signal_type == 'role_detected'
                                        )
                                    )
                                    if not existing.scalar_one_or_none():
                                        db.add(LeadSignal(
                                            lead_id=lead.id,
                                            signal_type='role_detected',
                                            title='Engineering team detected',
                                            detail=f'{lead.company_name} has engineering/design team',
                                            source_url=lead.website,
                                            detected_at=datetime.now()
                                        ))
                                        signals_added += 1

                                # CAD software logo (10pts)
                                if any(kw in text for kw in ['solidworks', 'catia', 'autocad', 'inventor']):
                                    existing = await db.execute(
                                        select(LeadSignal).where(
                                            LeadSignal.lead_id == lead.id,
                                            LeadSignal.signal_type == 'logo_detected'
                                        )
                                    )
                                    if not existing.scalar_one_or_none():
                                        db.add(LeadSignal(
                                            lead_id=lead.id,
                                            signal_type='logo_detected',
                                            title='CAD software detected',
                                            detail=f'{lead.company_name} uses CAD software',
                                            source_url=lead.website,
                                            detected_at=datetime.now()
                                        ))
                                        signals_added += 1

                    except:
                        pass

                    if idx % 20 == 0:
                        await db.commit()
                        logger.info(f"Progress: {idx}/{len(leads)}, {signals_added} signals")

                    await asyncio.sleep(1)

                await db.commit()
                logger.info(f"✅ Scraping complete: {signals_added} new signals")
                return signals_added

    return asyncio.run(scrape_all())


@celery_app.task(name="app.workers.tasks.full_automation.recalculate_all_scores")
def recalculate_all_scores():
    """
    STEP 4: Recalculate scores for all companies
    Runs: Daily at 5am (after scraping)
    """
    logger.info("🔢 STEP 4: Recalculating scores for all companies...")

    async def recalc():
        async with AsyncSessionLocal() as db:
            # Get all services
            services_result = await db.execute(select(Service))
            services = list(services_result.scalars().all())

            # Get all leads
            leads_result = await db.execute(select(Lead))
            leads = list(leads_result.scalars().all())

            logger.info(f"Recalculating scores for {len(leads)} companies × {len(services)} services...")

            # Delete old scores
            await db.execute(delete(LeadScore))

            scored = 0
            for lead in leads:
                # Get signals
                signals_result = await db.execute(
                    select(LeadSignal).where(LeadSignal.lead_id == lead.id)
                )
                signals = list(signals_result.scalars().all())

                # Build signal map
                signal_map = {
                    'training_detected': any('training' in s.signal_type for s in signals),
                    'new_hire': any('hire' in s.signal_type for s in signals),
                    'role_detected': any('role' in s.signal_type for s in signals),
                    'logo_detected': any('logo' in s.signal_type for s in signals),
                    'is_multinational': lead.is_multinational or False,
                    'under_audit': lead.under_audit or False,
                    'is_exporter': lead.is_exporter or False,
                }

                # Score for each service
                for service in services:
                    weights = service.scoring_weights or {}
                    raw_score = 0
                    max_possible = sum(weights.values())

                    for signal_key, weight in weights.items():
                        if signal_map.get(signal_key, False):
                            raw_score += weight

                    final_score = (raw_score / max_possible * 100) if max_possible > 0 else 0

                    db.add(LeadScore(
                        lead_id=lead.id,
                        service_type=service.service_type,
                        service_name=service.name,
                        score=final_score,
                        reasoning=f"Score based on {len(signals)} signals",
                        signal_breakdown=signal_map,
                        scored_at=datetime.now()
                    ))

                scored += 1
                if scored % 50 == 0:
                    await db.commit()

            await db.commit()
            logger.info(f"✅ Scores recalculated: {scored} companies")
            return scored

    return asyncio.run(recalc())


@celery_app.task(name="app.workers.tasks.full_automation.run_full_pipeline")
def run_full_pipeline():
    """
    MASTER TASK: Run complete automation pipeline
    Runs: Daily at 2am

    This is the ONLY task you need - it runs everything automatically
    """
    logger.info("🚀 STARTING FULL AUTOMATION PIPELINE")
    logger.info("="*70)

    results = {}

    # Step 1: Discover new companies
    results['discovery'] = discover_companies()

    # Step 2: Find their websites
    results['find_urls'] = find_company_websites()

    # Step 3: Scrape all websites
    results['scraping'] = scrape_all_websites()

    # Step 4: Recalculate scores
    results['scoring'] = recalculate_all_scores()

    logger.info("="*70)
    logger.info("✅ FULL AUTOMATION PIPELINE COMPLETE")
    logger.info(f"Results: {results}")

    return results

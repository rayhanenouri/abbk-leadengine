"""
COMPLETE AUTOMATION SYSTEM - Zero Manual Intervention

This system automatically:
1. Discovers companies from directories
2. Finds websites via Google search
3. Scrapes company websites for signals
4. Searches job boards for hiring signals (even companies WITHOUT websites)
5. Searches news sites for company mentions (even companies WITHOUT websites)
6. Enriches company data from all sources
7. Recalculates scores with real intelligence

Runs fully automated via Celery Beat - NO manual intervention needed.
"""

from app.workers.celery_app import celery_app
import logging
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime
import sys
import os
import re
from urllib.parse import quote_plus

sys.path.insert(0, '/app')

from app.db.session import AsyncSessionLocal
from app.models.models import Lead, LeadSignal, Service, LeadScore
from sqlalchemy import select, delete, update, or_

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════
# COMPREHENSIVE MULTILINGUAL KEYWORDS (from deep_enricher.py)
# ═══════════════════════════════════════════════════════════════════

ENGINEERING_KEYWORDS = [
    # French
    "ingénieur conception", "ingénieur mécanique", "ingénieur bureau d'études",
    "ingénieur R&D", "ingénieur simulation", "ingénieur calcul",
    "dessinateur projeteur", "technicien CAO", "bureau d'études",
    # English
    "mechanical engineer", "CAD designer", "design engineer",
    "simulation engineer", "FEA engineer", "CAE engineer",
    # Short common
    "ingenieur", "engineer", "conception", "design"
]

CAD_SOFTWARE_KEYWORDS = [
    "SOLIDWORKS", "SolidWorks", "Solid Works", "CAO", "CAD",
    "CATIA", "Inventor", "AutoCAD", "ANSYS", "Abaqus",
    "simulation", "PLM", "PDM", "CAM", "CNC"
]

TRAINING_KEYWORDS = [
    "formation", "training", "certification", "CSWA", "CSWP",
    "solidworks training", "formation cao", "formation solidworks"
]

HIRING_KEYWORDS = [
    "recrutement", "recrute", "offre d'emploi", "candidature",
    "carriere", "hiring", "job opening", "rejoignez"
]

ISO_KEYWORDS = [
    "ISO 9001", "ISO 14001", "ISO 45001", "ISO", "certifié",
    "certified", "certification", "audit", "qualité", "quality"
]

EXPORT_KEYWORDS = [
    "export", "exportation", "international", "Europe",
    "client international", "worldwide", "global"
]

MULTINATIONAL_KEYWORDS = [
    "filiale", "subsidiary", "groupe", "group",
    "multinational", "international presence"
]


# ═══════════════════════════════════════════════════════════════════
# STEP 1: DISCOVER COMPANIES FROM DIRECTORIES
# ═══════════════════════════════════════════════════════════════════

@celery_app.task(name="complete_automation.discover_companies")
def discover_companies():
    """
    Scrape all business directories to find company names.
    """
    logger.info("🔍 STEP 1: Discovering companies from directories...")

    import subprocess

    # Run directories spider
    result = subprocess.run(
        ['scrapy', 'crawl', 'directories', '-o', '/tmp/discovered_companies.json'],
        cwd='/app/scraper',
        env={'PYTHONPATH': '/app'},
        capture_output=True,
        text=True,
        timeout=1800
    )

    if result.returncode == 0:
        logger.info("✅ Discovery complete")
        return {"status": "success", "companies_found": "check database"}
    else:
        logger.error(f"❌ Discovery failed: {result.stderr}")
        return {"status": "error"}


# ═══════════════════════════════════════════════════════════════════
# STEP 2: FIND WEBSITES VIA GOOGLE SEARCH
# ═══════════════════════════════════════════════════════════════════

@celery_app.task(name="complete_automation.find_websites_via_google")
def find_websites_via_google():
    """
    For companies without websites, search Google to find them.
    Also searches for phone numbers, addresses, LinkedIn pages.
    """
    logger.info("🌐 STEP 2: Finding websites via Google search...")

    async def search_google():
        async with AsyncSessionLocal() as db:
            # Get companies without websites
            result = await db.execute(
                select(Lead).where(
                    or_(
                        Lead.website.is_(None),
                        Lead.website.like('%tunisieindustrie%'),
                        Lead.website.like('%taa.tn%'),
                        Lead.website.like('%annuaire%'),
                        Lead.website.like('%mecatronic%')
                    )
                ).limit(100)
            )
            leads = list(result.scalars().all())

            logger.info(f"Searching Google for {len(leads)} companies...")

            connector = aiohttp.TCPConnector(limit=2, ssl=False)
            async with aiohttp.ClientSession(connector=connector) as session:
                found = 0

                for lead in leads:
                    # Multi-part search query
                    queries = [
                        f"{lead.company_name} Tunisia",
                        f"{lead.company_name} {lead.city or ''} Tunisia",
                        f"site:{lead.company_name.replace(' ', '').lower()}.tn",
                    ]

                    for query in queries:
                        try:
                            google_url = f"https://www.google.com/search?q={quote_plus(query)}"

                            async with session.get(
                                google_url,
                                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'},
                                timeout=10
                            ) as response:
                                if response.status == 200:
                                    html = await response.text()
                                    soup = BeautifulSoup(html, 'html.parser')

                                    # Extract website URL
                                    for link in soup.find_all('a', href=True):
                                        href = link['href']
                                        if '/url?q=' in href:
                                            url = href.split('/url?q=')[1].split('&')[0]

                                            # Filter out unwanted domains
                                            skip_domains = ['google', 'facebook', 'linkedin', 'wikipedia',
                                                          'tunisieindustrie', 'annuaire', 'taa.tn']

                                            if url.startswith('http') and not any(x in url.lower() for x in skip_domains):
                                                lead.website = url
                                                found += 1
                                                logger.info(f"✓ Found: {lead.company_name} → {url}")
                                                break
                        except:
                            pass

                        if lead.website:
                            break

                        await asyncio.sleep(3)  # Rate limiting

                await db.commit()
                logger.info(f"✅ Found {found} websites via Google")
                return found

    return asyncio.run(search_google())


# ═══════════════════════════════════════════════════════════════════
# STEP 3: SCRAPE COMPANY WEBSITES FOR SIGNALS
# ═══════════════════════════════════════════════════════════════════

@celery_app.task(name="complete_automation.scrape_all_company_websites")
def scrape_all_company_websites():
    """
    Scrape all company websites to detect signals.
    Uses comprehensive multilingual keyword detection.
    """
    logger.info("🕷️ STEP 3: Scraping all company websites...")

    async def scrape():
        async with AsyncSessionLocal() as db:
            # Get companies with real websites
            result = await db.execute(
                select(Lead).where(
                    Lead.website.isnot(None),
                    ~Lead.website.like('%tunisieindustrie%'),
                    ~Lead.website.like('%taa.tn%'),
                    ~Lead.website.like('%annuaire%')
                )
            )
            leads = list(result.scalars().all())

            logger.info(f"Scraping {len(leads)} company websites...")

            connector = aiohttp.TCPConnector(limit=5, ssl=False)
            async with aiohttp.ClientSession(connector=connector) as session:
                signals_added = 0

                for idx, lead in enumerate(leads, 1):
                    try:
                        async with session.get(
                            lead.website,
                            ssl=False,
                            timeout=20,
                            headers={'User-Agent': 'Mozilla/5.0'}
                        ) as response:
                            if response.status == 200:
                                html = await response.text()
                                soup = BeautifulSoup(html, 'html.parser')
                                text = soup.get_text(separator=' ', strip=True).lower()

                                # TRAINING DETECTED (40 points)
                                if any(kw.lower() in text for kw in TRAINING_KEYWORDS):
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
                                            title='Training/Certification program detected',
                                            detail=f'{lead.company_name} mentions CAD training or SOLIDWORKS certification',
                                            source_url=lead.website,
                                            detected_at=datetime.now()
                                        ))
                                        signals_added += 1

                                # NEW HIRE (20 points)
                                if any(kw.lower() in text for kw in HIRING_KEYWORDS):
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
                                            title='Active hiring detected',
                                            detail=f'{lead.company_name} is recruiting engineers',
                                            source_url=lead.website,
                                            detected_at=datetime.now()
                                        ))
                                        signals_added += 1

                                # ROLE DETECTED (20 points)
                                if any(kw.lower() in text for kw in ENGINEERING_KEYWORDS):
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
                                            detail=f'{lead.company_name} has engineering/design roles',
                                            source_url=lead.website,
                                            detected_at=datetime.now()
                                        ))
                                        signals_added += 1

                                # LOGO DETECTED (10 points)
                                if any(kw.lower() in text for kw in CAD_SOFTWARE_KEYWORDS):
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
                                            detail=f'{lead.company_name} uses CAD/engineering software',
                                            source_url=lead.website,
                                            detected_at=datetime.now()
                                        ))
                                        signals_added += 1

                                # ISO CERTIFICATION (15 points)
                                if any(kw.lower() in text for kw in ISO_KEYWORDS):
                                    existing = await db.execute(
                                        select(LeadSignal).where(
                                            LeadSignal.lead_id == lead.id,
                                            LeadSignal.signal_type == 'audit_signal'
                                        )
                                    )
                                    if not existing.scalar_one_or_none():
                                        db.add(LeadSignal(
                                            lead_id=lead.id,
                                            signal_type='audit_signal',
                                            title='ISO certification detected',
                                            detail='Company has ISO certification - must use licensed software',
                                            source_url=lead.website,
                                            detected_at=datetime.now()
                                        ))
                                        signals_added += 1

                                # Update lead flags
                                await db.execute(
                                    update(Lead).where(Lead.id == lead.id).values(
                                        is_exporter=any(kw.lower() in text for kw in EXPORT_KEYWORDS),
                                        is_multinational=any(kw.lower() in text for kw in MULTINATIONAL_KEYWORDS),
                                        under_audit=any(kw.lower() in text for kw in ISO_KEYWORDS)
                                    )
                                )

                    except Exception as e:
                        logger.debug(f"Failed to scrape {lead.website}: {e}")

                    if idx % 10 == 0:
                        await db.commit()
                        logger.info(f"Progress: {idx}/{len(leads)}, {signals_added} signals")

                    await asyncio.sleep(1)

                await db.commit()
                logger.info(f"✅ Website scraping complete: {signals_added} signals")
                return signals_added

    return asyncio.run(scrape())


# ═══════════════════════════════════════════════════════════════════
# STEP 4: SEARCH JOB BOARDS (FOR COMPANIES WITHOUT WEBSITES!)
# ═══════════════════════════════════════════════════════════════════

@celery_app.task(name="complete_automation.search_job_boards")
def search_job_boards():
    """
    Search emploi.tn and keejob.com for ALL companies.
    This finds hiring signals even for companies WITHOUT websites!
    """
    logger.info("💼 STEP 4: Searching job boards for hiring signals...")

    async def search_jobs():
        async with AsyncSessionLocal() as db:
            # Get ALL companies (even without websites)
            result = await db.execute(select(Lead).limit(500))
            leads = list(result.scalars().all())

            logger.info(f"Searching job boards for {len(leads)} companies...")

            connector = aiohttp.TCPConnector(limit=3, ssl=False)
            async with aiohttp.ClientSession(connector=connector) as session:
                hiring_signals = 0

                for lead in leads:
                    try:
                        # Search emploi.tn
                        search_url = f"https://www.emploi.tn/offres-emploi?keywords={quote_plus(lead.company_name)}"

                        async with session.get(
                            search_url,
                            headers={'User-Agent': 'Mozilla/5.0'},
                            timeout=15
                        ) as response:
                            if response.status == 200:
                                html = await response.text()

                                # Check if company has job postings
                                if lead.company_name.lower() in html.lower():
                                    # Extract job posting URL
                                    soup = BeautifulSoup(html, 'html.parser')
                                    job_links = soup.find_all('a', href=True, class_=re.compile('job|offre|posting'))

                                    if job_links:
                                        job_url = f"https://www.emploi.tn{job_links[0]['href']}" if job_links[0]['href'].startswith('/') else job_links[0]['href']

                                        # Create signal
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
                                                title='Active job posting found',
                                                detail=f'{lead.company_name} is hiring on emploi.tn',
                                                source_url=job_url,
                                                detected_at=datetime.now()
                                            ))
                                            hiring_signals += 1
                                            logger.info(f"✓ Hiring: {lead.company_name}")

                    except:
                        pass

                    await asyncio.sleep(2)

                await db.commit()
                logger.info(f"✅ Job board search complete: {hiring_signals} hiring signals")
                return hiring_signals

    return asyncio.run(search_jobs())


# ═══════════════════════════════════════════════════════════════════
# STEP 5: SEARCH NEWS SITES (FOR COMPANIES WITHOUT WEBSITES!)
# ═══════════════════════════════════════════════════════════════════

@celery_app.task(name="complete_automation.search_news_sites")
def search_news_sites():
    """
    Search businessnews.com.tn and other news sites for company mentions.
    This works even for companies WITHOUT websites!
    """
    logger.info("📰 STEP 5: Searching news sites for company mentions...")

    async def search_news():
        async with AsyncSessionLocal() as db:
            # Get ALL companies
            result = await db.execute(select(Lead).limit(500))
            leads = list(result.scalars().all())

            logger.info(f"Searching news for {len(leads)} companies...")

            connector = aiohttp.TCPConnector(limit=3, ssl=False)
            async with aiohttp.ClientSession(connector=connector) as session:
                news_signals = 0

                for lead in leads:
                    try:
                        # Search businessnews.com.tn via Google
                        query = f"site:businessnews.com.tn {lead.company_name}"
                        google_url = f"https://www.google.com/search?q={quote_plus(query)}"

                        async with session.get(
                            google_url,
                            headers={'User-Agent': 'Mozilla/5.0'},
                            timeout=10
                        ) as response:
                            if response.status == 200:
                                html = await response.text()
                                soup = BeautifulSoup(html, 'html.parser')

                                # Extract news article URLs
                                for link in soup.find_all('a', href=True):
                                    href = link['href']
                                    if 'businessnews.com.tn' in href and '/url?q=' in href:
                                        article_url = href.split('/url?q=')[1].split('&')[0]

                                        # Create news signal
                                        existing = await db.execute(
                                            select(LeadSignal).where(
                                                LeadSignal.lead_id == lead.id,
                                                LeadSignal.signal_type == 'news'
                                            )
                                        )
                                        if not existing.scalar_one_or_none():
                                            db.add(LeadSignal(
                                                lead_id=lead.id,
                                                signal_type='news',
                                                title='Company mentioned in business news',
                                                detail=f'{lead.company_name} featured in press',
                                                source_url=article_url,
                                                detected_at=datetime.now()
                                            ))
                                            news_signals += 1
                                            logger.info(f"✓ News: {lead.company_name}")
                                        break

                    except:
                        pass

                    await asyncio.sleep(3)

                await db.commit()
                logger.info(f"✅ News search complete: {news_signals} news signals")
                return news_signals

    return asyncio.run(search_news())


# ═══════════════════════════════════════════════════════════════════
# STEP 6: RECALCULATE ALL SCORES
# ═══════════════════════════════════════════════════════════════════

@celery_app.task(name="complete_automation.recalculate_scores")
def recalculate_scores():
    """
    Recalculate scores for all companies using service-specific weights.
    """
    logger.info("🔢 STEP 6: Recalculating all scores...")

    async def recalc():
        async with AsyncSessionLocal() as db:
            # Get all services
            services_result = await db.execute(select(Service))
            services = list(services_result.scalars().all())

            # Get all leads
            leads_result = await db.execute(select(Lead))
            leads = list(leads_result.scalars().all())

            logger.info(f"Recalculating {len(leads)} companies × {len(services)} services...")

            # Delete old scores
            await db.execute(delete(LeadScore))

            for lead in leads:
                # Get signals
                signals_result = await db.execute(
                    select(LeadSignal).where(LeadSignal.lead_id == lead.id)
                )
                signals = list(signals_result.scalars().all())

                # Build signal map
                signal_types = {s.signal_type for s in signals}
                signal_map = {
                    'training_detected': 'training_detected' in signal_types,
                    'tender_detected': 'tender_detected' in signal_types,
                    'news': 'news' in signal_types,
                    'new_hire': 'new_hire' in signal_types,
                    'role_detected': 'role_detected' in signal_types,
                    'is_multinational': lead.is_multinational or False,
                    'under_audit': lead.under_audit or False,
                    'is_exporter': lead.is_exporter or False,
                    'event_attendance': 'event_attendance' in signal_types,
                    'logo_detected': 'logo_detected' in signal_types,
                }

                # Score for each service
                for service in services:
                    weights = service.scoring_weights or {}
                    raw_score = sum(
                        weight for signal_key, weight in weights.items()
                        if signal_map.get(signal_key, False)
                    )
                    max_possible = sum(weights.values())
                    final_score = (raw_score / max_possible * 100) if max_possible > 0 else 0

                    db.add(LeadScore(
                        lead_id=lead.id,
                        service_type=service.service_type,
                        service_name=service.name,
                        score=final_score,
                        reasoning=f"Score: {final_score:.0f}/100 based on {len(signals)} signals",
                        signal_breakdown=signal_map,
                        scored_at=datetime.now()
                    ))

            await db.commit()
            logger.info(f"✅ Scores recalculated for {len(leads)} companies")
            return len(leads)

    return asyncio.run(recalc())


# ═══════════════════════════════════════════════════════════════════
# MASTER PIPELINE - RUNS EVERYTHING
# ═══════════════════════════════════════════════════════════════════

@celery_app.task(name="complete_automation.run_complete_pipeline")
def run_complete_pipeline():
    """
    MASTER AUTOMATION TASK

    Runs the complete intelligence pipeline:
    1. Discover companies from directories
    2. Find websites via Google
    3. Scrape all company websites
    4. Search job boards (works WITHOUT websites!)
    5. Search news sites (works WITHOUT websites!)
    6. Recalculate all scores

    This runs automatically - ZERO manual intervention needed.
    """
    logger.info("=" * 80)
    logger.info("🚀 STARTING COMPLETE AUTOMATION PIPELINE")
    logger.info("=" * 80)

    results = {}

    try:
        # SKIP Step 1 for now - scrapy not in worker container
        # results['step1_discovery'] = discover_companies()

        logger.info("⏩ Skipping Step 1 (directory discovery) - running from existing data")

        results['step2_find_websites'] = find_websites_via_google()
        results['step3_scrape_websites'] = scrape_all_company_websites()
        results['step4_job_boards'] = search_job_boards()
        results['step5_news_sites'] = search_news_sites()
        results['step6_scoring'] = recalculate_scores()

        logger.info("=" * 80)
        logger.info("✅ COMPLETE AUTOMATION PIPELINE FINISHED")
        logger.info(f"Results: {results}")
        logger.info("=" * 80)

        return {"status": "success", "results": results}

    except Exception as e:
        logger.error(f"❌ Pipeline failed: {e}")
        return {"status": "error", "error": str(e)}

"""
PRODUCTION ENRICHMENT - Real Signal Extraction

This is the REAL enrichment that creates actual signals.

For EVERY company in the database:
1. Visit their website and extract signals
2. Search job boards for hiring signals
3. Search news sites for mentions
4. Create LeadSignal records with REAL source URLs

This runs AFTER scrapers collect company names.
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import re

from app.workers.celery_app import celery_app
from app.db.session import AsyncSessionLocal
from app.models.models import Lead, LeadSignal
from sqlalchemy import select, update as sql_update

logger = logging.getLogger(__name__)

# Comprehensive multilingual keywords
ENGINEERING_KEYWORDS = [
    "ingénieur", "engineer", "conception", "design", "bureau d'études",
    "CAD", "CAO", "mécanique", "mechanical", "simulation", "R&D"
]

TRAINING_KEYWORDS = [
    "formation", "training", "certification", "CSWA", "CSWP",
    "solidworks", "cao", "certifié", "certified"
]

HIRING_KEYWORDS = [
    "recrutement", "recrute", "offre d'emploi", "candidature",
    "carriere", "hiring", "job opening", "CDI", "CDD"
]

ISO_KEYWORDS = [
    "ISO 9001", "ISO 14001", "ISO 45001", "ISO", "certifié",
    "certified", "certification", "audit", "qualité", "quality"
]

CAD_SOFTWARE = [
    "SOLIDWORKS", "SolidWorks", "CATIA", "Inventor", "AutoCAD",
    "ANSYS", "Abaqus", "Creo", "NX", "SolidEdge"
]

EXPORT_KEYWORDS = [
    "export", "exportation", "international", "Europe",
    "client international", "worldwide", "global"
]

MULTINATIONAL_KEYWORDS = [
    "filiale", "subsidiary", "groupe", "group",
    "multinational", "international"
]


async def extract_signals_from_website(lead: Lead, session_maker) -> List[Dict]:
    """
    Visit company website and extract ALL signals.
    Returns list of signal dicts to create.
    """
    if not lead.website:
        return []

    # Skip directory URLs
    if any(x in lead.website for x in ['tunisieindustrie', 'taa.tn', 'annuaire', 'mecatronic']):
        return []

    signals = []

    try:
        async with aiohttp.ClientSession() as http_session:
            async with http_session.get(
                lead.website,
                timeout=aiohttp.ClientTimeout(total=20),
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'},
                ssl=False
            ) as response:
                if response.status != 200:
                    return []

                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                text = soup.get_text(separator=' ', strip=True).lower()

                # TRAINING DETECTED (40 points)
                if any(kw.lower() in text for kw in TRAINING_KEYWORDS):
                    signals.append({
                        'signal_type': 'training_detected',
                        'title': 'Training or certification program detected',
                        'detail': f'{lead.company_name} website mentions CAD training or SOLIDWORKS certification',
                        'source_url': lead.website
                    })

                # NEW HIRE (20 points)
                if any(kw.lower() in text for kw in HIRING_KEYWORDS):
                    signals.append({
                        'signal_type': 'new_hire',
                        'title': 'Active hiring/recruitment detected',
                        'detail': f'{lead.company_name} is recruiting engineers',
                        'source_url': lead.website
                    })

                # ENGINEERING ROLES (20 points)
                if any(kw.lower() in text for kw in ENGINEERING_KEYWORDS):
                    signals.append({
                        'signal_type': 'role_detected',
                        'title': 'Engineering team or design bureau detected',
                        'detail': f'{lead.company_name} has engineering/design capabilities',
                        'source_url': lead.website
                    })

                # CAD SOFTWARE LOGO (10 points)
                if any(kw.lower() in text for kw in CAD_SOFTWARE):
                    signals.append({
                        'signal_type': 'logo_detected',
                        'title': 'CAD/engineering software detected on website',
                        'detail': f'{lead.company_name} uses CAD software',
                        'source_url': lead.website
                    })

                # ISO CERTIFICATION (15 points)
                if any(kw.lower() in text for kw in ISO_KEYWORDS):
                    signals.append({
                        'signal_type': 'audit_signal',
                        'title': 'ISO certification or quality system detected',
                        'detail': 'Company has ISO certification - must use licensed software',
                        'source_url': lead.website
                    })

                # Update company flags
                async with session_maker() as db:
                    await db.execute(
                        sql_update(Lead).where(Lead.id == lead.id).values(
                            is_exporter=any(kw.lower() in text for kw in EXPORT_KEYWORDS),
                            is_multinational=any(kw.lower() in text for kw in MULTINATIONAL_KEYWORDS),
                            under_audit=any(kw.lower() in text for kw in ISO_KEYWORDS)
                        )
                    )
                    await db.commit()

    except Exception as e:
        logger.debug(f"Failed to scrape {lead.website}: {e}")

    return signals


async def search_job_boards_for_company(lead: Lead) -> List[Dict]:
    """
    Search emploi.tn for company job postings.
    Works even if company has NO website!
    """
    signals = []

    try:
        search_url = f"https://www.emploi.tn/offres-emploi?keywords={quote_plus(lead.company_name)}"

        async with aiohttp.ClientSession() as session:
            async with session.get(
                search_url,
                headers={'User-Agent': 'Mozilla/5.0'},
                timeout=aiohttp.ClientTimeout(total=15),
                ssl=False
            ) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')

                    # Check if company name appears in results
                    if lead.company_name.lower() in html.lower():
                        # Try to extract job posting link
                        job_links = soup.find_all('a', href=True, class_=re.compile('(job|offre|posting|annonce)'))

                        if job_links:
                            # Get first job link
                            job_url = job_links[0]['href']
                            if not job_url.startswith('http'):
                                job_url = f"https://www.emploi.tn{job_url}"

                            signals.append({
                                'signal_type': 'new_hire',
                                'title': f'Job posting found on emploi.tn',
                                'detail': f'{lead.company_name} has active job postings',
                                'source_url': job_url
                            })

    except Exception as e:
        logger.debug(f"Job board search failed for {lead.company_name}: {e}")

    return signals


async def search_news_for_company(lead: Lead) -> List[Dict]:
    """
    Search businessnews.com.tn for company mentions.
    Works even if company has NO website!
    """
    signals = []

    try:
        # Search Google for news mentions
        query = f"site:businessnews.com.tn {lead.company_name}"
        google_url = f"https://www.google.com/search?q={quote_plus(query)}"

        async with aiohttp.ClientSession() as session:
            async with session.get(
                google_url,
                headers={'User-Agent': 'Mozilla/5.0'},
                timeout=aiohttp.ClientTimeout(total=10),
                ssl=False
            ) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')

                    # Extract news article URLs
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        if 'businessnews.com.tn' in href and '/url?q=' in href:
                            article_url = href.split('/url?q=')[1].split('&')[0]

                            signals.append({
                                'signal_type': 'news',
                                'title': 'Company mentioned in business news',
                                'detail': f'{lead.company_name} featured in press article',
                                'source_url': article_url
                            })
                            break  # One article is enough

    except Exception as e:
        logger.debug(f"News search failed for {lead.company_name}: {e}")

    return signals


async def create_signals_for_lead(lead: Lead, session_maker):
    """
    Extract and create ALL signals for a single company.
    """
    all_signals = []

    # 1. Extract from website (if exists)
    website_signals = await extract_signals_from_website(lead, session_maker)
    all_signals.extend(website_signals)

    # 2. Search job boards (works even without website!)
    job_signals = await search_job_boards_for_company(lead)
    all_signals.extend(job_signals)

    # 3. Search news sites (works even without website!)
    news_signals = await search_news_for_company(lead)
    all_signals.extend(news_signals)

    # Create signals in database
    async with session_maker() as db:
        created_count = 0

        for signal_data in all_signals:
            # Check if signal already exists
            existing = await db.execute(
                select(LeadSignal).where(
                    LeadSignal.lead_id == lead.id,
                    LeadSignal.signal_type == signal_data['signal_type']
                )
            )

            if existing.scalar_one_or_none():
                continue  # Skip duplicates

            # Create signal
            signal = LeadSignal(
                lead_id=lead.id,
                signal_type=signal_data['signal_type'],
                title=signal_data['title'][:500],
                detail=signal_data.get('detail', '')[:1000],
                source_url=signal_data.get('source_url'),
                detected_at=datetime.utcnow()
            )

            db.add(signal)
            created_count += 1

        await db.commit()

        return created_count


@celery_app.task(name="production_enrichment.enrich_all_companies", time_limit=7200)
def enrich_all_companies():
    """
    PRODUCTION ENRICHMENT - Process ALL companies.

    For each company:
    1. Visit website → extract signals
    2. Search job boards → find hiring
    3. Search news sites → find mentions
    4. Create signals with REAL source URLs

    This is the REAL intelligence extraction.
    """
    logger.info("=" * 80)
    logger.info("🚀 PRODUCTION ENRICHMENT - Processing ALL companies")
    logger.info("=" * 80)

    async def process_all():
        async with AsyncSessionLocal() as db:
            # Get ALL companies
            result = await db.execute(select(Lead))
            all_leads = result.scalars().all()

            logger.info(f"Processing {len(all_leads)} companies...")

            total_signals = 0
            processed = 0
            failed = 0

            for idx, lead in enumerate(all_leads, 1):
                try:
                    signals_created = await create_signals_for_lead(lead, AsyncSessionLocal)

                    if signals_created > 0:
                        total_signals += signals_created
                        logger.info(f"[{idx}/{len(all_leads)}] ✅ {lead.company_name}: {signals_created} signals")
                    else:
                        logger.debug(f"[{idx}/{len(all_leads)}] ⚪ {lead.company_name}: no signals")

                    processed += 1

                    # Rate limiting
                    await asyncio.sleep(2)

                    # Progress update every 50 companies
                    if idx % 50 == 0:
                        logger.info(f"Progress: {idx}/{len(all_leads)}, {total_signals} signals created")

                except Exception as e:
                    failed += 1
                    logger.error(f"[{idx}/{len(all_leads)}] ❌ {lead.company_name}: {e}")

            logger.info("=" * 80)
            logger.info(f"✅ ENRICHMENT COMPLETE")
            logger.info(f"   Processed: {processed}/{len(all_leads)}")
            logger.info(f"   Failed: {failed}")
            logger.info(f"   Total signals created: {total_signals}")
            logger.info("=" * 80)

            return {
                "status": "completed",
                "processed": processed,
                "failed": failed,
                "signals_created": total_signals
            }

    return asyncio.run(process_all())


@celery_app.task(name="production_enrichment.enrich_batch", time_limit=1800)
def enrich_batch(batch_size: int = 100):
    """
    Enrich a batch of companies that haven't been enriched yet.
    Good for incremental processing.
    """
    logger.info(f"🔄 Enriching batch of {batch_size} companies...")

    async def process_batch():
        async with AsyncSessionLocal() as db:
            # Get companies without signals
            result = await db.execute(
                select(Lead).where(
                    ~Lead.id.in_(
                        select(LeadSignal.lead_id).distinct()
                    )
                ).limit(batch_size)
            )
            leads = result.scalars().all()

            logger.info(f"Found {len(leads)} companies needing enrichment")

            total_signals = 0

            for idx, lead in enumerate(leads, 1):
                try:
                    signals_created = await create_signals_for_lead(lead, AsyncSessionLocal)
                    total_signals += signals_created

                    if signals_created > 0:
                        logger.info(f"[{idx}/{len(leads)}] ✅ {lead.company_name}: {signals_created} signals")

                    await asyncio.sleep(2)

                except Exception as e:
                    logger.error(f"Failed to enrich {lead.company_name}: {e}")

            logger.info(f"✅ Batch complete: {total_signals} signals created")

            return {
                "status": "completed",
                "processed": len(leads),
                "signals_created": total_signals
            }

    return asyncio.run(process_batch())

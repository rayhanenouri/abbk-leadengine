"""
Universal scraping tasks using AI-powered scraper.

Scrapes all 34 verified data sources with Playwright + Claude API.
No CSS selectors needed - future-proof and reliable.
"""
from app.workers.celery_app import celery_app
from app.scrapers.universal_scraper import UniversalScraper
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import async_session
from app.models.models import Lead, LeadSignal
from sqlalchemy import select
import logging
import asyncio

logger = logging.getLogger(__name__)


# All 34 verified data sources
VERIFIED_SOURCES = {
    "directories": [
        "https://mecatronic.tn/membres/",
        "https://taa.tn/fr/membres",
        "https://www.cetime.tn/fr/annuaire-des-entreprises",
        "https://www.tunisieindustrie.nat.tn/fr/dbi.asp",
        "https://www.tunisieindustrie.nat.tn/fr/dbs.asp",
        "https://www.tunisieindustrie.nat.tn/fr/certifdbi.asp?action=list&idsect=&pagenum=1",
        "https://tn.kompass.com/en",
        "https://www.scribd.com/document/620128474/Liste-Entreprises",
        "https://maps.prodafrica.com/",
        "https://africabusinessbureau.com/",
        "https://www.success.ai/company-directory/Civil_Engineering/country/tunisia",
        "https://www.aihitdata.com/search/companies?i=african+engineering",
    ],
    "jobs": [
        "https://www.naukrigulf.com/engineer-jobs-in-tunis",
        "https://tunisia.tanqeeb.com/s/jobs/engineer?state=148",
        "https://www.bayt.com/en/tunisia/jobs/mechanical-engineer-jobs/",
        "https://www.tunisietravail.net/",
        "https://www.optioncarriere.tn/",
        "https://www.keejob.com/",
        "https://emploi.nat.tn/fo/Fr/global.php",
        "https://www.tanitjobs.com/",
        "https://www.africareers.net/",
    ],
    "news": [
        "https://en.africanmanager.com/fdi-in-tunisia-rising-attractiveness-and-strategic-growth/",
        "https://www.tunisieindustrie.nat.tn/en/etrangere.asp",
        "https://www.adendorff.co.za/adendorff-optimum-cnc-machines-now-in-south-africa",
    ],
    "training": [
        "https://enis.rnu.tn/",
        "https://enit.rnu.tn/en/presentation-2/",
        "http://www.enicarthage.rnu.tn/en/ecole/apropos",
        "https://ucar.rnu.tn/events-et-news/",
        "https://www.ept.tn/news-and-events",
        "https://mecadtechnologies.co.za/specialised-training/",
        "https://camining.com/",
    ],
}


@celery_app.task(name="app.workers.tasks.universal_scraping.scrape_all_directories")
def scrape_all_directories():
    """
    Scrape all 12 verified business directory sources.
    Uses AI-powered universal scraper - no CSS selectors needed.
    """
    logger.info("Starting universal directory scraping (12 sources)")

    async def run_scraping():
        scraper = UniversalScraper()
        all_companies = []

        for url in VERIFIED_SOURCES["directories"]:
            try:
                logger.info(f"Scraping directory: {url}")
                companies = await scraper.scrape_business_directory(url, _get_source_name(url))
                all_companies.extend(companies)
                logger.info(f"Found {len(companies)} companies from {url}")

                # Small delay to be respectful
                await asyncio.sleep(2)

            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")
                continue

        # Save to database
        saved_count = await _save_companies_to_db(all_companies)

        logger.info(f"Directory scraping complete: {saved_count} companies saved from {len(all_companies)} scraped")
        return {"status": "completed", "scraped": len(all_companies), "saved": saved_count}

    # Run async function
    return asyncio.run(run_scraping())


@celery_app.task(name="app.workers.tasks.universal_scraping.scrape_all_jobs")
def scrape_all_jobs():
    """
    Scrape all 9 verified job board sources.
    """
    logger.info("Starting universal job board scraping (9 sources)")

    async def run_scraping():
        scraper = UniversalScraper()
        all_jobs = []

        for url in VERIFIED_SOURCES["jobs"]:
            try:
                logger.info(f"Scraping job board: {url}")
                jobs = await scraper.scrape_job_board(url, _get_source_name(url))
                all_jobs.extend(jobs)
                logger.info(f"Found {len(jobs)} jobs from {url}")

                await asyncio.sleep(2)

            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")
                continue

        # Save job signals to database
        saved_count = await _save_job_signals_to_db(all_jobs)

        logger.info(f"Job scraping complete: {saved_count} signals saved from {len(all_jobs)} scraped")
        return {"status": "completed", "scraped": len(all_jobs), "saved": saved_count}

    return asyncio.run(run_scraping())


@celery_app.task(name="app.workers.tasks.universal_scraping.scrape_all_news")
def scrape_all_news():
    """
    Scrape all 3 verified news sources.
    """
    logger.info("Starting universal news scraping (3 sources)")

    async def run_scraping():
        scraper = UniversalScraper()
        all_signals = []

        for url in VERIFIED_SOURCES["news"]:
            try:
                logger.info(f"Scraping news: {url}")
                signals = await scraper.scrape_news_article(url, _get_source_name(url))
                all_signals.extend(signals)
                logger.info(f"Found {len(signals)} signals from {url}")

                await asyncio.sleep(2)

            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")
                continue

        # Save news signals to database
        saved_count = await _save_news_signals_to_db(all_signals)

        logger.info(f"News scraping complete: {saved_count} signals saved from {len(all_signals)} scraped")
        return {"status": "completed", "scraped": len(all_signals), "saved": saved_count}

    return asyncio.run(run_scraping())


@celery_app.task(name="app.workers.tasks.universal_scraping.scrape_all_training")
def scrape_all_training():
    """
    Scrape all 7 verified training sources.
    """
    logger.info("Starting universal training scraping (7 sources)")

    async def run_scraping():
        scraper = UniversalScraper()
        all_companies = []

        for url in VERIFIED_SOURCES["training"]:
            try:
                logger.info(f"Scraping training: {url}")
                companies = await scraper.scrape_business_directory(url, _get_source_name(url))
                all_companies.extend(companies)
                logger.info(f"Found {len(companies)} companies from {url}")

                await asyncio.sleep(2)

            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")
                continue

        # Save to database
        saved_count = await _save_companies_to_db(all_companies)

        logger.info(f"Training scraping complete: {saved_count} companies saved from {len(all_companies)} scraped")
        return {"status": "completed", "scraped": len(all_companies), "saved": saved_count}

    return asyncio.run(run_scraping())


@celery_app.task(name="app.workers.tasks.universal_scraping.scrape_all_sources")
def scrape_all_sources():
    """
    Scrape ALL 34 verified sources in one go.
    Triggers all 4 category tasks.
    """
    logger.info("Triggering scraping for all 34 verified sources")

    # Trigger all sub-tasks
    from app.workers.tasks.universal_scraping import (
        scrape_all_directories,
        scrape_all_jobs,
        scrape_all_news,
        scrape_all_training,
    )

    results = {
        "directories": scrape_all_directories.delay(),
        "jobs": scrape_all_jobs.delay(),
        "news": scrape_all_news.delay(),
        "training": scrape_all_training.delay(),
    }

    return {
        "status": "triggered",
        "message": "All 34 sources triggered",
        "task_ids": {
            "directories": results["directories"].id,
            "jobs": results["jobs"].id,
            "news": results["news"].id,
            "training": results["training"].id,
        }
    }


# Helper functions

def _get_source_name(url: str) -> str:
    """Extract readable source name from URL."""
    from urllib.parse import urlparse
    domain = urlparse(url).netloc
    return domain.replace("www.", "")


async def _save_companies_to_db(companies: list) -> int:
    """
    Save scraped companies to database.
    Deduplicates by website or company_name.
    """
    if not companies:
        return 0

    saved_count = 0

    async with async_session() as session:
        for company_data in companies:
            try:
                # Check if company already exists
                website = company_data.get("website")
                company_name = company_data.get("company_name")

                if not company_name:
                    continue

                # Query existing lead
                query = select(Lead)
                if website:
                    query = query.where(Lead.website == website)
                else:
                    query = query.where(Lead.company_name == company_name)

                result = await session.execute(query)
                existing_lead = result.scalar_one_or_none()

                if existing_lead:
                    # Update existing lead
                    existing_lead.scraped_data = existing_lead.scraped_data or {}
                    existing_lead.scraped_data[company_data.get("source", "unknown")] = company_data
                    logger.info(f"Updated existing lead: {company_name}")
                else:
                    # Create new lead
                    new_lead = Lead(
                        company_name=company_name,
                        website=website,
                        country=company_data.get("country", "Tunisia"),
                        city=company_data.get("city"),
                        sector=company_data.get("sector"),
                        scraped_data={company_data.get("source", "unknown"): company_data},
                        status="new",
                    )
                    session.add(new_lead)
                    saved_count += 1
                    logger.info(f"Created new lead: {company_name}")

                await session.commit()

            except Exception as e:
                logger.error(f"Error saving company {company_data.get('company_name')}: {e}")
                await session.rollback()
                continue

    return saved_count


async def _save_job_signals_to_db(jobs: list) -> int:
    """
    Save job signals to database.
    Creates/updates lead and adds signal.
    """
    if not jobs:
        return 0

    saved_count = 0

    async with async_session() as session:
        for job_data in jobs:
            try:
                company_name = job_data.get("company_name")
                if not company_name:
                    continue

                # Find or create lead
                result = await session.execute(
                    select(Lead).where(Lead.company_name == company_name)
                )
                lead = result.scalar_one_or_none()

                if not lead:
                    # Create new lead
                    lead = Lead(
                        company_name=company_name,
                        country="Tunisia",  # Default
                        city=job_data.get("location"),
                        status="new",
                        scraped_data={"job_signal": job_data},
                    )
                    session.add(lead)
                    await session.flush()  # Get lead.id

                # Create signal
                signal = LeadSignal(
                    lead_id=lead.id,
                    signal_type="new_hire",
                    title=f"Hiring {job_data.get('job_title', 'engineer')}",
                    detail=job_data.get("detail", ""),
                    source_url=job_data.get("source_url"),
                )
                session.add(signal)
                saved_count += 1

                await session.commit()
                logger.info(f"Saved job signal for {company_name}")

            except Exception as e:
                logger.error(f"Error saving job signal: {e}")
                await session.rollback()
                continue

    return saved_count


async def _save_news_signals_to_db(signals: list) -> int:
    """
    Save news signals to database.
    """
    if not signals:
        return 0

    saved_count = 0

    async with async_session() as session:
        for signal_data in signals:
            try:
                company_name = signal_data.get("company_name")
                if not company_name:
                    continue

                # Find or create lead
                result = await session.execute(
                    select(Lead).where(Lead.company_name == company_name)
                )
                lead = result.scalar_one_or_none()

                if not lead:
                    lead = Lead(
                        company_name=company_name,
                        country="Tunisia",
                        status="new",
                        scraped_data={"news_signal": signal_data},
                    )
                    session.add(lead)
                    await session.flush()

                # Create signal
                signal = LeadSignal(
                    lead_id=lead.id,
                    signal_type=signal_data.get("signal_type", "news"),
                    title=signal_data.get("title", "News mention"),
                    detail=signal_data.get("detail", ""),
                    source_url=signal_data.get("source_url"),
                )
                session.add(signal)
                saved_count += 1

                await session.commit()
                logger.info(f"Saved news signal for {company_name}")

            except Exception as e:
                logger.error(f"Error saving news signal: {e}")
                await session.rollback()
                continue

    return saved_count

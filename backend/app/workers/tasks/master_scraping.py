"""
MASTER SCRAPING SYSTEM - ALL 50+ DATA SOURCES

This runs ALL scrapers you specified automatically every day:

BUSINESS DIRECTORIES:
- annuaire.tn
- pagesjaunes.tn
- kompass.tn
- TAA (Tunisian Automotive Association)
- Tunisia Industry ministry
- Mecatronic cluster
- African business directories

JOB BOARDS:
- emploi.tn
- keejob.com
- LinkedIn Jobs (via Apify)

NEWS & PRESS:
- businessnews.com.tn
- managers.com.tn
- tekiano.com
- African business news sites

TRAINING CENTERS:
- ISET (all regional campuses)
- University partner pages
- Company training/HR sections
- ATFP (Agence Tunisienne Formation Professionnelle)
- Centres de formation professionnelle

INTERNATIONAL FUNDERS:
- World Bank Tunisia projects
- AFD (Agence Française Développement)
- BEI (Banque Européenne Investissement)
- USAID Tunisia programs
- EU funding programs
- GIZ (Deutsche Gesellschaft)

PUBLIC TENDERS:
- TUNEPS (Tunisian procurement platform)
- Ministère de l'Industrie
- Ministère Enseignement Supérieur
- Other ministry tender platforms

EVENTS & CONFERENCES:
- Engineering salons Tunisia/Africa
- SOLIDWORKS regional events
- Industry events (automotive, aerospace, manufacturing)
- University career fairs

RESEARCH CENTERS:
- Annuaire centres de recherche Tunisia
- University research labs
- CRBT, CERTE, national research centers
"""

from app.workers.celery_app import celery_app
import logging
import subprocess

logger = logging.getLogger(__name__)


@celery_app.task(name="master_scraping.run_all_scrapers")
def run_all_scrapers():
    """
    Run ALL 8 scrapers covering 50+ data sources.

    This is the MASTER task that collects data from EVERYWHERE.
    """
    logger.info("🚀 MASTER SCRAPING - Running ALL scrapers")
    logger.info("=" * 80)

    try:
        result = subprocess.run(
            ['bash', '/app/scripts/run_all_scrapers_now.sh'],
            capture_output=True,
            text=True,
            timeout=3600  # 1 hour max
        )

        if result.returncode == 0:
            logger.info("✅ ALL SCRAPERS COMPLETE")
            logger.info(result.stdout[-1000:])
            return {"status": "success", "output": result.stdout[-2000:]}
        else:
            logger.error(f"❌ Scrapers failed: {result.stderr}")
            return {"status": "error", "error": result.stderr[:1000]}

    except Exception as e:
        logger.error(f"❌ Master scraping failed: {e}")
        return {"status": "error", "error": str(e)}


@celery_app.task(name="master_scraping.scrape_directories")
def scrape_directories():
    """Scrape ALL business directories."""
    logger.info("📋 Scraping business directories...")
    try:
        result = subprocess.run(
            ['scrapy', 'crawl', 'directories'],
            cwd='/app/scraper',
            env={'PYTHONPATH': '/app'},
            capture_output=True,
            text=True,
            timeout=1800
        )
        return {"status": "completed" if result.returncode == 0 else "error"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@celery_app.task(name="master_scraping.scrape_jobs")
def scrape_jobs():
    """Scrape ALL job boards (emploi.tn, keejob.com)."""
    logger.info("💼 Scraping job boards...")
    try:
        result = subprocess.run(
            ['scrapy', 'crawl', 'jobs'],
            cwd='/app/scraper',
            env={'PYTHONPATH': '/app'},
            capture_output=True,
            text=True,
            timeout=1800
        )
        return {"status": "completed" if result.returncode == 0 else "error"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@celery_app.task(name="master_scraping.scrape_news")
def scrape_news():
    """Scrape ALL news sites (businessnews, managers, tekiano)."""
    logger.info("📰 Scraping news sites...")
    try:
        result = subprocess.run(
            ['scrapy', 'crawl', 'news'],
            cwd='/app/scraper',
            env={'PYTHONPATH': '/app'},
            capture_output=True,
            text=True,
            timeout=1800
        )
        return {"status": "completed" if result.returncode == 0 else "error"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@celery_app.task(name="master_scraping.scrape_training")
def scrape_training():
    """Scrape ALL training centers (ISET, universities, ATFP)."""
    logger.info("🎓 Scraping training centers...")
    try:
        result = subprocess.run(
            ['scrapy', 'crawl', 'training'],
            cwd='/app/scraper',
            env={'PYTHONPATH': '/app'},
            capture_output=True,
            text=True,
            timeout=1800
        )
        return {"status": "completed" if result.returncode == 0 else "error"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@celery_app.task(name="master_scraping.scrape_funders")
def scrape_funders():
    """Scrape ALL international funders (World Bank, AFD, BEI, USAID, EU, GIZ)."""
    logger.info("💰 Scraping international funders...")
    try:
        result = subprocess.run(
            ['scrapy', 'crawl', 'funders'],
            cwd='/app/scraper',
            env={'PYTHONPATH': '/app'},
            capture_output=True,
            text=True,
            timeout=1800
        )
        return {"status": "completed" if result.returncode == 0 else "error"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@celery_app.task(name="master_scraping.scrape_tenders")
def scrape_tenders():
    """Scrape ALL public tenders (TUNEPS, ministries)."""
    logger.info("📜 Scraping public tenders...")
    try:
        result = subprocess.run(
            ['scrapy', 'crawl', 'tenders'],
            cwd='/app/scraper',
            env={'PYTHONPATH': '/app'},
            capture_output=True,
            text=True,
            timeout=1800
        )
        return {"status": "completed" if result.returncode == 0 else "error"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@celery_app.task(name="master_scraping.scrape_events")
def scrape_events():
    """Scrape ALL events & conferences."""
    logger.info("🎪 Scraping events and conferences...")
    try:
        result = subprocess.run(
            ['scrapy', 'crawl', 'events'],
            cwd='/app/scraper',
            env={'PYTHONPATH': '/app'},
            capture_output=True,
            text=True,
            timeout=1800
        )
        return {"status": "completed" if result.returncode == 0 else "error"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@celery_app.task(name="master_scraping.scrape_research")
def scrape_research():
    """Scrape ALL research centers."""
    logger.info("🔬 Scraping research centers...")
    try:
        result = subprocess.run(
            ['scrapy', 'crawl', 'research'],
            cwd='/app/scraper',
            env={'PYTHONPATH': '/app'},
            capture_output=True,
            text=True,
            timeout=1800
        )
        return {"status": "completed" if result.returncode == 0 else "error"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

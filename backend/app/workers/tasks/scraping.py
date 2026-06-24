from app.workers.celery_app import celery_app
import logging
import subprocess
import sys
import os

logger = logging.getLogger(__name__)

# Get the backend directory path
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


@celery_app.task(name="app.workers.tasks.scraping.scrape_linkedin")
def scrape_linkedin():
    """Scrape LinkedIn companies using Apify."""
    logger.info("TODO: Implement LinkedIn scraping with Apify")
    return {"status": "not_implemented"}


@celery_app.task(name="app.workers.tasks.scraping.scrape_news")
def scrape_news():
    """
    Scrape Tunisian business news.

    Runs BusinessNewsSpider to collect signals from:
    - businessnews.com.tn
    - managers.com.tn
    - tekiano.com

    Returns count of signals created.
    """
    try:
        script_path = os.path.join(BACKEND_DIR, "run_news_spider.py")
        result = subprocess.run([sys.executable, script_path], capture_output=True, text=True, timeout=600)

        if result.returncode == 0:
            logger.info(f"News spider completed: {result.stdout}")
            return {"status": "completed", "spider": "news", "output": result.stdout[:500]}
        else:
            logger.error(f"News spider failed: {result.stderr}")
            return {"status": "error", "error": result.stderr[:500]}

    except Exception as e:
        logger.error(f"Error running news spider: {e}")
        return {"status": "error", "error": str(e)}


@celery_app.task(name="app.workers.tasks.scraping.scrape_jobs")
def scrape_jobs():
    """
    Scrape job boards for hiring signals.

    Runs JobsBoardsSpider to collect hiring signals from:
    - emploi.tn
    - keejob.com

    Returns count of signals created.
    """
    try:
        script_path = os.path.join(BACKEND_DIR, "run_jobs_spider.py")
        result = subprocess.run([sys.executable, script_path], capture_output=True, text=True, timeout=600)

        if result.returncode == 0:
            logger.info(f"Jobs spider completed: {result.stdout}")
            return {"status": "completed", "spider": "jobs", "output": result.stdout[:500]}
        else:
            logger.error(f"Jobs spider failed: {result.stderr}")
            return {"status": "error", "error": result.stderr[:500]}

    except Exception as e:
        logger.error(f"Error running jobs spider: {e}")
        return {"status": "error", "error": str(e)}


@celery_app.task(name="app.workers.tasks.scraping.scrape_directories")
def scrape_directories():
    """
    Scrape Tunisian business directories.

    Runs DirectoriesSpider to collect companies from:
    - annuaire.tn
    - pagesjaunes.tn
    - kompass.tn

    Returns count of companies scraped.
    """
    try:
        # Run spider as subprocess to avoid Twisted reactor conflicts
        script_path = os.path.join(BACKEND_DIR, "run_directories_spider.py")

        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=600  # 10 minutes timeout
        )

        if result.returncode == 0:
            logger.info(f"Directories spider completed successfully: {result.stdout}")
            return {"status": "completed", "spider": "directories", "output": result.stdout[:500]}
        else:
            logger.error(f"Directories spider failed: {result.stderr}")
            return {"status": "error", "error": result.stderr[:500]}

    except Exception as e:
        logger.error(f"Error running directories spider: {e}")
        return {"status": "error", "error": str(e)}


@celery_app.task(name="app.workers.tasks.scraping.scrape_training")
def scrape_training():
    """
    Scrape training centers for company participation signals.

    Runs TrainingCentersSpider to collect training signals from:
    - ISET websites (all regional campuses)
    - University partner pages
    - ATFP (Agence Tunisienne de la Formation Professionnelle)
    - Professional training centers

    Returns count of signals created.
    """
    try:
        script_path = os.path.join(BACKEND_DIR, "run_training_spider.py")
        result = subprocess.run([sys.executable, script_path], capture_output=True, text=True, timeout=600)

        if result.returncode == 0:
            logger.info(f"Training spider completed: {result.stdout}")
            return {"status": "completed", "spider": "training", "output": result.stdout[:500]}
        else:
            logger.error(f"Training spider failed: {result.stderr}")
            return {"status": "error", "error": result.stderr[:500]}

    except Exception as e:
        logger.error(f"Error running training spider: {e}")
        return {"status": "error", "error": str(e)}


@celery_app.task(name="app.workers.tasks.scraping.scrape_funders")
def scrape_funders():
    """
    Scrape international funding organizations for funded Tunisian companies.

    Runs FundersSpider to collect funding signals from:
    - World Bank Tunisia projects
    - AFD (Agence Française de Développement)
    - EIB (European Investment Bank)
    - EU funding programs
    - USAID Tunisia
    - GIZ (German development cooperation)
    - African Development Bank

    Companies with international funding MUST use licensed software (audit requirement).
    Sets under_audit=True flag on leads.

    Returns count of signals created.
    """
    try:
        script_path = os.path.join(BACKEND_DIR, "run_funders_spider.py")
        result = subprocess.run([sys.executable, script_path], capture_output=True, text=True, timeout=600)

        if result.returncode == 0:
            logger.info(f"Funders spider completed: {result.stdout}")
            return {"status": "completed", "spider": "funders", "output": result.stdout[:500]}
        else:
            logger.error(f"Funders spider failed: {result.stderr}")
            return {"status": "error", "error": result.stderr[:500]}

    except Exception as e:
        logger.error(f"Error running funders spider: {e}")
        return {"status": "error", "error": str(e)}


@celery_app.task(name="app.workers.tasks.scraping.scrape_tenders")
def scrape_tenders():
    """
    Scrape public tender platforms for engineering contract winners.

    Runs TendersSpider to collect tender signals from:
    - TUNEPS (Tunisia National Electronic Procurement System)
    - Ministry of Industry tenders
    - Ministry of Equipment tenders
    - HAICOP (Haute Instance de la Commande Publique)
    - Marchés Publics portal
    - JORT (Journal Officiel)

    Companies winning public tenders MUST use licensed software (transparency + audit).
    Sets under_audit=True flag on leads.

    Returns count of signals created.
    """
    try:
        script_path = os.path.join(BACKEND_DIR, "run_tenders_spider.py")
        result = subprocess.run([sys.executable, script_path], capture_output=True, text=True, timeout=600)

        if result.returncode == 0:
            logger.info(f"Tenders spider completed: {result.stdout}")
            return {"status": "completed", "spider": "tenders", "output": result.stdout[:500]}
        else:
            logger.error(f"Tenders spider failed: {result.stderr}")
            return {"status": "error", "error": result.stderr[:500]}

    except Exception as e:
        logger.error(f"Error running tenders spider: {e}")
        return {"status": "error", "error": str(e)}


@celery_app.task(name="app.workers.tasks.scraping.scrape_events")
def scrape_events():
    """
    Scrape engineering event websites for participant/exhibitor companies.

    Runs EventsSpider to collect event attendance signals from:
    - SOLIDWORKS regional events
    - Tunisia engineering salons
    - Industry conferences
    - Trade shows
    - University career fairs

    Companies attending engineering events = warm leads (actively engaged in engineering).

    Returns count of signals created.
    """
    try:
        script_path = os.path.join(BACKEND_DIR, "run_events_spider.py")
        result = subprocess.run([sys.executable, script_path], capture_output=True, text=True, timeout=600)

        if result.returncode == 0:
            logger.info(f"Events spider completed: {result.stdout}")
            return {"status": "completed", "spider": "events", "output": result.stdout[:500]}
        else:
            logger.error(f"Events spider failed: {result.stderr}")
            return {"status": "error", "error": result.stderr[:500]}

    except Exception as e:
        logger.error(f"Error running events spider: {e}")
        return {"status": "error", "error": str(e)}

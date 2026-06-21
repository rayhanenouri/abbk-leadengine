from app.workers.celery_app import celery_app
from scrapy.crawler import CrawlerRunner
from twisted.internet import reactor
from scrapy.utils.project import get_project_settings
import logging

logger = logging.getLogger(__name__)


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
        from app.scrapers.spiders.news_spider import BusinessNewsSpider
        from scrapy.crawler import CrawlerProcess
        from app.scrapers import settings as scrapy_settings

        settings_dict = {
            key: getattr(scrapy_settings, key)
            for key in dir(scrapy_settings)
            if key.isupper()
        }

        process = CrawlerProcess(settings_dict)
        process.crawl(BusinessNewsSpider)
        process.start()

        logger.info("News spider completed successfully")
        return {"status": "completed", "spider": "news"}

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
        from app.scrapers.spiders.jobs_spider import JobsBoardsSpider
        from scrapy.crawler import CrawlerProcess
        from app.scrapers import settings as scrapy_settings

        settings_dict = {
            key: getattr(scrapy_settings, key)
            for key in dir(scrapy_settings)
            if key.isupper()
        }

        process = CrawlerProcess(settings_dict)
        process.crawl(JobsBoardsSpider)
        process.start()

        logger.info("Jobs spider completed successfully")
        return {"status": "completed", "spider": "jobs"}

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
        from app.scrapers.spiders.directories_spider import DirectoriesSpider
        from scrapy.crawler import CrawlerProcess

        # Load settings
        from app.scrapers import settings as scrapy_settings
        settings_dict = {
            key: getattr(scrapy_settings, key)
            for key in dir(scrapy_settings)
            if key.isupper()
        }

        # Run spider
        process = CrawlerProcess(settings_dict)
        process.crawl(DirectoriesSpider)
        process.start()

        logger.info("Directories spider completed successfully")
        return {"status": "completed", "spider": "directories"}

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
        from app.scrapers.spiders.training_spider import TrainingCentersSpider
        from scrapy.crawler import CrawlerProcess
        from app.scrapers import settings as scrapy_settings

        settings_dict = {
            key: getattr(scrapy_settings, key)
            for key in dir(scrapy_settings)
            if key.isupper()
        }

        process = CrawlerProcess(settings_dict)
        process.crawl(TrainingCentersSpider)
        process.start()

        logger.info("Training spider completed successfully")
        return {"status": "completed", "spider": "training"}

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
        from app.scrapers.spiders.funders_spider import FundersSpider
        from scrapy.crawler import CrawlerProcess
        from app.scrapers import settings as scrapy_settings

        settings_dict = {
            key: getattr(scrapy_settings, key)
            for key in dir(scrapy_settings)
            if key.isupper()
        }

        process = CrawlerProcess(settings_dict)
        process.crawl(FundersSpider)
        process.start()

        logger.info("Funders spider completed successfully")
        return {"status": "completed", "spider": "funders"}

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
        from app.scrapers.spiders.tenders_spider import TendersSpider
        from scrapy.crawler import CrawlerProcess
        from app.scrapers import settings as scrapy_settings

        settings_dict = {
            key: getattr(scrapy_settings, key)
            for key in dir(scrapy_settings)
            if key.isupper()
        }

        process = CrawlerProcess(settings_dict)
        process.crawl(TendersSpider)
        process.start()

        logger.info("Tenders spider completed successfully")
        return {"status": "completed", "spider": "tenders"}

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
        from app.scrapers.spiders.events_spider import EventsSpider
        from scrapy.crawler import CrawlerProcess
        from app.scrapers import settings as scrapy_settings

        settings_dict = {
            key: getattr(scrapy_settings, key)
            for key in dir(scrapy_settings)
            if key.isupper()
        }

        process = CrawlerProcess(settings_dict)
        process.crawl(EventsSpider)
        process.start()

        logger.info("Events spider completed successfully")
        return {"status": "completed", "spider": "events"}

    except Exception as e:
        logger.error(f"Error running events spider: {e}")
        return {"status": "error", "error": str(e)}

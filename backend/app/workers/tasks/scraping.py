from app.workers.celery_app import celery_app
from scrapy.crawler import CrawlerRunner
from twisted.internet import reactor
from scrapy.utils.project import get_project_settings
import logging

logger = logging.getLogger(__name__)


@celery_app.task(name="app.workers.tasks.scraping.scrape_linkedin_companies")
def scrape_linkedin_companies():
    """Scrape LinkedIn companies using Apify."""
    logger.info("TODO: Implement LinkedIn scraping")
    return {"status": "not_implemented"}


@celery_app.task(name="app.workers.tasks.scraping.scrape_news_and_jobs")
def scrape_news_and_jobs():
    """Scrape news and job boards."""
    logger.info("TODO: Implement news and jobs scraping")
    return {"status": "not_implemented"}


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

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

#!/usr/bin/env python3
"""
Standalone runner for DirectoriesSpider.
Used by Celery tasks to avoid reactor conflicts.
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scrapy.crawler import CrawlerProcess
from app.scrapers.spiders.directories_spider import DirectoriesSpider
from app.scrapers import settings as scrapy_settings


def main():
    """Run DirectoriesSpider standalone."""

    # Load Scrapy settings
    settings_dict = {
        key: getattr(scrapy_settings, key)
        for key in dir(scrapy_settings)
        if key.isupper()
    }

    print("Starting DirectoriesSpider...")
    print("Targets: annuaire.tn, pagesjaunes.tn, kompass.tn")

    # Create and run crawler
    process = CrawlerProcess(settings_dict)
    process.crawl(DirectoriesSpider)
    process.start()

    print("DirectoriesSpider completed successfully!")


if __name__ == '__main__':
    main()

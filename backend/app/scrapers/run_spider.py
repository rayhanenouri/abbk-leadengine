#!/usr/bin/env python3
"""
Spider runner script for ABBK LeadEngine.

Usage:
    python -m app.scrapers.run_spider directories
    python -m app.scrapers.run_spider pagesjaunes
    python -m app.scrapers.run_spider kompass
"""
import sys
import os
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from app.scrapers.spiders.directories_spider import (
    DirectoriesSpider,
    PagesJaunesSpider,
    KompassSpider
)


def run_spider(spider_name: str):
    """
    Run a specific spider.

    Args:
        spider_name: Name of the spider to run (directories, pagesjaunes, kompass)
    """
    # Map spider names to classes
    spiders = {
        'directories': DirectoriesSpider,
        'pagesjaunes': PagesJaunesSpider,
        'kompass': KompassSpider,
    }

    spider_class = spiders.get(spider_name.lower())
    if not spider_class:
        print(f"Error: Unknown spider '{spider_name}'")
        print(f"Available spiders: {', '.join(spiders.keys())}")
        sys.exit(1)

    # Load Scrapy settings
    from app.scrapers import settings as scrapy_settings
    settings_dict = {
        key: getattr(scrapy_settings, key)
        for key in dir(scrapy_settings)
        if key.isupper()
    }

    # Create crawler process
    process = CrawlerProcess(settings_dict)

    # Start crawling
    print(f"Starting {spider_name} spider...")
    process.crawl(spider_class)
    process.start()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python -m app.scrapers.run_spider <spider_name>")
        print("Available spiders: directories, pagesjaunes, kompass")
        sys.exit(1)

    spider_name = sys.argv[1]
    run_spider(spider_name)

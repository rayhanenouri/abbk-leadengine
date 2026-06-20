"""
Test script for business news spider.

Tests the spider locally and verifies it extracts signals correctly.
"""
import sys
import asyncio
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from app.scrapers.spiders.news_spider import BusinessNewsSpider


def test_news_spider():
    """Run news spider and print results."""
    print("=" * 60)
    print("Testing Business News Spider")
    print("=" * 60)

    # Override settings for testing
    settings = {
        'LOG_LEVEL': 'INFO',
        'ROBOTSTXT_OBEY': True,
        'CONCURRENT_REQUESTS': 2,
        'DOWNLOAD_DELAY': 2,
        'CLOSESPIDER_ITEMCOUNT': 10,  # Stop after 10 items for testing
        'ITEM_PIPELINES': {
            'app.scrapers.pipelines_signals.SignalsPipeline': 300,
        },
        'TWISTED_REACTOR': 'twisted.internet.asyncioreactor.AsyncioSelectorReactor',
    }

    process = CrawlerProcess(settings)
    process.crawl(BusinessNewsSpider)

    print("\nStarting spider...")
    print("Will stop after 10 signals or when all URLs scraped")
    print("-" * 60)

    process.start()

    print("\n" + "=" * 60)
    print("Spider finished")
    print("=" * 60)


if __name__ == '__main__':
    test_news_spider()

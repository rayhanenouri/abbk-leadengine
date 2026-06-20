"""
Test script for job boards spider.

Tests the spider locally to verify it works correctly.
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from scrapy.crawler import CrawlerProcess
from app.scrapers.spiders.jobs_spider import JobsBoardsSpider


def test_jobs_spider():
    """Run jobs spider with test settings."""
    print("=" * 70)
    print("Testing Job Boards Spider (emploi.tn, keejob.com)")
    print("=" * 70)

    settings = {
        'LOG_LEVEL': 'INFO',
        'ROBOTSTXT_OBEY': True,
        'CONCURRENT_REQUESTS': 2,
        'DOWNLOAD_DELAY': 2,
        'CLOSESPIDER_ITEMCOUNT': 5,  # Stop after 5 items for testing
        'ITEM_PIPELINES': {
            'app.scrapers.pipelines_signals.SignalsPipeline': 300,
        },
        'TWISTED_REACTOR': 'twisted.internet.asyncioreactor.AsyncioSelectorReactor',
    }

    process = CrawlerProcess(settings)
    process.crawl(JobsBoardsSpider)

    print("\nStarting spider...")
    print("Will stop after 5 hiring signals or when all URLs scraped")
    print("-" * 70)

    process.start()

    print("\n" + "=" * 70)
    print("Spider finished")
    print("=" * 70)


if __name__ == '__main__':
    test_jobs_spider()

#!/usr/bin/env python3
"""
Run all ABBK LeadEngine spiders to populate the database.

Order:
1. Ministry of Industry (official government source)
2. Directories (annuaire.tn, pagesjaunes.tn, kompass.tn)
3. Job boards (emploi.tn, keejob.com)
"""
import sys
import os
from scrapy.crawler import CrawlerProcess
from scrapy.utils.log import configure_logging

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.scrapers.spiders.ministry_industry_spider import MinistryIndustrySpider
from app.scrapers.spiders.directories_spider import DirectoriesSpider
from app.scrapers.spiders.jobs_spider import JobsBoardsSpider
from app.scrapers import settings as scrapy_settings


def run_all_spiders():
    """Run all spiders sequentially."""

    # Load Scrapy settings
    settings_dict = {
        key: getattr(scrapy_settings, key)
        for key in dir(scrapy_settings)
        if key.isupper()
    }

    # Configure logging
    configure_logging(settings_dict)

    # Create crawler process
    process = CrawlerProcess(settings_dict)

    # Queue all spiders
    print("=" * 60)
    print("ABBK LeadEngine - Running All Spiders")
    print("=" * 60)

    print("\n1. Ministry of Industry Spider (tunisieindustrie.nat.tn)")
    print("   Official government database - highest priority")
    process.crawl(MinistryIndustrySpider)

    print("\n2. Directories Spider (annuaire.tn + pagesjaunes.tn + kompass.tn)")
    print("   Business directories across Tunisia")
    process.crawl(DirectoriesSpider)

    print("\n3. Job Boards Spider (emploi.tn + keejob.com)")
    print("   Hiring signals for engineering roles")
    process.crawl(JobsBoardsSpider)

    print("\n" + "=" * 60)
    print("Starting crawlers...")
    print("=" * 60 + "\n")

    # Start all crawlers
    process.start()

    print("\n" + "=" * 60)
    print("All spiders completed!")
    print("=" * 60)


if __name__ == '__main__':
    run_all_spiders()

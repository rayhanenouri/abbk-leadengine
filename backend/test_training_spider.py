#!/usr/bin/env python3
"""
Test script for training centers spider.

Runs the spider and shows detected training signals.
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from scrapy.crawler import CrawlerProcess
from app.scrapers.spiders.training_spider import TrainingCentersSpider
from app.scrapers import settings as scrapy_settings


def main():
    print("=" * 80)
    print("  ABBK LeadEngine — Training Centers Spider Test")
    print("=" * 80)
    print()
    print("Target sources:")
    print("  - ISET campuses (12 locations)")
    print("  - ATFP (Agence Tunisienne de la Formation Professionnelle)")
    print("  - Engineering schools (ENIM, ENIS, ENIT)")
    print("  - Professional training centers")
    print()
    print("Starting spider...")
    print("-" * 80)
    print()

    # Load settings
    settings_dict = {
        key: getattr(scrapy_settings, key)
        for key in dir(scrapy_settings)
        if key.isupper()
    }

    # Override some settings for testing
    settings_dict['LOG_LEVEL'] = 'INFO'
    settings_dict['CLOSESPIDER_PAGECOUNT'] = 50  # Limit for testing
    settings_dict['CONCURRENT_REQUESTS'] = 2  # Be extra polite to educational sites

    # Run spider
    process = CrawlerProcess(settings_dict)
    process.crawl(TrainingCentersSpider)
    process.start()

    print()
    print("=" * 80)
    print("  Spider completed!")
    print("=" * 80)
    print()
    print("Check database for training_detected signals:")
    print("  SELECT * FROM lead_signals WHERE signal_type = 'training_detected';")
    print()


if __name__ == '__main__':
    main()

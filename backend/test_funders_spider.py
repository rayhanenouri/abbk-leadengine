#!/usr/bin/env python3
"""
Test script for bailleurs de fonds (international funders) spider.

Runs the spider and shows detected funding signals.
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from scrapy.crawler import CrawlerProcess
from app.scrapers.spiders.funders_spider import FundersSpider
from app.scrapers import settings as scrapy_settings


def main():
    print("=" * 80)
    print("  ABBK LeadEngine — International Funders Spider Test")
    print("=" * 80)
    print()
    print("Target sources:")
    print("  - World Bank Tunisia projects")
    print("  - AFD (Agence Française de Développement)")
    print("  - EIB (European Investment Bank)")
    print("  - EU funding programs")
    print("  - USAID Tunisia")
    print("  - GIZ (German development)")
    print("  - African Development Bank")
    print()
    print("Why this matters:")
    print("  🔍 International funding = audit requirement")
    print("  🔍 Audits expose cracked software")
    print("  🔍 Companies MUST buy licenses = HIGH CONVERSION")
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
    settings_dict['CLOSESPIDER_PAGECOUNT'] = 30  # Limit for testing
    settings_dict['CONCURRENT_REQUESTS'] = 3

    # Run spider
    process = CrawlerProcess(settings_dict)
    process.crawl(FundersSpider)
    process.start()

    print()
    print("=" * 80)
    print("  Spider completed!")
    print("=" * 80)
    print()
    print("Check database for funding signals:")
    print("  SELECT * FROM lead_signals WHERE signal_type = 'funding';")
    print()
    print("Check leads with audit flags:")
    print("  SELECT * FROM leads WHERE under_audit = true;")
    print()


if __name__ == '__main__':
    main()

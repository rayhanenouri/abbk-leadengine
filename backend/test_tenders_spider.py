#!/usr/bin/env python3
"""
Test script for ministères and public tenders spider.

Runs the spider and shows detected tender signals.
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from scrapy.crawler import CrawlerProcess
from app.scrapers.spiders.tenders_spider import TendersSpider
from app.scrapers import settings as scrapy_settings


def main():
    print("=" * 80)
    print("  ABBK LeadEngine — Public Tenders Spider Test")
    print("=" * 80)
    print()
    print("Target sources:")
    print("  - TUNEPS (Tunisia National Electronic Procurement)")
    print("  - Ministry of Industry")
    print("  - Ministry of Equipment")
    print("  - HAICOP (Haute Instance de la Commande Publique)")
    print("  - Marchés Publics portal")
    print("  - JORT (Journal Officiel)")
    print()
    print("Why this matters:")
    print("  🔍 Public contracts = licensed software required")
    print("  🔍 Government audits check licenses")
    print("  🔍 Transparency law = compliance mandatory")
    print("  🔍 Multi-year contracts = stable revenue")
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
    settings_dict['CONCURRENT_REQUESTS'] = 2  # Be gentle with gov sites

    # Run spider
    process = CrawlerProcess(settings_dict)
    process.crawl(TendersSpider)
    process.start()

    print()
    print("=" * 80)
    print("  Spider completed!")
    print("=" * 80)
    print()
    print("Check database for tender signals:")
    print("  SELECT * FROM lead_signals WHERE signal_type = 'tender_detected';")
    print()
    print("Check leads with audit flags:")
    print("  SELECT * FROM leads WHERE under_audit = true;")
    print()


if __name__ == '__main__':
    main()

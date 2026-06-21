#!/usr/bin/env python3
"""
Test script for engineering events spider.

Runs the spider and shows detected event attendance signals.
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from scrapy.crawler import CrawlerProcess
from app.scrapers.spiders.events_spider import EventsSpider
from app.scrapers import settings as scrapy_settings


def main():
    print("=" * 80)
    print("  ABBK LeadEngine — Engineering Events Spider Test")
    print("=" * 80)
    print()
    print("Target sources:")
    print("  - SOLIDWORKS regional events")
    print("  - Tunisia engineering salons")
    print("  - UTICA industry events")
    print("  - CEPEX trade shows")
    print("  - University career fairs")
    print()
    print("Why this matters:")
    print("  📍 Event participants = actively engaged in engineering")
    print("  📍 SOLIDWORKS events = direct users/prospects")
    print("  📍 Industry salons = companies investing in growth")
    print("  📍 Exhibitors have budget")
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

    # Run spider
    process = CrawlerProcess(settings_dict)
    process.crawl(EventsSpider)
    process.start()

    print()
    print("=" * 80)
    print("  Spider completed!")
    print("=" * 80)
    print()
    print("Check database for event signals:")
    print("  SELECT * FROM lead_signals WHERE signal_type = 'event_attendance';")
    print()


if __name__ == '__main__':
    main()

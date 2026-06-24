#!/usr/bin/env python3
"""Standalone runner for BusinessNewsSpider."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scrapy.crawler import CrawlerProcess
from app.scrapers.spiders.news_spider import BusinessNewsSpider
from app.scrapers import settings as scrapy_settings

def main():
    settings_dict = {k: getattr(scrapy_settings, k) for k in dir(scrapy_settings) if k.isupper()}
    print("Starting BusinessNewsSpider...")
    process = CrawlerProcess(settings_dict)
    process.crawl(BusinessNewsSpider)
    process.start()
    print("BusinessNewsSpider completed!")

if __name__ == '__main__':
    main()

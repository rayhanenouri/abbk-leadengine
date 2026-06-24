#!/usr/bin/env python3
"""Standalone runner for LinkedIn companies spider."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scrapy.crawler import CrawlerProcess
from app.scrapers import settings as scrapy_settings

spider_classes = {
    'linkedin': 'LinkedInCompaniesSpider',
}

spider_name = 'linkedin'
class_name = spider_classes[spider_name]
module = __import__(f'app.scrapers.spiders.linkedin_companies_spider', fromlist=[class_name])
SpiderClass = getattr(module, class_name)

def main():
    settings_dict = {k: getattr(scrapy_settings, k) for k in dir(scrapy_settings) if k.isupper()}
    print(f"Starting {class_name}...")
    print("WARNING: LinkedIn heavily rate-limits scrapers.")
    print("For production, use Apify LinkedIn Company Scraper instead.")
    print("This spider only scrapes the 3 verified LinkedIn URLs.\n")

    process = CrawlerProcess(settings_dict)
    process.crawl(SpiderClass)
    process.start()
    print(f"{class_name} completed!")

if __name__ == '__main__':
    main()

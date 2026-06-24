#!/usr/bin/env python3
"""Standalone runner for events spider."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scrapy.crawler import CrawlerProcess
from app.scrapers import settings as scrapy_settings

# Import correct spider class
spider_classes = {
    'jobs': 'JobsBoardsSpider',
    'training': 'TrainingCentersSpider',
    'funders': 'FundersSpider',
    'tenders': 'TendersSpider',
    'events': 'EventsSpider'
}

spider_name = 'events'
class_name = spider_classes[spider_name]
module = __import__(f'app.scrapers.spiders.{spider_name}_spider', fromlist=[class_name])
SpiderClass = getattr(module, class_name)

def main():
    settings_dict = {k: getattr(scrapy_settings, k) for k in dir(scrapy_settings) if k.isupper()}
    print(f"Starting {class_name}...")
    process = CrawlerProcess(settings_dict)
    process.crawl(SpiderClass)
    process.start()
    print(f"{class_name} completed!")

if __name__ == '__main__':
    main()

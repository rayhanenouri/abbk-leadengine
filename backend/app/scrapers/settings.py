"""
Scrapy settings for ABBK LeadEngine scrapers.
"""

BOT_NAME = 'abbk_scraper'

SPIDER_MODULES = ['app.scrapers.spiders']
NEWSPIDER_MODULE = 'app.scrapers.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests
CONCURRENT_REQUESTS = 16

# Configure a delay for requests (in seconds)
DOWNLOAD_DELAY = 1

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Configure item pipelines
ITEM_PIPELINES = {
    'app.scrapers.pipelines.DatabasePipeline': 300,
}

# User-Agent
USER_AGENT = 'Mozilla/5.0 (compatible; ABBKLeadBot/1.0; +https://abbk-tn.com)'

# AutoThrottle settings
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 3
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0

# Enable and configure HTTP caching (optional)
HTTPCACHE_ENABLED = False

# Log level
LOG_LEVEL = 'INFO'

# Request fingerprinter implementation
REQUEST_FINGERPRINTER_IMPLEMENTATION = '2.7'

# Twisted reactor
TWISTED_REACTOR = 'twisted.internet.asyncioreactor.AsyncioSelectorReactor'

# Feed exports (optional - for debugging)
FEEDS = {
    'scraped_data.json': {
        'format': 'json',
        'encoding': 'utf8',
        'store_empty': False,
        'overwrite': True,
    },
}

"""
SPIDER: DIRECTORIES - VERIFIED WORKING SOURCES ONLY
Scrapes REAL Tunisia engineering company directories
"""

import scrapy
from datetime import datetime


class DirectoriesSpider(scrapy.Spider):
    name = 'directories'

    custom_settings = {
        'CONCURRENT_REQUESTS': 4,
        'DOWNLOAD_DELAY': 3,
    }

    # VERIFIED WORKING URLs from user
    start_urls = [
        # Tunisia Industry Portal - VERIFIED
        'https://www.tunisieindustrie.nat.tn/fr/dbi.asp',
        'https://www.tunisieindustrie.nat.tn/fr/dbs.asp',
        'https://www.tunisieindustrie.nat.tn/fr/certifdbi.asp?action=list&idsect=&pagenum=1',
        'https://www.tunisieindustrie.nat.tn/en/dbi.asp',
        'https://www.tunisieindustrie.nat.tn/en/etrangere.asp',

        # Professional Associations - VERIFIED
        'https://mecatronic.tn/membres/',
        'https://taa.tn/fr/membres',
        'https://www.cetime.tn/fr/annuaire-des-entreprises',

        # Other directories - VERIFIED
        'https://www.studi.com.tn/site/en/',
        'https://tn.kompass.com/en',
        'https://africabusinessbureau.com/',
        'https://www.aihitdata.com/search/companies?i=african+engineering',
    ]

    def parse(self, response):
        """Parse company listings"""

        # Extract all company names and links
        # Generic extraction - works for most directory sites

        # Method 1: Look for company links
        for link in response.css('a'):
            text = link.css('::text').get()
            href = link.css('::attr(href)').get()

            if text and len(text.strip()) > 3 and len(text.strip()) < 100:
                # Filter out navigation links
                if any(word in text.lower() for word in ['accueil', 'contact', 'about', 'login', 'register']):
                    continue

                yield {
                    'company_name': text.strip(),
                    'website': response.urljoin(href) if href else None,
                    'sector': 'Engineering',
                    'city': 'Tunis',
                    'country': 'Tunisia',
                    'source': response.url,
                    'found_at': datetime.now().isoformat()
                }

        # Method 2: Look for table rows (common in directories)
        for row in response.css('tr'):
            cells = row.css('td::text').getall()
            if cells and len(cells) > 0:
                company_name = cells[0].strip()
                if len(company_name) > 3:
                    yield {
                        'company_name': company_name,
                        'sector': 'Engineering',
                        'city': cells[1].strip() if len(cells) > 1 else 'Tunis',
                        'country': 'Tunisia',
                        'source': response.url,
                        'found_at': datetime.now().isoformat()
                    }

        # Method 3: Look for list items
        for item in response.css('li'):
            text = item.css('::text').get()
            if text and len(text.strip()) > 3 and len(text.strip()) < 100:
                yield {
                    'company_name': text.strip(),
                    'sector': 'Engineering',
                    'city': 'Tunis',
                    'country': 'Tunisia',
                    'source': response.url,
                    'found_at': datetime.now().isoformat()
                }

        # Follow pagination
        for next_page in response.css('a[href*="pagenum"], a[href*="page"], a.next::attr(href)').getall():
            yield response.follow(next_page, callback=self.parse)

"""
Spider 1: Tunisian business directories scraper.

Targets:
- annuaire.tn
- pagesjaunes.tn (Yellow Pages Tunisia)
- kompass.tn

Focus: industrial, engineering, manufacturing, construction sectors
Extracts: company name, website, sector, city, phone, size, description
"""
import scrapy
from typing import Dict, Any, Optional
import logging


class DirectoriesSpider(scrapy.Spider):
    """
    Scrapes Tunisian business directories for company data.

    Priority sectors:
    - Engineering / Bureau d'études
    - Manufacturing / Fabrication
    - Construction / BTP
    - Industrial / Industriel
    - Automotive / Automobile
    - Electronics / Electronique
    - Mechanical / Mécanique
    """

    name = "directories"

    # VERIFIED data sources - Tunisia business directories
    start_urls = [
        # Tunisia industry associations and directories
        "https://mecatronic.tn/membres/",  # Mecatronic industry members
        "https://taa.tn/fr/membres",  # Tunisian automotive association
        "https://www.cetime.tn/fr/annuaire-des-entreprises",  # CETIME directory
        "https://www.tunisieindustrie.nat.tn/fr/dbi.asp",  # Tunisia industry database
        "https://www.tunisieindustrie.nat.tn/fr/dbs.asp",  # Tunisia services database
        "https://www.tunisieindustrie.nat.tn/fr/certifdbi.asp?action=list&idsect=&pagenum=1",  # Certified companies
        "https://tn.kompass.com/en",  # Kompass Tunisia

        # Tunisia company lists
        "https://www.scribd.com/document/620128474/Liste-Entreprises",  # Enterprise list

        # Africa-wide directories
        "https://maps.prodafrica.com/",  # Production Africa map
        "https://africabusinessbureau.com/",  # African business bureau
        "https://www.success.ai/company-directory/Civil_Engineering/country/tunisia",  # Engineering companies
        "https://www.aihitdata.com/search/companies?i=african+engineering",  # African engineering
    ]

    custom_settings = {
        'ROBOTSTXT_OBEY': True,
        'CONCURRENT_REQUESTS': 8,
        'DOWNLOAD_DELAY': 1,  # Be respectful - 1 second delay
        'USER_AGENT': 'Mozilla/5.0 (compatible; ABBKLeadBot/1.0; +https://abbk-tn.com)',
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 3,
    }

    def parse(self, response):
        """
        Parse directory listing pages.
        Extract company cards and follow pagination.
        """
        # Extract company listings (adjust selectors based on actual site structure)
        companies = response.css('.company-item, .listing-item, .company-card, article.company')

        self.logger.info(f"Found {len(companies)} companies on {response.url}")

        for company in companies:
            yield self.parse_company(company, response.url)

        # Follow pagination
        next_page = response.css('a.next, .pagination a.next, a[rel="next"]::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_company(self, selector, source_url: str) -> Dict[str, Any]:
        """
        Extract company data from a listing card.
        """
        # Extract all possible fields
        company_name = self.extract_text(selector, [
            '.company-name::text',
            'h2::text',
            'h3::text',
            '.title::text',
            '.name::text'
        ])

        website = self.extract_text(selector, [
            'a.website::attr(href)',
            'a[href*="http"]::attr(href)',
            '.website::text',
            '.web::text'
        ])

        phone = self.extract_text(selector, [
            '.phone::text',
            '.tel::text',
            '.telephone::text',
            'a[href^="tel:"]::attr(href)',
            '.contact-phone::text'
        ])

        sector = self.extract_text(selector, [
            '.sector::text',
            '.category::text',
            '.industry::text',
            '.activity::text'
        ])

        city = self.extract_text(selector, [
            '.city::text',
            '.location::text',
            '.ville::text',
            '.address::text'
        ])

        description = self.extract_text(selector, [
            '.description::text',
            '.desc::text',
            'p::text'
        ])

        # Clean phone number
        if phone:
            phone = phone.replace('tel:', '').strip()

        # Clean website
        if website and not website.startswith('http'):
            if '@' not in website:  # Not an email
                website = f"https://{website}"

        # Skip if no company name
        if not company_name:
            return None

        return {
            'company_name': company_name.strip(),
            'website': website,
            'phone': phone,
            'sector': sector,
            'city': city,
            'description': description,
            'country': 'Tunisia',
            'source': 'annuaire.tn',
            'source_url': source_url,
        }

    def extract_text(self, selector, css_selectors: list) -> Optional[str]:
        """
        Try multiple CSS selectors and return the first non-empty result.
        """
        for css in css_selectors:
            result = selector.css(css).get()
            if result and result.strip():
                return result.strip()
        return None


class PagesJaunesSpider(scrapy.Spider):
    """
    Scrapes pagesjaunes.tn (Yellow Pages Tunisia).
    Similar structure to annuaire.tn but different selectors.
    """

    name = "pagesjaunes"

    start_urls = [
        "https://www.pagesjaunes.tn/entreprises/bureaux-d-etudes",
        "https://www.pagesjaunes.tn/entreprises/industrie",
        "https://www.pagesjaunes.tn/entreprises/construction",
    ]

    custom_settings = {
        'ROBOTSTXT_OBEY': True,
        'CONCURRENT_REQUESTS': 8,
        'DOWNLOAD_DELAY': 1,
        'USER_AGENT': 'Mozilla/5.0 (compatible; ABBKLeadBot/1.0; +https://abbk-tn.com)',
    }

    def parse(self, response):
        """Parse PagesJaunes listings."""
        # Will implement specific selectors after testing
        self.logger.info(f"Scraping {response.url}")

        # Placeholder - needs actual site inspection
        companies = response.css('.company, .business-item, .listing')

        for company in companies:
            name = company.css('.name::text, h2::text').get()
            if name:
                yield {
                    'company_name': name.strip(),
                    'source': 'pagesjaunes.tn',
                    'source_url': response.url,
                    'country': 'Tunisia',
                }


class KompassSpider(scrapy.Spider):
    """
    Scrapes kompass.tn (Kompass Tunisia business directory).
    International directory with detailed company profiles.
    """

    name = "kompass"

    start_urls = [
        "https://tn.kompass.com/a/engineering-offices-and-technical-consultancies/113/",
        "https://tn.kompass.com/a/industrial-equipment/205/",
    ]

    custom_settings = {
        'ROBOTSTXT_OBEY': True,
        'CONCURRENT_REQUESTS': 5,  # More conservative for international site
        'DOWNLOAD_DELAY': 2,
        'USER_AGENT': 'Mozilla/5.0 (compatible; ABBKLeadBot/1.0; +https://abbk-tn.com)',
    }

    def parse(self, response):
        """Parse Kompass listings."""
        self.logger.info(f"Scraping {response.url}")

        # Placeholder - Kompass has more structured data
        companies = response.css('.company-item, .product-item')

        for company in companies:
            name = company.css('.company-name::text, h3::text').get()
            if name:
                yield {
                    'company_name': name.strip(),
                    'source': 'kompass.tn',
                    'source_url': response.url,
                    'country': 'Tunisia',
                }

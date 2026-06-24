"""
Spider: LinkedIn Company Pages - SOLIDWORKS user groups and engineering companies.

VERIFIED LinkedIn company pages from client:
- SOLIDWORKS user groups in Africa
- Engineering companies in Tunisia and Africa
- Training providers

Creates company records with LinkedIn enrichment data.
Note: For full LinkedIn scraping use Apify LinkedIn Company Scraper (see backend/app/workers/tasks/apify_discover.py)
"""
import scrapy
from datetime import datetime
from typing import Dict, Any, Optional
import logging


class LinkedInCompaniesSpider(scrapy.Spider):
    """
    Scrapes verified LinkedIn company pages.

    Note: This is for direct LinkedIn URLs provided by client.
    For broader LinkedIn discovery, use Apify integration instead.
    """

    name = "linkedin_companies"

    # VERIFIED LinkedIn company pages
    start_urls = [
        # SOLIDWORKS user groups - Africa
        "https://www.linkedin.com/company/lagos-swug/",  # Lagos SOLIDWORKS User Group
        "https://community.swugn.org/tanzania-solidworks-user-group/",  # Tanzania SWUG

        # Engineering companies
        "https://www.linkedin.com/company/m-c-engineering1/",  # M-C Engineering
    ]

    custom_settings = {
        'ROBOTSTXT_OBEY': True,
        'CONCURRENT_REQUESTS': 2,  # Very conservative for LinkedIn
        'DOWNLOAD_DELAY': 5,  # Respectful 5 second delay
        'USER_AGENT': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 5,
        'AUTOTHROTTLE_MAX_DELAY': 15,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,
        'DOWNLOAD_TIMEOUT': 30,
        'COOKIES_ENABLED': False,  # Avoid LinkedIn tracking
    }

    def parse(self, response):
        """
        Parse LinkedIn company page.

        WARNING: LinkedIn heavily rate-limits and blocks scrapers.
        For production, use Apify LinkedIn Company Scraper instead.
        This spider is only for the specific verified URLs.
        """
        self.logger.info(f"Parsing LinkedIn page: {response.url}")

        # LinkedIn requires authentication for most data
        # This spider can only extract publicly visible info

        # Check if we hit a login wall
        if 'authwall' in response.url or 'login' in response.url:
            self.logger.warning(f"LinkedIn login wall detected for {response.url}")
            self.logger.warning("For full LinkedIn scraping, use Apify LinkedIn Company Scraper")
            return

        # Try to extract basic company info from public page
        company_name = self.extract_text(response, [
            'h1.top-card-layout__title::text',
            'h1::text',
            '.org-top-card-summary__title::text',
        ])

        description = self.extract_text(response, [
            '.org-top-card-summary__tagline::text',
            'p.break-words::text',
        ])

        industry = self.extract_text(response, [
            '.org-top-card-summary-info-list__info-item::text',
        ])

        website = response.css('a[data-tracking-control-name="about_website"]::attr(href)').get()

        if company_name:
            yield {
                'company_name': company_name.strip(),
                'description': description.strip() if description else None,
                'industry': industry.strip() if industry else None,
                'website': website,
                'linkedin_url': response.url,
                'source': 'LinkedIn (verified URL)',
                'source_url': response.url,
                'country': self._detect_country_from_url(response.url),
            }
        else:
            self.logger.warning(f"Could not extract company name from {response.url}")
            self.logger.warning("LinkedIn may require authentication or Apify scraper")

    def _detect_country_from_url(self, url: str) -> str:
        """Detect country from LinkedIn URL or company name."""
        if 'lagos' in url.lower() or 'nigeria' in url.lower():
            return 'Nigeria'
        elif 'tanzania' in url.lower():
            return 'Tanzania'
        elif 'tunisia' in url.lower() or 'tunis' in url.lower():
            return 'Tunisia'
        elif 'south-africa' in url.lower() or 'za' in url.lower():
            return 'South Africa'
        else:
            return 'Africa'  # Default for unknown African companies

    def extract_text(self, response, css_selectors: list) -> Optional[str]:
        """Try multiple CSS selectors and return first non-empty result."""
        for css in css_selectors:
            result = response.css(css).get()
            if result and result.strip():
                return result.strip()
        return None

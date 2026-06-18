"""
Spider: Tunisian Ministry of Industry Database (tunisieindustrie.nat.tn)

HIGH PRIORITY - Official government database of all Tunisian industrial companies.
This is the most authoritative source for company data in Tunisia.

Extracts:
- Company name, sector, activity
- Official registration data
- Contact information
- Location details
"""
import scrapy
from typing import Dict, Any, Optional
import logging


class MinistryIndustrySpider(scrapy.Spider):
    """
    Scrapes tunisieindustrie.nat.tn - Official Ministry of Industry database.

    This is the authoritative government source for all industrial companies in Tunisia.
    Highest priority data source requested by ABBK manager.
    """

    name = "ministry_industry"

    start_urls = [
        # Main company directory - will need to be adjusted based on actual site structure
        "https://www.tunisieindustrie.nat.tn/fr/",
        "https://www.tunisieindustrie.nat.tn/fr/annuaire.asp",
    ]

    # Focus sectors for SOLIDWORKS potential
    PRIORITY_SECTORS = [
        'mecanique',
        'mécanique',
        'metallurgie',
        'métallurgie',
        'electrique',
        'électrique',
        'electronique',
        'électronique',
        'automobile',
        'aeronautique',
        'aéronautique',
        'construction',
        'btp',
        'industriel',
        'fabrication',
        'manufacture',
    ]

    custom_settings = {
        'ROBOTSTXT_OBEY': True,
        'CONCURRENT_REQUESTS': 3,  # Conservative for government site
        'DOWNLOAD_DELAY': 3,  # Very respectful - 3 second delay
        'USER_AGENT': 'Mozilla/5.0 (compatible; ABBKLeadBot/1.0; +https://abbk-tn.com)',
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 3,
        'AUTOTHROTTLE_MAX_DELAY': 10,
    }

    def parse(self, response):
        """
        Parse ministry directory pages.

        Note: This will need to be adjusted based on the actual site structure.
        Government sites often have unique layouts.
        """
        self.logger.info(f"Parsing Ministry of Industry page: {response.url}")

        # Look for company listings - try multiple possible selectors
        companies = response.css(
            '.company-item, .entreprise, .liste-entreprise > div, '
            'table.companies tr, .annuaire-item, article.company'
        )

        if not companies:
            # If no standard selectors work, log the page structure for debugging
            self.logger.warning(f"No companies found on {response.url}")
            self.logger.debug(f"Page title: {response.css('title::text').get()}")

        for company in companies:
            company_data = self.parse_company(company, response.url)
            if company_data:
                yield company_data

        # Look for pagination or category links
        category_links = response.css(
            'a[href*="secteur"], a[href*="category"], '
            'a[href*="activite"], .category a::attr(href)'
        ).getall()

        for link in category_links[:20]:  # Limit to avoid too many requests
            yield response.follow(link, callback=self.parse)

        # Pagination
        next_page = response.css(
            'a.next::attr(href), a[rel="next"]::attr(href), '
            '.pagination a.next::attr(href)'
        ).get()

        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_company(self, selector, source_url: str) -> Optional[Dict[str, Any]]:
        """Extract company data from a listing."""

        # Company name - try multiple selectors
        company_name = self.extract_text(selector, [
            '.company-name::text',
            'h2::text',
            'h3::text',
            '.nom-entreprise::text',
            '.raison-sociale::text',
            'td.name::text',
            '.title::text'
        ])

        if not company_name:
            return None

        # Sector/Activity
        sector = self.extract_text(selector, [
            '.sector::text',
            '.secteur::text',
            '.activity::text',
            '.activite::text',
            'td.secteur::text',
            '.domaine::text'
        ])

        # Location
        city = self.extract_text(selector, [
            '.city::text',
            '.ville::text',
            '.location::text',
            '.localisation::text',
            'td.ville::text',
            '.address::text'
        ])

        # Contact info
        phone = self.extract_text(selector, [
            '.phone::text',
            '.tel::text',
            '.telephone::text',
            'td.phone::text',
            'a[href^="tel:"]::attr(href)'
        ])

        website = self.extract_text(selector, [
            '.website::text',
            'a.website::attr(href)',
            'a[href^="http"]::attr(href)',
            'td.web::text'
        ])

        # Description/Activity detail
        description = self.extract_text(selector, [
            '.description::text',
            '.detail::text',
            'p::text',
            '.activite-detail::text'
        ])

        # Only return if it's a priority sector or if we have good data
        if sector and self._is_priority_sector(sector):
            return {
                'company_name': company_name.strip(),
                'website': website,
                'phone': phone,
                'sector': sector,
                'city': city,
                'description': description,
                'country': 'Tunisia',
                'source': 'tunisieindustrie.nat.tn',
                'source_url': source_url,
                'is_official_government_source': True,  # Flag for high priority
            }

        # Return all companies if no sector filter (we can filter in pipeline)
        return {
            'company_name': company_name.strip(),
            'website': website,
            'phone': phone,
            'sector': sector,
            'city': city,
            'description': description,
            'country': 'Tunisia',
            'source': 'tunisieindustrie.nat.tn',
            'source_url': source_url,
            'is_official_government_source': True,
        }

    def _is_priority_sector(self, sector: str) -> bool:
        """Check if sector is a priority for SOLIDWORKS."""
        if not sector:
            return False

        sector_lower = sector.lower()
        return any(keyword in sector_lower for keyword in self.PRIORITY_SECTORS)

    def extract_text(self, selector, css_selectors: list) -> Optional[str]:
        """Try multiple CSS selectors and return first non-empty result."""
        for css in css_selectors:
            result = selector.css(css).get()
            if result and result.strip():
                # Clean up phone numbers
                if 'tel:' in result:
                    result = result.replace('tel:', '')
                return result.strip()
        return None

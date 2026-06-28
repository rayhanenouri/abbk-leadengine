"""
FIXED DIRECTORIES SPIDER - REAL COMPANIES ONLY

Extracts ONLY actual company names from verified directories.
NO navigation menus, NO page titles, NO junk.

Uses specific CSS selectors per directory to get REAL data.
"""

import scrapy
from datetime import datetime
import re


class DirectoriesSpiderFixed(scrapy.Spider):
    name = 'directories'

    custom_settings = {
        'CONCURRENT_REQUESTS': 2,
        'DOWNLOAD_DELAY': 3,
        'HTTPCACHE_ENABLED': True,
    }

    # Junk patterns to ALWAYS skip
    JUNK_PATTERNS = [
        # Navigation
        'accueil', 'home', 'contact', 'about', 'login', 'register', 'recherche',
        'search', 'filter', 'annuaire', 'directory', 'liste', 'page',
        # Common words
        'secteur', 'gouvernorat', 'cluster', 'réseau', 'network', 'membre', 'member',
        'adhérent', 'partenaire', 'actualité', 'news', 'event', 'formation',
        # Technical
        'http', 'www', 'pdf', 'jpg', 'png', 'javascript', 'css',
        # Short words
        'le', 'la', 'les', 'de', 'du', 'des', 'en', 'et', 'ou', 'a', 'à',
    ]

    # Company name validation patterns
    COMPANY_INDICATORS = [
        r'\bS\.?A\.?R\.?L\.?\b',  # SARL
        r'\bS\.?A\.?\b',  # SA
        r'\bLtd\.?\b',  # Ltd
        r'\bL\.?L\.?C\.?\b',  # LLC
        r'\bGmbH\b',  # GmbH
        r'\bTunisia\b',
        r'\bTunisie\b',
    ]

    start_urls = [
        # TAA - Automotive cluster (REAL automotive companies)
        'https://taa.tn/fr/membres',

        # CETIME - Engineering center directory
        'https://www.cetime.tn/fr/annuaire-des-entreprises',

        # Mecatronic - Mechatronics cluster
        'https://mecatronic.tn/membres/',
    ]

    def is_valid_company_name(self, name):
        """
        Validate if a name is a REAL company name.
        Returns True only for actual companies.
        """
        if not name or len(name) < 4 or len(name) > 150:
            return False

        name_lower = name.lower()

        # Skip if contains junk patterns
        for pattern in self.JUNK_PATTERNS:
            if pattern in name_lower:
                return False

        # Skip if it's just numbers or special chars
        if re.match(r'^[\d\s\-_\.]+$', name):
            return False

        # Skip if starts with common non-company words
        if name_lower.startswith(('notre', 'nos', 'les', 'le', 'la', 'des', 'voir', 'consulter', 'plus')):
            return False

        # GOOD SIGNS: Contains company indicators
        has_indicator = any(re.search(pattern, name, re.IGNORECASE) for pattern in self.COMPANY_INDICATORS)

        # GOOD SIGNS: Has capital letters in middle (company names are often TitleCase or UPPERCASE)
        has_capitals = bool(re.search(r'[A-Z]{2,}', name))

        # GOOD SIGNS: Contains numbers (like "3M", "A380", etc.)
        has_numbers_with_letters = bool(re.search(r'[A-Z]+\d+|\d+[A-Z]+', name))

        # Must have at least ONE good sign
        if has_indicator or has_capitals or has_numbers_with_letters:
            return True

        # Or: length > 15 characters and contains spaces (likely a real company name)
        if len(name) > 15 and ' ' in name and not name.lower().startswith(tuple(self.JUNK_PATTERNS)):
            return True

        return False

    def parse(self, response):
        """Parse directory pages with STRICT validation"""

        if 'taa.tn' in response.url:
            yield from self.parse_taa(response)
        elif 'cetime.tn' in response.url:
            yield from self.parse_cetime(response)
        elif 'mecatronic.tn' in response.url:
            yield from self.parse_mecatronic(response)
        else:
            yield from self.parse_generic(response)

    def parse_taa(self, response):
        """Parse TAA automotive cluster members"""
        self.logger.info("Parsing TAA members page")

        # TAA has company links in specific structure
        # Look for actual company profile links
        for company_link in response.css('div.view-content a'):
            company_name = company_link.css('::text').get()
            href = company_link.css('::attr(href)').get()

            if company_name and self.is_valid_company_name(company_name):
                yield {
                    'company_name': company_name.strip(),
                    'website': response.urljoin(href),
                    'sector': 'Automotive',
                    'country': 'Tunisia',
                    'source': 'taa.tn',
                    'source_url': response.url
                }

    def parse_cetime(self, response):
        """Parse CETIME engineering directory"""
        self.logger.info("Parsing CETIME directory")

        # CETIME lists companies in table format
        for row in response.css('table tr'):
            cells = row.css('td')
            if len(cells) >= 2:
                # First cell usually has company name
                company_name = cells[0].css('::text').get()

                if company_name and self.is_valid_company_name(company_name):
                    # Try to get city from second cell
                    city = cells[1].css('::text').get()

                    yield {
                        'company_name': company_name.strip(),
                        'sector': 'Engineering',
                        'city': city.strip() if city else 'Tunis',
                        'country': 'Tunisia',
                        'source': 'cetime.tn',
                        'source_url': response.url
                    }

    def parse_mecatronic(self, response):
        """Parse Mecatronic cluster members"""
        self.logger.info("Parsing Mecatronic members")

        # Mecatronic has member cards or list items
        for member in response.css('div.member, li.company'):
            company_name = member.css('h3::text, h4::text, strong::text').get()

            if company_name and self.is_valid_company_name(company_name):
                yield {
                    'company_name': company_name.strip(),
                    'sector': 'Engineering',
                    'country': 'Tunisia',
                    'source': 'mecatronic.tn',
                    'source_url': response.url
                }

    def parse_generic(self, response):
        """
        Generic parser with VERY strict validation.
        Only use this for unknown directory structures.
        """
        self.logger.info(f"Parsing generic directory: {response.url}")

        # Look for company names in common places with strict validation
        candidates = []

        # Tables (common in directories)
        for row in response.css('table tr'):
            cells = row.css('td::text').getall()
            if cells:
                for cell in cells[:3]:  # Only first 3 columns
                    if cell and self.is_valid_company_name(cell.strip()):
                        candidates.append(cell.strip())

        # Lists with specific classes that indicate company lists
        for item in response.css('ul.companies li, ul.members li, div.company-list div'):
            text = item.css('::text').get()
            if text and self.is_valid_company_name(text.strip()):
                candidates.append(text.strip())

        # Yield unique valid companies
        seen = set()
        for company_name in candidates:
            if company_name not in seen:
                seen.add(company_name)
                yield {
                    'company_name': company_name,
                    'sector': 'Engineering',
                    'country': 'Tunisia',
                    'source': 'directory',
                    'source_url': response.url
                }

                # Log what we're collecting (for debugging)
                self.logger.info(f"✅ Valid company: {company_name}")


    def parse_item(self, item):
        """Final validation before yielding item"""
        if 'company_name' in item:
            # One final check
            if self.is_valid_company_name(item['company_name']):
                return item
        return None

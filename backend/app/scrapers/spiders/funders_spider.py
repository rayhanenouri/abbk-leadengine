"""
Spider 5: Bailleurs de fonds (International funders) funded projects.

Targets:
- Banque Mondiale (World Bank) Tunisia projects
- AFD (Agence Française de Développement)
- BEI (Banque Européenne d'Investissement)
- EU funding programs (Tunisia)
- USAID Tunisia
- GIZ (Deutsche Gesellschaft für Internationale Zusammenarbeit)

Focus: Companies receiving international funding = MUST use licensed software (audit requirement)
Creates LeadSignal with signal_type=funding
Sets under_audit=true flag on lead
"""
import scrapy
from datetime import datetime
from typing import Dict, Any, Optional
import logging
import re


class FundersSpider(scrapy.Spider):
    """
    Scrapes international funding organization websites for funded Tunisian companies.

    Why this matters for ABBK:
    1. Internationally funded projects require audits
    2. Audits expose cracked software usage
    3. Companies MUST buy licenses to pass audit
    4. These are HIGH CONVERSION leads

    Detection strategy:
    - Project databases listing beneficiary companies
    - Funding announcements with company names
    - Project reports mentioning Tunisian partners
    - Grant recipient lists
    """

    name = "funders"

    # Funding keywords
    FUNDING_KEYWORDS = [
        'financement', 'financing', 'funded', 'financé',
        'grant', 'subvention', 'don',
        'loan', 'prêt', 'crédit',
        'investment', 'investissement',
        'project', 'projet',
        'beneficiary', 'bénéficiaire',
        'recipient', 'attributaire',
    ]

    # Audit keywords (triggers under_audit flag)
    AUDIT_KEYWORDS = [
        'audit', 'audité',
        'compliance', 'conformité',
        'certification',
        'inspection',
        'vérification', 'verification',
        'controle', 'contrôle',
        'due diligence',
    ]

    start_urls = [
        # World Bank Tunisia Projects
        "https://projects.worldbank.org/en/projects-operations/projects-list?countrycode_exact=TN",
        "https://www.banquemondiale.org/fr/country/tunisia/projects",

        # AFD - Agence Française de Développement
        "https://www.afd.fr/fr/page-region-pays/tunisie",
        "https://www.afd.fr/fr/rechercher?query=tunisie&type=project",

        # European Investment Bank (BEI/EIB)
        "https://www.eib.org/en/projects/regions/african-caribbean-pacific-and-overseas-countries-and-territories/tunisia",

        # EU Funding - European Commission Tunisia
        "https://neighbourhood-enlargement.ec.europa.eu/european-neighbourhood-policy/countries-region/tunisia_en",
        "https://ec.europa.eu/neighbourhood-enlargement/tunisia_en",

        # USAID Tunisia
        "https://www.usaid.gov/tunisia",
        "https://www.usaid.gov/tunisia/our-work",

        # GIZ Tunisia
        "https://www.giz.de/en/worldwide/327.html",  # Tunisia country page

        # African Development Bank Tunisia
        "https://www.afdb.org/en/countries/north-africa/tunisia",
        "https://www.afdb.org/en/countries/north-africa/tunisia/tunisia-projects",

        # UNDP Tunisia
        "https://www.tn.undp.org/content/tunisia/fr/home/projects.html",

        # Tunisian Government - Ministry of Development
        "http://www.mdci.gov.tn/en/",  # May list funded projects
    ]

    custom_settings = {
        'ROBOTSTXT_OBEY': True,
        'CONCURRENT_REQUESTS': 4,
        'DOWNLOAD_DELAY': 2,
        'USER_AGENT': 'Mozilla/5.0 (compatible; ABBKLeadBot/1.0; +https://abbk-tn.com)',
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 2,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 2.0,
        'DOWNLOAD_TIMEOUT': 30,
        'RETRY_ENABLED': True,
        'RETRY_TIMES': 3,
    }

    def parse(self, response):
        """Parse funding organization pages for project listings."""
        self.logger.info(f"Parsing funder page: {response.url}")

        # Detect which organization
        if 'worldbank.org' in response.url or 'banquemondiale.org' in response.url:
            yield from self.parse_world_bank(response)
        elif 'afd.fr' in response.url:
            yield from self.parse_afd(response)
        elif 'eib.org' in response.url:
            yield from self.parse_eib(response)
        elif 'usaid.gov' in response.url:
            yield from self.parse_usaid(response)
        elif 'giz.de' in response.url:
            yield from self.parse_giz(response)
        elif 'afdb.org' in response.url:
            yield from self.parse_afdb(response)
        else:
            # Generic parsing for other sources
            yield from self.parse_generic(response)

    def parse_world_bank(self, response):
        """Parse World Bank project pages."""
        # World Bank project listings
        projects = response.css('.project-item, .project-card, article.project')

        for project in projects:
            project_title = self.extract_text(project, [
                'h2::text', 'h3::text', '.title::text', '.project-title::text'
            ])

            project_description = ' '.join(project.css('p::text, .description::text').getall())

            # Extract company names from project description
            companies = self._extract_companies_from_text(project_description)

            for company_name in companies:
                funder_info = self._detect_funder_and_amount(response, project_description)

                yield {
                    'signal_type': 'funding',
                    'company_name': company_name,
                    'funder': funder_info['funder'],
                    'amount': funder_info['amount'],
                    'project_title': project_title,
                    'source': 'World Bank',
                    'source_url': response.url,
                    'title': f"World Bank funding: {project_title[:100] if project_title else 'Project'}",
                    'detail': f"Received {funder_info['funder']} funding for {project_title if project_title else 'international project'}",
                    'has_audit_requirement': self._has_audit_language(project_description),
                }

        # Follow project links
        for href in response.css('a[href*="project"]::attr(href)').getall():
            if href and 'tunisia' in href.lower():
                yield response.follow(href, callback=self.parse_world_bank)

    def parse_afd(self, response):
        """Parse AFD (Agence Française de Développement) pages."""
        # AFD project cards
        projects = response.css('.project, .card-project, article')

        for project in projects:
            title = self.extract_text(project, [
                'h2 a::text', 'h3::text', '.title::text'
            ])

            description = ' '.join(project.css('p::text, .description::text').getall())

            companies = self._extract_companies_from_text(description)

            for company_name in companies:
                funder_info = self._detect_funder_and_amount(response, description)

                yield {
                    'signal_type': 'funding',
                    'company_name': company_name,
                    'funder': funder_info['funder'],
                    'amount': funder_info['amount'],
                    'project_title': title,
                    'source': 'AFD',
                    'source_url': response.url,
                    'title': f"AFD funding: {title[:100] if title else 'Project'}",
                    'detail': f"Received AFD (French Development Agency) funding for {title if title else 'development project'}",
                    'has_audit_requirement': True,  # AFD always requires audits
                }

        # Pagination
        next_page = response.css('a.next::attr(href), .pagination a[rel="next"]::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse_afd)

    def parse_eib(self, response):
        """Parse European Investment Bank pages."""
        projects = response.css('.project, .project-item, article')

        for project in projects:
            title = self.extract_text(project, [
                'h2::text', 'h3::text', '.title::text'
            ])

            description = ' '.join(project.css('p::text, .description::text').getall())

            companies = self._extract_companies_from_text(description)

            for company_name in companies:
                funder_info = self._detect_funder_and_amount(response, description)

                yield {
                    'signal_type': 'funding',
                    'company_name': company_name,
                    'funder': funder_info['funder'],
                    'amount': funder_info['amount'],
                    'project_title': title,
                    'source': 'EIB',
                    'source_url': response.url,
                    'title': f"EIB funding: {title[:100] if title else 'Project'}",
                    'detail': f"Received European Investment Bank funding for {title if title else 'infrastructure project'}",
                    'has_audit_requirement': True,  # EU funding always audited
                }

    def parse_usaid(self, response):
        """Parse USAID Tunisia pages."""
        # USAID partner organizations and projects
        partners = response.css('.partner, .organization, .implementer')

        for partner in partners:
            company_name = self.extract_text(partner, [
                'h3::text', '.name::text', 'strong::text'
            ])

            if company_name and self._looks_like_company(company_name):
                description = ' '.join(partner.css('p::text').getall())
                funder_info = self._detect_funder_and_amount(response, description)

                yield {
                    'signal_type': 'funding',
                    'company_name': company_name,
                    'funder': funder_info['funder'],
                    'amount': funder_info['amount'],
                    'source': 'USAID',
                    'source_url': response.url,
                    'title': 'USAID implementing partner',
                    'detail': f'Listed as USAID implementing partner in Tunisia',
                    'has_audit_requirement': True,  # USAID requires strict audits
                }

        # Generic text scanning for company mentions
        yield from self.parse_generic(response)

    def parse_giz(self, response):
        """Parse GIZ (German development cooperation) pages."""
        yield from self.parse_generic(response)

    def parse_afdb(self, response):
        """Parse African Development Bank pages."""
        yield from self.parse_generic(response)

    def parse_generic(self, response):
        """Generic parser for any funding page."""
        # Extract all text and look for company names in context of funding
        page_text = ' '.join(response.css('body ::text').getall())

        # Look for sections about projects, beneficiaries, partners
        project_sections = response.css(
            'section:contains("project"), '
            'section:contains("beneficiary"), '
            'section:contains("partner"), '
            'div.projects, '
            'div.beneficiaries, '
            '.project-list'
        )

        for section in project_sections:
            section_text = ' '.join(section.css('::text').getall())

            # Check if this section talks about funding
            if any(kw in section_text.lower() for kw in self.FUNDING_KEYWORDS):
                companies = self._extract_companies_from_text(section_text)

                for company_name in companies:
                    funder_info = self._detect_funder_and_amount(response, section_text)

                    yield {
                        'signal_type': 'funding',
                        'company_name': company_name,
                        'funder': funder_info['funder'],
                        'amount': funder_info['amount'],
                        'source': self._get_source_name(response.url),
                        'source_url': response.url,
                        'title': f"{funder_info['funder']} funding detected",
                        'detail': f"Mentioned in {self._get_source_name(response.url)} funded projects",
                        'has_audit_requirement': self._has_audit_language(section_text),
                    }

    def _extract_companies_from_text(self, text: str) -> list:
        """
        Extract company names from project descriptions.

        Looks for:
        - Capitalized multi-word phrases
        - Company suffixes (SARL, SA, Group, etc.)
        - Known Tunisian company patterns
        """
        if not text:
            return []

        companies = []

        # Pattern 1: Text after "company", "enterprise", "entreprise", "société"
        patterns = [
            r'(?:company|enterprise|entreprise|société|firm|organisation)\s+([A-Z][A-Za-z\s&-]{3,50})',
            r'([A-Z][A-Za-z\s&-]{3,50})\s+(?:SARL|SA|SAS|Group|Groupe|Industries|Engineering)',
            r'(?:by|avec|with|partner)\s+([A-Z][A-Za-z\s&-]{3,40})',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                match = match.strip()
                if self._looks_like_company(match):
                    companies.append(match)

        # Pattern 2: Strong/bold text (often company names in reports)
        # This would need HTML parsing, already handled in parse methods

        return list(set(companies))  # Deduplicate

    def _looks_like_company(self, text: str) -> bool:
        """Check if text looks like a company name."""
        if not text or len(text) < 3:
            return False

        text_lower = text.lower().strip()

        # Exclude common non-company words
        excluded = [
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'with', 'by', 'from', 'about', 'tunisia', 'tunisian', 'project',
            'program', 'programme', 'development', 'funding', 'grant',
            'government', 'ministry', 'ministère', 'national', 'international',
            'world bank', 'african', 'european', 'french', 'german', 'american',
        ]

        if text_lower in excluded:
            return False

        # Must have at least one capital letter (company names are capitalized)
        if not any(c.isupper() for c in text):
            return False

        # Company name indicators
        company_indicators = [
            'group', 'groupe', 'sarl', 'sa', 'sas', 'industries', 'engineering',
            'technology', 'technologies', 'services', 'solutions', 'systems',
            'construction', 'manufacturing', 'production', 'textile', 'chemical',
            'pharmaceuticals', 'holding', 'international', 'tunisia', 'tunisie'
        ]

        if any(indicator in text_lower for indicator in company_indicators):
            return True

        # If it has 2+ words and starts with capital, likely a company
        words = text.split()
        if len(words) >= 2 and words[0][0].isupper():
            return True

        return False

    def _detect_funder_and_amount(self, response, text: str) -> dict:
        """Extract funder name and funding amount from text."""
        funder = self._get_source_name(response.url)
        amount = None

        # Try to extract funding amount
        # Patterns: $X million, €X million, X M€, X M$, etc.
        amount_patterns = [
            r'[\$€]\s*(\d+(?:\.\d+)?)\s*(?:million|M|mn)',
            r'(\d+(?:\.\d+)?)\s*(?:million|M|mn)\s*[\$€]',
            r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:USD|EUR|TND)',
        ]

        for pattern in amount_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount = match.group(1).replace(',', '') + ' million'
                break

        return {
            'funder': funder,
            'amount': amount
        }

    def _has_audit_language(self, text: str) -> bool:
        """Check if text contains audit-related keywords."""
        if not text:
            return False

        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.AUDIT_KEYWORDS)

    def _get_source_name(self, url: str) -> str:
        """Extract readable source name from URL."""
        if 'worldbank.org' in url or 'banquemondiale.org' in url:
            return "World Bank"
        elif 'afd.fr' in url:
            return "AFD"
        elif 'eib.org' in url:
            return "EIB"
        elif 'usaid.gov' in url:
            return "USAID"
        elif 'giz.de' in url:
            return "GIZ"
        elif 'afdb.org' in url:
            return "African Development Bank"
        elif 'undp.org' in url:
            return "UNDP"
        elif 'europa.eu' in url or 'ec.europa.eu' in url:
            return "European Union"
        else:
            # Extract domain
            match = re.search(r'https?://(?:www\.)?([^/]+)', url)
            return match.group(1) if match else url

    def extract_text(self, selector, css_selectors: list) -> Optional[str]:
        """Try multiple CSS selectors and return first non-empty result."""
        for css in css_selectors:
            result = selector.css(css).get()
            if result and result.strip():
                return result.strip()
        return None

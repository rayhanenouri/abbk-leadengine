"""
Spider 6: Ministères and public sector tenders.

Targets:
- TUNEPS (Tunisian public procurement platform)
- Ministry websites tender announcements
- Public sector marchés publics databases
- Government engineering contracts

Focus: Companies winning public tenders = MUST use licensed software (audit + transparency)
Creates LeadSignal with signal_type=tender_detected
Sets under_audit=true flag on lead
"""
import scrapy
from datetime import datetime
from typing import Dict, Any, Optional
import logging
import re


class TendersSpider(scrapy.Spider):
    """
    Scrapes public tender platforms for engineering/design contract winners.

    Why this matters for ABBK:
    1. Public contracts require licensed software (transparency law)
    2. Government audits check software licenses
    3. Public procurement = compliance mandatory
    4. Engineering/design tenders = likely SOLIDWORKS users
    5. Multi-year contracts = stable revenue

    Detection strategy:
    - TUNEPS tender awards and winners
    - Ministry tender announcements
    - Public project beneficiaries
    - Engineering/design contract winners
    """

    name = "tenders"

    # Tender keywords indicating engineering/design work
    TENDER_KEYWORDS = [
        'conception', 'design',
        'etude', 'étude', 'study',
        'bureau d etudes', "bureau d'études",
        'ingenierie', 'ingénierie', 'engineering',
        'projet', 'project',
        'infrastructure',
        'construction',
        'cao', 'cad', 'solidworks',
        'plans', 'drawing', 'dessin',
        'technique', 'technical',
        'maitrise d oeuvre', "maîtrise d'œuvre",
        'architecture',
    ]

    # Contract types that require engineering software
    ENGINEERING_CONTRACT_TYPES = [
        'étude technique',
        'bureau d études',
        'conception',
        'maîtrise d oeuvre',
        'infrastructure',
        'génie civil',
        'architecture',
        'ingénierie',
    ]

    start_urls = [
        # TUNEPS - Tunisia National Electronic Procurement System
        "http://www.tuneps.tn",
        "http://www.tuneps.tn/avis",
        "http://www.tuneps.tn/resultats",

        # Ministère de l'Industrie
        "http://www.industrie.gov.tn/appels-doffres",
        "http://www.industrie.gov.tn/marches-publics",

        # Ministère de l'Équipement
        "http://www.equipement.tn/appels-offres",
        "http://www.equipement.tn/marches",

        # Ministère du Développement et de la Coopération Internationale
        "http://www.mdci.gov.tn/marches-publics",

        # Haute Instance de la Commande Publique
        "http://www.haicop.tn/marches-publics",
        "http://www.haicop.tn/resultats",

        # JORT - Journal Officiel de la République Tunisienne
        "http://www.iort.gov.tn/marches-publics",

        # Marchés Publics Tunisia portal
        "https://marchespublics.gov.tn",
        "https://marchespublics.gov.tn/consulter/resultats",
    ]

    custom_settings = {
        'ROBOTSTXT_OBEY': True,
        'CONCURRENT_REQUESTS': 3,
        'DOWNLOAD_DELAY': 3,  # Respectful - government sites can be slow
        'USER_AGENT': 'Mozilla/5.0 (compatible; ABBKLeadBot/1.0; +https://abbk-tn.com)',
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 3,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 2.0,
        'DOWNLOAD_TIMEOUT': 45,  # Government sites can be very slow
        'RETRY_ENABLED': True,
        'RETRY_TIMES': 3,
    }

    def parse(self, response):
        """Parse tender platform pages for contract awards."""
        self.logger.info(f"Parsing tender page: {response.url}")

        # Detect which platform
        if 'tuneps' in response.url:
            yield from self.parse_tuneps(response)
        elif 'industrie.gov.tn' in response.url:
            yield from self.parse_ministry_industry(response)
        elif 'equipement.tn' in response.url:
            yield from self.parse_ministry_equipment(response)
        elif 'haicop.tn' in response.url:
            yield from self.parse_haicop(response)
        elif 'marchespublics.gov.tn' in response.url:
            yield from self.parse_marches_publics(response)
        else:
            # Generic parsing
            yield from self.parse_generic(response)

    def parse_tuneps(self, response):
        """Parse TUNEPS tender results."""
        # TUNEPS tender result cards
        tenders = response.css('.tender, .result, .marche, article')

        for tender in tenders:
            tender_title = self.extract_text(tender, [
                'h2::text', 'h3::text', '.title::text', '.titre::text'
            ])

            # Check if it's engineering/design related
            if not self._is_engineering_tender(tender_title):
                continue

            # Extract winner company
            winner = self.extract_text(tender, [
                '.winner::text', '.attributaire::text',
                '.company::text', '.entreprise::text',
                'strong:contains("Attributaire")::text',
                'td:contains("Attributaire") + td::text'
            ])

            if winner and self._looks_like_company(winner):
                tender_ref = self.extract_text(tender, [
                    '.reference::text', '.ref::text', '.numero::text'
                ])

                amount = self._extract_amount(tender)

                yield {
                    'signal_type': 'tender_detected',
                    'company_name': winner.strip(),
                    'tender_title': tender_title,
                    'tender_ref': tender_ref,
                    'amount': amount,
                    'source': 'TUNEPS',
                    'source_url': response.url,
                    'title': f"Public tender won: {tender_title[:100] if tender_title else 'Engineering contract'}",
                    'detail': f"Won TUNEPS tender: {tender_title if tender_title else 'engineering/design contract'}",
                    'has_audit_requirement': True,  # Public tenders always audited
                }

        # Pagination
        next_page = response.css('a.next::attr(href), .pagination a[rel="next"]::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse_tuneps)

    def parse_ministry_industry(self, response):
        """Parse Ministry of Industry tender pages."""
        yield from self.parse_generic(response)

    def parse_ministry_equipment(self, response):
        """Parse Ministry of Equipment tender pages."""
        yield from self.parse_generic(response)

    def parse_haicop(self, response):
        """Parse Haute Instance de la Commande Publique pages."""
        yield from self.parse_generic(response)

    def parse_marches_publics(self, response):
        """Parse marchespublics.gov.tn platform."""
        yield from self.parse_generic(response)

    def parse_generic(self, response):
        """Generic parser for any tender page."""
        # Look for tender result sections
        tender_sections = response.css(
            'section:contains("résultat"), '
            'section:contains("attributaire"), '
            'div.results, '
            'div.tenders, '
            'table.marches, '
            'table.results'
        )

        for section in tender_sections:
            section_text = ' '.join(section.css('::text').getall())

            # Check if engineering-related
            if not any(kw in section_text.lower() for kw in self.TENDER_KEYWORDS):
                continue

            # Try to extract tender info from tables
            rows = section.css('tr')
            for row in rows:
                cells = row.css('td::text, th::text').getall()
                cells_text = ' '.join(cells)

                # Look for company names in cells
                for cell in cells:
                    cell = cell.strip()
                    if self._looks_like_company(cell) and len(cell) > 5:
                        # Found potential winner
                        tender_title = self._extract_tender_title_from_row(row)

                        yield {
                            'signal_type': 'tender_detected',
                            'company_name': cell,
                            'tender_title': tender_title,
                            'source': self._get_source_name(response.url),
                            'source_url': response.url,
                            'title': f"Public tender won: {tender_title[:100] if tender_title else 'Government contract'}",
                            'detail': f"Won public sector tender from {self._get_source_name(response.url)}",
                            'has_audit_requirement': True,
                        }

        # Look for list items with company names
        list_items = response.css('ul li, ol li')
        for item in list_items:
            item_text = ' '.join(item.css('::text').getall())

            # Check for tender/attributaire keywords
            if any(kw in item_text.lower() for kw in ['attributaire', 'winner', 'retenu', 'adjudicataire']):
                # Try to extract company name
                company = self._extract_company_from_text(item_text)
                if company:
                    yield {
                        'signal_type': 'tender_detected',
                        'company_name': company,
                        'source': self._get_source_name(response.url),
                        'source_url': response.url,
                        'title': 'Public tender won',
                        'detail': f"Listed as tender winner on {self._get_source_name(response.url)}",
                        'has_audit_requirement': True,
                    }

        # Follow tender/result links
        for href in response.css('a[href*="resultat"], a[href*="tender"], a[href*="marche"]::attr(href)').getall():
            if href and len(href) > 5:
                yield response.follow(href, callback=self.parse)

    def _is_engineering_tender(self, title: str) -> bool:
        """Check if tender is engineering/design related."""
        if not title:
            return False

        title_lower = title.lower()
        return any(keyword in title_lower for keyword in self.TENDER_KEYWORDS)

    def _extract_amount(self, selector) -> Optional[str]:
        """Extract tender amount from selector."""
        amount_text = self.extract_text(selector, [
            '.montant::text', '.amount::text',
            'td:contains("Montant") + td::text',
            'span:contains("TND")::text'
        ])

        if amount_text:
            # Try to extract numeric amount
            match = re.search(r'([\d\s,\.]+)\s*(?:TND|DT|dinars)', amount_text, re.IGNORECASE)
            if match:
                return match.group(1).strip() + ' TND'

        return None

    def _extract_tender_title_from_row(self, row) -> Optional[str]:
        """Extract tender title from table row."""
        # Look for title-like cells
        cells = row.css('td::text, th::text').getall()

        for cell in cells:
            cell = cell.strip()
            # Title is usually longer text with keywords
            if len(cell) > 20 and any(kw in cell.lower() for kw in self.TENDER_KEYWORDS):
                return cell

        return None

    def _extract_company_from_text(self, text: str) -> Optional[str]:
        """Extract company name from text containing tender info."""
        # Patterns to match company names after key phrases
        patterns = [
            r'(?:attributaire|winner|retenu|adjudicataire)[:\s]+([A-Z][A-Za-z\s&-]{5,60})',
            r'([A-Z][A-Za-z\s&-]{5,60})\s+(?:a été retenu|has been awarded|remporte)',
            r'(?:entreprise|société|company)\s+([A-Z][A-Za-z\s&-]{5,60})',
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                candidate = match.group(1).strip()
                if self._looks_like_company(candidate):
                    return candidate

        return None

    def _looks_like_company(self, text: str) -> bool:
        """Check if text looks like a company name."""
        if not text or len(text) < 4:
            return False

        text_lower = text.lower().strip()

        # Exclude common non-company words
        excluded = [
            'resultat', 'résultat', 'result', 'tender', 'marche', 'marché',
            'appel', "appel d'offres", 'consultation', 'avis',
            'government', 'gouvernement', 'ministry', 'ministère', 'ministere',
            'republic', 'république', 'tunisian', 'tunisien', 'tunisia', 'tunisie',
            'national', 'public', 'state', 'etat', 'état',
            'project', 'projet', 'contract', 'contrat',
            'montant', 'amount', 'date', 'deadline', 'delai', 'délai',
            'objet', 'object', 'description',
        ]

        if text_lower in excluded:
            return False

        # Must have at least one capital letter
        if not any(c.isupper() for c in text):
            return False

        # Company name indicators (good signs)
        company_indicators = [
            'group', 'groupe', 'sarl', 'sa', 'sas', 'suarl',
            'industries', 'engineering', 'ingenierie', 'ingénierie',
            'construction', 'batiment', 'bâtiment',
            'technology', 'technologies', 'services', 'solutions',
            'consulting', 'conseil', 'bureau', 'btp',
            'etudes', 'études', 'design', 'conception',
        ]

        if any(indicator in text_lower for indicator in company_indicators):
            return True

        # If it has 2+ words and starts with capital, probably company
        words = text.split()
        if len(words) >= 2 and words[0][0].isupper():
            # But make sure it's not just a title
            if not text_lower.startswith(('etude', 'étude', 'conception', 'projet', 'marche', 'marché')):
                return True

        return False

    def _get_source_name(self, url: str) -> str:
        """Extract readable source name from URL."""
        if 'tuneps' in url:
            return "TUNEPS"
        elif 'industrie.gov.tn' in url:
            return "Ministry of Industry"
        elif 'equipement.tn' in url:
            return "Ministry of Equipment"
        elif 'mdci.gov.tn' in url:
            return "Ministry of Development"
        elif 'haicop.tn' in url:
            return "HAICOP"
        elif 'marchespublics.gov.tn' in url:
            return "Marchés Publics"
        elif 'iort.gov.tn' in url:
            return "JORT"
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

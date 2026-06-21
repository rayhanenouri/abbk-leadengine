"""
Spider 7: Event-based lead signals (engineering events, salons, conferences).

Targets:
- SOLIDWORKS regional events
- Engineering salons in Tunisia and Africa
- Industry conferences (automotive, aerospace, manufacturing)
- Trade shows with CAD/engineering exhibitors
- University career fairs with engineering companies

Focus: Companies attending engineering events = warm leads (already interested in engineering tools)
Creates LeadSignal with signal_type=event_attendance
"""
import scrapy
from datetime import datetime
from typing import Dict, Any, Optional
import logging
import re


class EventsSpider(scrapy.Spider):
    """
    Scrapes engineering event websites for participant/exhibitor companies.

    Why this matters for ABBK:
    1. Event participants are actively engaged in engineering
    2. SOLIDWORKS events = direct SOLIDWORKS users or prospects
    3. Industry salons = companies investing in visibility/growth
    4. Exhibitors have budget (booth costs money)
    5. Networking events = decision-makers present

    Detection strategy:
    - Event exhibitor lists
    - Participant company rosters
    - Sponsor company lists
    - Speaker/presenter companies
    """

    name = "events"

    # Engineering event keywords
    EVENT_KEYWORDS = [
        'solidworks', 'cad', 'cao',
        'engineering', 'ingénierie', 'ingenierie',
        'manufacturing', 'fabrication',
        'design', 'conception',
        'innovation', 'technologie',
        'industrie', 'industrial',
        'automotive', 'automobile',
        'aerospace', 'aéronautique',
        'construction', 'btp',
    ]

    start_urls = [
        # SOLIDWORKS Events
        "https://www.solidworks.com/events",
        "https://www.solidworks.com/events/regional-user-groups",

        # Tunisia Engineering Events
        "https://www.tunisie-industrie.tn/evenements",
        "https://www.tunisie-industrie.tn/salons",

        # UTICA (Union Tunisienne de l'Industrie, du Commerce et de l'Artisanat)
        "http://www.utica.org.tn/evenements",
        "http://www.utica.org.tn/salons",

        # CEPEX - Centre de Promotion des Exportations
        "http://www.cepex.tn/evenements",
        "http://www.cepex.tn/salons-internationaux",

        # Foires et Salons Tunisia
        "https://www.foiresetsalons.tn",
        "https://www.foiresetsalons.tn/salons-industriels",

        # African Engineering Events
        "https://www.afreximbankevents.com",  # African events
        "https://www.eventbrite.com/d/tunisia/engineering-events",

        # University Career Fairs
        "https://www.enit.rnu.tn/evenements",  # ENIT events
        "https://www.enim.rnu.tn/evenements",  # ENIM events

        # Chamber of Commerce Events
        "http://www.ccitunisie.org/evenements",
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
    }

    def parse(self, response):
        """Parse event pages for participant/exhibitor lists."""
        self.logger.info(f"Parsing event page: {response.url}")

        # Look for event listings
        events = response.css(
            '.event, .salon, .conference, '
            'article.event, '
            '.event-item, '
            'div[class*="event"]'
        )

        if events:
            for event in events:
                # Check if event is engineering-related
                event_text = ' '.join(event.css('::text').getall()).lower()
                if self._is_engineering_event(event_text):
                    # Try to find event detail page
                    event_url = event.css('a::attr(href)').get()
                    if event_url:
                        yield response.follow(event_url, callback=self.parse_event_detail)

        # Parse as event detail page (has exhibitors/participants)
        yield from self.parse_event_detail(response)

        # Follow event/salon links
        for href in response.css('a[href*="event"], a[href*="salon"], a[href*="conference"]::attr(href)').getall():
            if href:
                yield response.follow(href, callback=self.parse)

    def parse_event_detail(self, response):
        """Parse event detail page for exhibitor/participant companies."""
        # Extract event name
        event_name = self.extract_text(response, [
            'h1::text', 'h2.event-title::text', '.event-name::text', 'title::text'
        ])

        if not event_name:
            event_name = "Engineering event"

        # Check if this is an engineering event
        page_text = ' '.join(response.css('body ::text').getall()).lower()
        if not self._is_engineering_event(page_text):
            self.logger.debug(f"Not an engineering event: {response.url}")
            return

        # Extract event date
        event_date = self._extract_event_date(response)

        # Look for exhibitor/participant sections
        exhibitor_sections = response.css(
            'section:contains("exposant"), '
            'section:contains("exhibitor"), '
            'section:contains("participant"), '
            'div.exhibitors, '
            'div.participants, '
            '.exposants, '
            '.liste-exposants'
        )

        companies_found = []

        # Method 1: Structured exhibitor lists
        for section in exhibitor_sections:
            company_names = section.css(
                'h3::text, h4::text, '
                'li::text, '
                '.company-name::text, '
                '.exhibitor-name::text, '
                'a::text'
            ).getall()

            for name in company_names:
                name = name.strip()
                if self._looks_like_company(name):
                    companies_found.append(name)

        # Method 2: Exhibitor logos
        exhibitor_logos = response.css('.exhibitors img, .exposants img, .sponsors img')
        for img in exhibitor_logos:
            alt_text = img.css('::attr(alt)').get()
            if alt_text and self._looks_like_company(alt_text):
                companies_found.append(alt_text.strip())

        # Method 3: Sponsor companies
        sponsor_sections = response.css('section:contains("sponsor"), .sponsors, .partenaires')
        for section in sponsor_sections:
            company_names = section.css('strong::text, b::text, a::text').getall()
            for name in company_names:
                name = name.strip()
                if self._looks_like_company(name) and len(name) > 4:
                    companies_found.append(name)

        # Method 4: Tables with company lists
        tables = response.css('table.exhibitors, table.participants, table.exposants')
        for table in tables:
            cells = table.css('td::text, th::text').getall()
            for cell in cells:
                cell = cell.strip()
                if self._looks_like_company(cell):
                    companies_found.append(cell)

        # Deduplicate
        unique_companies = list(set(companies_found))

        for company_name in unique_companies:
            yield {
                'signal_type': 'event_attendance',
                'company_name': company_name,
                'event_name': event_name[:200],  # Truncate
                'event_date': event_date,
                'event_type': self._classify_event(event_name, page_text),
                'source': self._get_source_name(response.url),
                'source_url': response.url,
                'title': f"Attended: {event_name[:100]}",
                'detail': f"Company participated in {event_name}",
            }

        self.logger.info(f"Found {len(unique_companies)} companies at {event_name}")

    def _is_engineering_event(self, text: str) -> bool:
        """Check if event is engineering-related."""
        if not text:
            return False

        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.EVENT_KEYWORDS)

    def _extract_event_date(self, response) -> Optional[str]:
        """Extract event date from page."""
        date_text = self.extract_text(response, [
            '.event-date::text', '.date::text',
            'time::text', '[datetime]::attr(datetime)',
            'span.date::text'
        ])

        if date_text:
            # Try to extract date pattern
            # Common formats: "15-17 juin 2026", "June 15, 2026", "2026-06-15"
            date_patterns = [
                r'(\d{1,2}[-/]\d{1,2}[-/]\d{4})',  # DD-MM-YYYY or DD/MM/YYYY
                r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})',  # YYYY-MM-DD
                r'(\d{1,2}\s+\w+\s+\d{4})',        # DD Month YYYY
            ]

            for pattern in date_patterns:
                match = re.search(pattern, date_text)
                if match:
                    return match.group(1)

        return None

    def _classify_event(self, event_name: str, page_text: str) -> str:
        """Classify event type."""
        event_lower = (event_name + ' ' + page_text).lower()

        if 'solidworks' in event_lower:
            return "SOLIDWORKS event"
        elif any(kw in event_lower for kw in ['salon', 'fair', 'expo', 'exhibition']):
            return "Trade show"
        elif any(kw in event_lower for kw in ['conference', 'conférence', 'summit']):
            return "Conference"
        elif any(kw in event_lower for kw in ['workshop', 'atelier', 'formation']):
            return "Workshop"
        elif any(kw in event_lower for kw in ['forum', 'networking']):
            return "Forum"
        elif any(kw in event_lower for kw in ['career fair', 'job fair', 'emploi']):
            return "Career fair"
        else:
            return "Industry event"

    def _looks_like_company(self, text: str) -> bool:
        """Check if text looks like a company name."""
        if not text or len(text) < 4:
            return False

        text_lower = text.lower().strip()

        # Exclude common non-company words
        excluded = [
            'exposant', 'exhibitor', 'participant', 'sponsor',
            'voir', 'more', 'list', 'liste', 'all', 'tous',
            'contact', 'information', 'details', 'détails',
            'date', 'horaire', 'schedule', 'location', 'lieu',
            'inscription', 'register', 'ticket', 'billet',
            'home', 'accueil', 'about', 'propos',
        ]

        if text_lower in excluded:
            return False

        # Must have at least one letter
        if not re.search(r'[a-zA-Z]', text):
            return False

        # Filter out URLs
        if text_lower.startswith(('http', 'www', 'mailto:', 'tel:')):
            return False

        # Company indicators (good signs)
        company_indicators = [
            'group', 'groupe', 'sarl', 'sa', 'sas',
            'industries', 'engineering', 'technologies',
            'services', 'solutions', 'systems',
            'construction', 'manufacturing',
        ]

        if any(indicator in text_lower for indicator in company_indicators):
            return True

        # If it has 2+ words and reasonable length, likely a company
        words = text.split()
        if len(words) >= 2 and len(text) <= 80:
            # But filter out common phrases
            if not text_lower.startswith(('list of', 'liste des', 'our', 'nos', 'the', 'les')):
                return True

        return False

    def _get_source_name(self, url: str) -> str:
        """Extract readable source name from URL."""
        if 'solidworks.com' in url:
            return "SOLIDWORKS Events"
        elif 'tunisie-industrie' in url:
            return "Tunisie Industrie"
        elif 'utica.org.tn' in url:
            return "UTICA"
        elif 'cepex.tn' in url:
            return "CEPEX"
        elif 'foiresetsalons' in url:
            return "Foires et Salons"
        elif 'enit.rnu.tn' in url:
            return "ENIT"
        elif 'enim.rnu.tn' in url:
            return "ENIM"
        elif 'ccitunisie' in url:
            return "Chambre de Commerce"
        elif 'eventbrite' in url:
            return "Eventbrite"
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

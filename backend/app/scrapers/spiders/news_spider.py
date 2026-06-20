"""
Spider 3: Tunisian business news scraper.

Targets:
- businessnews.com.tn
- managers.com.tn
- tekiano.com

Focus: Company mentions, funding news, expansion signals, exports, partnerships
Creates LeadSignal with signal_type=news, funding, export_signal, etc.
"""
import scrapy
from datetime import datetime
from typing import Dict, Any, Optional
import logging
import re


class BusinessNewsSpider(scrapy.Spider):
    """
    Scrapes Tunisian business news for company signals.

    Target signals:
    - Funding announcements
    - Expansion news (new factory, new office)
    - Export contracts
    - International partnerships
    - Mergers & acquisitions
    - New product launches
    - ISO certifications
    - Government contracts/tenders won
    """

    name = "business_news"

    # Keywords that indicate high-value signals
    FUNDING_KEYWORDS = [
        'financement', 'investissement', 'levée de fonds', 'capital',
        'funding', 'investment', 'million', 'dinars', 'euros', 'dollars',
        'bailleur de fonds', 'banque mondiale', 'afd', 'bei',
    ]

    EXPANSION_KEYWORDS = [
        'expansion', 'croissance', 'nouvelle usine', 'nouveau site',
        'agrandissement', 'développement', 'growth', 'factory',
    ]

    EXPORT_KEYWORDS = [
        'export', 'international', 'étranger', 'abroad', 'overseas',
        'contrat international', 'marché international', 'partenariat international',
    ]

    AUDIT_KEYWORDS = [
        'iso', 'certification', 'audit', 'conformité', 'compliance',
        'qualité', 'norme', 'accréditation',
    ]

    MULTINATIONAL_KEYWORDS = [
        'multinational', 'filiale', 'groupe international', 'subsidiary',
        'international group', 'worldwide', 'global',
    ]

    start_urls = [
        # BusinessNews.com.tn - main business news
        "https://www.businessnews.com.tn/",
        "https://www.businessnews.com.tn/categorie/entreprises",
        "https://www.businessnews.com.tn/categorie/economie",

        # Managers.com.tn - management and business
        "https://www.managers.com.tn/",
        "https://www.managers.com.tn/articles/entreprises",

        # Tekiano.com - tech and business
        "https://www.tekiano.com/category/business/",
    ]

    custom_settings = {
        'ROBOTSTXT_OBEY': True,
        'CONCURRENT_REQUESTS': 3,
        'DOWNLOAD_DELAY': 3,  # Respectful - 3 second delay for news sites
        'USER_AGENT': 'Mozilla/5.0 (compatible; ABBKLeadBot/1.0; +https://abbk-tn.com)',
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 3,
        'AUTOTHROTTLE_MAX_DELAY': 10,
    }

    def parse(self, response):
        """Parse news listing pages and extract article links."""
        self.logger.info(f"Parsing news from {response.url}")

        # Detect which site we're on
        if 'businessnews.com.tn' in response.url:
            yield from self.parse_businessnews(response)
        elif 'managers.com.tn' in response.url:
            yield from self.parse_managers(response)
        elif 'tekiano.com' in response.url:
            yield from self.parse_tekiano(response)

    def parse_businessnews(self, response):
        """Parse businessnews.com.tn articles."""
        # Article links
        articles = response.css('article, .post, .article-item, .news-item')

        for article in articles[:20]:  # Limit to 20 most recent
            title = self.extract_text(article, [
                'h2 a::text',
                'h3 a::text',
                '.title a::text',
                '.post-title a::text',
            ])

            link = self.extract_link(article, [
                'h2 a::attr(href)',
                'h3 a::attr(href)',
                '.title a::attr(href)',
                'a.read-more::attr(href)',
            ], response)

            excerpt = self.extract_text(article, [
                '.excerpt::text',
                '.summary::text',
                'p::text',
            ])

            if title and link:
                # Check if title/excerpt contains company or signal keywords
                text = f"{title} {excerpt}".lower()

                if self.contains_business_signal(text):
                    yield response.follow(
                        link,
                        callback=self.parse_article,
                        meta={'title': title, 'source': 'businessnews.com.tn'}
                    )

    def parse_managers(self, response):
        """Parse managers.com.tn articles."""
        articles = response.css('article, .post-item, .article')

        for article in articles[:20]:
            title = self.extract_text(article, [
                'h2 a::text',
                'h3 a::text',
                '.post-title a::text',
            ])

            link = self.extract_link(article, [
                'h2 a::attr(href)',
                'h3 a::attr(href)',
                'a::attr(href)',
            ], response)

            excerpt = self.extract_text(article, [
                '.excerpt::text',
                'p::text',
            ])

            if title and link:
                text = f"{title} {excerpt}".lower()

                if self.contains_business_signal(text):
                    yield response.follow(
                        link,
                        callback=self.parse_article,
                        meta={'title': title, 'source': 'managers.com.tn'}
                    )

    def parse_tekiano(self, response):
        """Parse tekiano.com articles."""
        articles = response.css('article, .post')

        for article in articles[:15]:
            title = self.extract_text(article, [
                'h2 a::text',
                'h3 a::text',
                '.entry-title a::text',
            ])

            link = self.extract_link(article, [
                'h2 a::attr(href)',
                'h3 a::attr(href)',
                '.entry-title a::attr(href)',
            ], response)

            if title and link:
                text = title.lower()

                if self.contains_business_signal(text):
                    yield response.follow(
                        link,
                        callback=self.parse_article,
                        meta={'title': title, 'source': 'tekiano.com'}
                    )

    def parse_article(self, response):
        """Parse individual article and extract company signals."""
        title = response.meta.get('title', '')
        source = response.meta.get('source', '')

        # Extract article content
        content = ' '.join(response.css(
            'article p::text, .post-content p::text, .entry-content p::text, .article-body p::text'
        ).getall())

        full_text = f"{title} {content}".lower()

        # Extract all company names mentioned
        companies = self.extract_company_names(full_text, response)

        # Determine signal types
        signal_types = self.detect_signal_types(full_text)

        # Create signal for each company mentioned
        for company_name in companies:
            for signal_type in signal_types:
                yield {
                    'signal_type': signal_type,
                    'company_name': company_name,
                    'title': title[:500],  # Truncate to 500 chars
                    'detail': content[:1000] if content else title,  # First 1000 chars
                    'source': source,
                    'source_url': response.url,
                    'detected_at': datetime.utcnow().isoformat(),
                }

    def contains_business_signal(self, text: str) -> bool:
        """Check if text contains any business signal keywords."""
        all_keywords = (
            self.FUNDING_KEYWORDS +
            self.EXPANSION_KEYWORDS +
            self.EXPORT_KEYWORDS +
            self.AUDIT_KEYWORDS +
            self.MULTINATIONAL_KEYWORDS
        )

        return any(keyword in text for keyword in all_keywords)

    def detect_signal_types(self, text: str) -> list:
        """Detect which signal types are present in the text."""
        signals = []

        # Check funding
        if any(kw in text for kw in self.FUNDING_KEYWORDS):
            signals.append('funding')

        # Check expansion
        if any(kw in text for kw in self.EXPANSION_KEYWORDS):
            signals.append('news')  # General news signal

        # Check export
        if any(kw in text for kw in self.EXPORT_KEYWORDS):
            signals.append('export_signal')

        # Check audit/certification
        if any(kw in text for kw in self.AUDIT_KEYWORDS):
            signals.append('audit_signal')

        # Check multinational
        if any(kw in text for kw in self.MULTINATIONAL_KEYWORDS):
            signals.append('multinational_signal')

        # Default to news if nothing specific detected
        if not signals:
            signals.append('news')

        return signals

    def extract_company_names(self, text: str, response) -> list:
        """
        Extract company names from article text.

        Look for patterns like:
        - "l'entreprise X"
        - "la société X"
        - "le groupe X"
        - Capitalized multi-word names
        - Known Tunisian companies
        """
        companies = set()

        # Pattern 1: "l'entreprise/société/groupe NAME"
        patterns = [
            r"l'entreprise\s+([A-Z][A-Za-z\s&-]{2,40})",
            r"la société\s+([A-Z][A-Za-z\s&-]{2,40})",
            r"le groupe\s+([A-Z][A-Za-z\s&-]{2,40})",
            r"société\s+([A-Z][A-Za-z\s&-]{2,40})",
            r"entreprise\s+([A-Z][A-Za-z\s&-]{2,40})",
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                company = match.strip()
                if len(company) > 3 and not self.is_common_word(company):
                    companies.add(company)

        # Pattern 2: Capitalized sequences (likely company names)
        # e.g., "Poulina Group", "STMicroelectronics", "Telnet Holding"
        cap_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3})\b'
        matches = re.findall(cap_pattern, response.text)
        for match in matches[:50]:  # Limit to avoid noise
            if len(match) > 3 and not self.is_common_word(match):
                companies.add(match)

        # Pattern 3: Company suffixes
        suffix_pattern = r'([A-Za-z\s&-]{3,40})\s+(SA|SARL|SUARL|Holding|Group|Corporation|International|Industries|Tunisia)'
        matches = re.findall(suffix_pattern, text, re.IGNORECASE)
        for match in matches:
            company = f"{match[0].strip()} {match[1]}"
            if not self.is_common_word(company):
                companies.add(company)

        return list(companies)[:10]  # Max 10 companies per article

    def is_common_word(self, text: str) -> bool:
        """Filter out common words that aren't company names."""
        common_words = {
            'tunisie', 'tunisia', 'tunis', 'sfax', 'sousse',
            'gouvernement', 'ministère', 'ministre', 'president',
            'république', 'état', 'pays', 'national', 'nouveau',
            'million', 'milliard', 'euros', 'dinars', 'dollars',
            'aujourd', 'demain', 'hier', 'année', 'mois',
        }
        return text.lower() in common_words

    def extract_text(self, element, selectors: list) -> str:
        """Extract text using first matching selector."""
        for selector in selectors:
            text = element.css(selector).get()
            if text:
                return text.strip()
        return ""

    def extract_link(self, element, selectors: list, response) -> Optional[str]:
        """Extract link using first matching selector."""
        for selector in selectors:
            link = element.css(selector).get()
            if link:
                return response.urljoin(link)
        return None

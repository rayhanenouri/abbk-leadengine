"""
Spider 4: Training history detection.

Targets:
- ISET websites (all regional campuses)
- University partner pages
- Company training and HR sections
- Centres de formation professionnelle listings
- ATFP (Agence Tunisienne de la Formation Professionnelle)

Focus: Companies sending employees to technical/engineering training
Creates LeadSignal with signal_type=training_detected
"""
import scrapy
from datetime import datetime
from typing import Dict, Any, Optional
import logging
import re


class TrainingCentersSpider(scrapy.Spider):
    """
    Scrapes training center websites for company participation signals.

    Detection methods:
    1. Partner companies listed on training center websites
    2. Company names in participant lists or testimonials
    3. Training programs with company sponsorship
    4. Corporate training announcements
    """

    name = "training_centers"

    # Target training keywords
    TRAINING_KEYWORDS = [
        'solidworks',
        'cao', 'cad',
        'conception',
        'simulation',
        'autocad',
        'catia',
        'abaqus',
        'ingenierie', 'ingénierie',
        'mecanique', 'mécanique',
        'industriel',
        'design',
        'bureau d etudes', "bureau d'études",
    ]

    # Tunisia ISET campuses
    ISET_URLS = [
        # Main ISET campuses
        "http://www.isetso.rnu.tn",  # Sousse
        "http://www.isetrad.rnu.tn",  # Radès
        "http://www.isetna.rnu.tn",  # Nabeul
        "http://www.isetkr.rnu.tn",  # Kairouan
        "http://www.isetgb.rnu.tn",  # Gabès
        "http://www.isetbz.rnu.tn",  # Bizerte
        "http://www.isetgf.rnu.tn",  # Gafsa
        "http://www.isetke.rnu.tn",  # Kef
        "http://www.isetks.rnu.tn",  # Kasserine
        "http://www.isetme.rnu.tn",  # Médenine
        "http://www.isetmh.rnu.tn",  # Mahdia
        "http://www.isetsf.rnu.tn",  # Sfax
    ]

    # VERIFIED training and education sources
    start_urls = [
        # Engineering schools
        "https://enis.rnu.tn/",  # ENIS Sfax
        "https://enit.rnu.tn/en/presentation-2/",  # ENIT Tunis
        "http://www.enicarthage.rnu.tn/en/ecole/apropos",  # ENIC Carthage

        # Universities and events
        "https://ucar.rnu.tn/events-et-news/",  # UCAR events
        "https://www.ept.tn/news-and-events",  # EPT news and events

        # Training providers (Tunisia and Africa)
        "https://mecadtechnologies.co.za/specialised-training/",  # Mecad Technologies South Africa
        "https://camining.com/",  # CAMining training
    ]

    custom_settings = {
        'ROBOTSTXT_OBEY': True,
        'CONCURRENT_REQUESTS': 3,
        'DOWNLOAD_DELAY': 3,  # Respectful - 3 second delay for .edu.tn sites
        'USER_AGENT': 'Mozilla/5.0 (compatible; ABBKLeadBot/1.0; +https://abbk-tn.com)',
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 3,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 2.0,
        'DOWNLOAD_TIMEOUT': 30,  # Educational sites can be slow
    }

    def parse(self, response):
        """Parse training center pages for company mentions."""
        self.logger.info(f"Parsing training center: {response.url}")

        # Extract all text content
        page_text = ' '.join(response.css('body ::text').getall()).lower()

        # Look for partner companies section
        partner_sections = response.css(
            'section:contains("partenaires"), '
            'section:contains("entreprises"), '
            'div.partners, '
            'div.entreprises, '
            '.partenaires, '
            '.entreprises'
        )

        companies_found = []

        # Method 1: Structured partner lists
        for section in partner_sections:
            company_names = section.css(
                'h3::text, h4::text, '
                'li::text, '
                '.company-name::text, '
                '.partner-name::text, '
                'a::text'
            ).getall()

            for name in company_names:
                name = name.strip()
                if self._looks_like_company(name):
                    companies_found.append(name)

        # Method 2: Logo images with alt text (common on partner pages)
        partner_logos = response.css('img[alt*="partenaire"], img[alt*="entreprise"], .partners img, .partenaires img')
        for img in partner_logos:
            alt_text = img.css('::attr(alt)').get()
            if alt_text and self._looks_like_company(alt_text):
                companies_found.append(alt_text.strip())

        # Method 3: Training program announcements
        training_programs = response.css(
            'article, '
            '.formation, '
            '.program, '
            '.training'
        )

        for program in training_programs:
            program_text = ' '.join(program.css('::text').getall()).lower()

            # Check if it's engineering/CAD related
            if any(keyword in program_text for keyword in self.TRAINING_KEYWORDS):
                # Look for company names in the program description
                company_mentions = program.css('strong::text, b::text, .company::text').getall()
                for mention in company_mentions:
                    mention = mention.strip()
                    if self._looks_like_company(mention):
                        companies_found.append(mention)

        # Method 4: Testimonials and case studies
        testimonials = response.css('.testimonial, .temoignage, .success-story, .etude-cas')
        for testimonial in testimonials:
            company = self.extract_text(testimonial, [
                '.company::text',
                '.entreprise::text',
                'cite::text',
                'strong::text'
            ])
            if company and self._looks_like_company(company):
                companies_found.append(company.strip())

        # Deduplicate and yield signals
        unique_companies = list(set(companies_found))

        for company_name in unique_companies:
            # Determine what kind of training
            training_type = self._detect_training_type(response, company_name)

            yield {
                'signal_type': 'training_detected',
                'company_name': company_name,
                'training_type': training_type,
                'source': self._get_source_name(response.url),
                'source_url': response.url,
                'detail': f"Company sent employees to {training_type} at {self._get_source_name(response.url)}",
                'title': f"Training at {self._get_source_name(response.url)}",
            }

        # Follow internal links to find more partner/training pages
        for href in response.css('a[href*="partenaire"], a[href*="entreprise"], a[href*="formation"]::attr(href)').getall():
            if href:
                yield response.follow(href, callback=self.parse)

    def _looks_like_company(self, text: str) -> bool:
        """
        Check if text looks like a company name.

        Filter out:
        - Very short strings (< 3 chars)
        - Common words
        - Navigation items
        """
        if not text or len(text) < 3:
            return False

        text_lower = text.lower().strip()

        # Filter out common non-company words
        excluded_words = [
            'accueil', 'home', 'contact', 'about', 'nous', 'services',
            'formation', 'training', 'partenaires', 'partners', 'entreprises',
            'voir', 'more', 'lire', 'read', 'suivant', 'next', 'précédent',
            'et', 'and', 'ou', 'or', 'le', 'la', 'les', 'the', 'a', 'an',
            'télécharger', 'download', 'inscription', 'register', 'login',
            'tous', 'all', 'notre', 'notre', 'nos', 'our', 'votre', 'your'
        ]

        if text_lower in excluded_words:
            return False

        # Must contain at least one letter
        if not re.search(r'[a-zA-Z]', text):
            return False

        # Filter out pure navigation text
        if text_lower.startswith(('http', 'www', 'mailto:', 'tel:')):
            return False

        # Company names typically have capital letters or specific patterns
        # Accept if:
        # 1. Has multiple words with capitals (e.g., "Poulina Group")
        # 2. Contains common company suffixes
        # 3. Is reasonably long (4+ chars)

        company_indicators = ['group', 'groupe', 'sarl', 'sa', 'industries', 'engineering', 'tunisie', 'tunisia']
        if any(indicator in text_lower for indicator in company_indicators):
            return True

        # If it's all lowercase and single word, probably not a company
        if text.islower() and ' ' not in text:
            return False

        return len(text) >= 4

    def _detect_training_type(self, response, company_name: str) -> str:
        """Detect what type of training based on page content."""
        page_text = ' '.join(response.css('body ::text').getall()).lower()

        # Check for specific training types
        if any(kw in page_text for kw in ['solidworks', 'catia', 'cao', 'cad']):
            return "CAD/SOLIDWORKS training"
        elif any(kw in page_text for kw in ['simulation', 'abaqus', 'ansys']):
            return "Simulation training"
        elif any(kw in page_text for kw in ['mecanique', 'mécanique', 'mechanical']):
            return "Mechanical engineering training"
        elif any(kw in page_text for kw in ['conception', 'design']):
            return "Design/conception training"
        elif any(kw in page_text for kw in ['industriel', 'manufacturing']):
            return "Industrial/manufacturing training"
        else:
            return "Technical training"

    def _get_source_name(self, url: str) -> str:
        """Extract readable source name from URL."""
        if 'isetso' in url:
            return "ISET Sousse"
        elif 'isetrad' in url:
            return "ISET Radès"
        elif 'isetna' in url:
            return "ISET Nabeul"
        elif 'isetkr' in url:
            return "ISET Kairouan"
        elif 'isetgb' in url:
            return "ISET Gabès"
        elif 'isetbz' in url:
            return "ISET Bizerte"
        elif 'isetgf' in url:
            return "ISET Gafsa"
        elif 'isetke' in url:
            return "ISET Kef"
        elif 'isetks' in url:
            return "ISET Kasserine"
        elif 'isetme' in url:
            return "ISET Médenine"
        elif 'isetmh' in url:
            return "ISET Mahdia"
        elif 'isetsf' in url:
            return "ISET Sfax"
        elif 'atfp' in url:
            return "ATFP"
        elif 'enim' in url:
            return "ENIM Monastir"
        elif 'enis' in url:
            return "ENIS Sfax"
        elif 'enit' in url:
            return "ENIT Tunis"
        elif 'tunisieformation' in url:
            return "TunisieFormation.com"
        elif 'formation.com.tn' in url:
            return "Formation.com.tn"
        else:
            # Extract domain name
            match = re.search(r'https?://(?:www\.)?([^/]+)', url)
            return match.group(1) if match else url

    def extract_text(self, selector, css_selectors: list) -> Optional[str]:
        """Try multiple CSS selectors and return first non-empty result."""
        for css in css_selectors:
            result = selector.css(css).get()
            if result and result.strip():
                return result.strip()
        return None

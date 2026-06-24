"""
Spider 2: Job boards hiring signals scraper.

Targets:
- emploi.tn
- keejob.com

Focus: Companies hiring engineers, CAD designers, R&D roles
Creates LeadSignal with signal_type=new_hire
"""
import scrapy
from datetime import datetime
from typing import Dict, Any, Optional
import logging


class JobsBoardsSpider(scrapy.Spider):
    """
    Scrapes Tunisian job boards for hiring signals.

    Target roles:
    - Ingénieur conception
    - CAD designer / Dessinateur CAO
    - Bureau d'études
    - R&D / Recherche et développement
    - Ingénieur mécanique
    - Ingénieur calcul
    - Ingénieur simulation
    - Ingénieur fabrication
    """

    name = "jobs_boards"

    # Target job keywords that indicate SOLIDWORKS potential
    TARGET_KEYWORDS = [
        'ingenieur conception',
        'ingénieur conception',
        'cad designer',
        'cao',
        'dessinateur cao',
        'bureau d etudes',
        "bureau d'études",
        'r&d',
        'recherche',
        'mecanique',
        'mécanique',
        'ingenieur calcul',
        'ingénieur calcul',
        'simulation',
        'solidworks',
        'conception mecanique',
        'conception mécanique',
        'ingenieur fabrication',
        'ingénieur fabrication',
    ]

    # VERIFIED job boards - hiring signals
    start_urls = [
        # Tunisia job sites
        "https://www.naukrigulf.com/engineer-jobs-in-tunis",  # Engineering jobs Tunis
        "https://tunisia.tanqeeb.com/s/jobs/engineer?state=148",  # Engineer jobs Tunisia
        "https://www.bayt.com/en/tunisia/jobs/mechanical-engineer-jobs/",  # Mechanical engineer
        "https://www.tunisietravail.net/",  # Tunisia work portal
        "https://www.optioncarriere.tn/",  # Career options
        "https://www.keejob.com/",  # KeeJob
        "https://emploi.nat.tn/fo/Fr/global.php",  # National employment
        "https://www.tanitjobs.com/",  # Tanit Jobs

        # Africa-wide
        "https://www.africareers.net/",  # African careers
    ]

    custom_settings = {
        'ROBOTSTXT_OBEY': True,
        'CONCURRENT_REQUESTS': 4,
        'DOWNLOAD_DELAY': 2,  # Respectful - 2 second delay
        'USER_AGENT': 'Mozilla/5.0 (compatible; ABBKLeadBot/1.0; +https://abbk-tn.com)',
        'AUTOTHROTTLE_ENABLED': True,
    }

    def parse(self, response):
        """Parse job listing pages."""
        self.logger.info(f"Parsing job listings from {response.url}")

        # Detect which site we're on
        if 'emploi.tn' in response.url:
            yield from self.parse_emploi_tn(response)
        elif 'keejob.com' in response.url:
            yield from self.parse_keejob(response)

    def parse_emploi_tn(self, response):
        """Parse emploi.tn job listings."""
        # Job cards on emploi.tn
        jobs = response.css('.job-item, .job-card, .offer-item, article.job')

        for job in jobs:
            job_title = self.extract_text(job, [
                '.job-title::text',
                'h2 a::text',
                'h3 a::text',
                '.title a::text'
            ])

            company_name = self.extract_text(job, [
                '.company-name::text',
                '.employer::text',
                '.company::text',
                'span.company::text'
            ])

            location = self.extract_text(job, [
                '.location::text',
                '.ville::text',
                '.city::text'
            ])

            if self._is_target_job(job_title) and company_name:
                yield {
                    'signal_type': 'new_hire',
                    'company_name': company_name.strip(),
                    'job_title': job_title.strip() if job_title else 'Engineering role',
                    'location': location.strip() if location else None,
                    'source': 'emploi.tn',
                    'source_url': response.url,
                    'detail': f"Hiring {job_title}" if job_title else "Hiring engineering role",
                }

        # Pagination
        next_page = response.css('a.next::attr(href), .pagination a[rel="next"]::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_keejob(self, response):
        """Parse keejob.com job listings."""
        jobs = response.css('.job-list-item, .job-item, article.job')

        for job in jobs:
            job_title = self.extract_text(job, [
                'h2 a::text',
                '.job-title::text',
                'h3::text'
            ])

            company_name = self.extract_text(job, [
                '.company-name::text',
                '.recruiter::text',
                '.entreprise::text'
            ])

            location = self.extract_text(job, [
                '.location::text',
                '.localisation::text'
            ])

            if self._is_target_job(job_title) and company_name:
                yield {
                    'signal_type': 'new_hire',
                    'company_name': company_name.strip(),
                    'job_title': job_title.strip() if job_title else 'Engineering role',
                    'location': location.strip() if location else None,
                    'source': 'keejob.com',
                    'source_url': response.url,
                    'detail': f"Hiring {job_title}" if job_title else "Hiring engineering role",
                }

        # Pagination
        next_page = response.css('a.next::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def _is_target_job(self, job_title: str) -> bool:
        """Check if job title matches target engineering roles."""
        if not job_title:
            return False

        job_lower = job_title.lower()
        return any(keyword in job_lower for keyword in self.TARGET_KEYWORDS)

    def extract_text(self, selector, css_selectors: list) -> Optional[str]:
        """Try multiple CSS selectors and return first non-empty result."""
        for css in css_selectors:
            result = selector.css(css).get()
            if result and result.strip():
                return result.strip()
        return None

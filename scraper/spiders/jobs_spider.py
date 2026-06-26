"""
SPIDER: JOBS - VERIFIED WORKING JOB BOARDS ONLY
Scrapes hiring signals from REAL working job sites
"""

import scrapy
from datetime import datetime
import re


class JobsSpider(scrapy.Spider):
    name = 'jobs'

    custom_settings = {
        'CONCURRENT_REQUESTS': 4,
        'DOWNLOAD_DELAY': 3,
    }

    # VERIFIED WORKING URLs from user
    start_urls = [
        # International job boards - VERIFIED
        'https://www.naukrigulf.com/engineer-jobs-in-tunis',
        'https://tunisia.tanqeeb.com/s/jobs/engineer?state=148',
        'https://www.bayt.com/en/tunisia/jobs/mechanical-engineer-jobs/',

        # Tunisia job boards - VERIFIED
        'https://www.tunisietravail.net/',
        'https://www.optioncarriere.tn/',
        'https://www.keejob.com/',
        'https://emploi.nat.tn/fo/Fr/global.php',
        'https://www.tanitjobs.com/',

        # African job boards - VERIFIED
        'https://www.africareers.net/',
        'https://www.ceecareers.com/',
    ]

    def parse(self, response):
        """Parse job listing pages - generic extraction"""

        # Extract all job postings - generic approach
        for job in response.css('div[class*="job"], article[class*="job"], li[class*="job"]'):
            company = job.css('[class*="company"]::text, [class*="employer"]::text').get()
            title = job.css('[class*="title"]::text, h2::text, h3::text').get()
            link = job.css('a::attr(href)').get()

            if company and title:
                yield {
                    'signal_type': 'new_hire',
                    'company_name': company.strip(),
                    'title': f'Hiring: {title.strip()}',
                    'detail': f'{company.strip()} is actively hiring {title.strip()}',
                    'source_url': response.urljoin(link) if link else response.url,
                    'detected_at': datetime.now().isoformat(),
                    'source_site': 'Job Boards'
                }

        # Alternative: Extract company names from page text
        text = response.css('body::text').getall()
        full_text = ' '.join(text)

        # Find capitalized company names (heuristic)
        companies = re.findall(r'\b[A-Z][A-Za-z0-9\s&]{3,50}\b', full_text)

        for company in set(companies[:20]):  # Limit to 20 per page
            if len(company.strip()) > 3 and 'engineer' not in company.lower():
                yield {
                    'signal_type': 'new_hire',
                    'company_name': company.strip(),
                    'title': 'Hiring signal detected',
                    'detail': f'{company.strip()} mentioned on job board',
                    'source_url': response.url,
                    'detected_at': datetime.now().isoformat(),
                    'source_site': 'Job Boards'
                }

        # Follow pagination
        for next_link in response.css('a[href*="page"], a.next::attr(href)').getall()[:5]:
            yield response.follow(next_link, callback=self.parse)

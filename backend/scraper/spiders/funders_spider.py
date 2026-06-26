"""
SPIDER 6: FUNDERS SPIDER
Scrapes international funding organizations

Detects:
- funding signal (15 points)
- Sets under_audit=True (international funding requires licensed software)

Target sources:
- World Bank Tunisia
- AFD (Agence Française de Développement)
- EIB (European Investment Bank)
- EU funding programs
- USAID Tunisia
- GIZ (German cooperation)
- African Development Bank
"""

import scrapy
from datetime import datetime
import re


class FundersSpider(scrapy.Spider):
    name = 'funders'

    custom_settings = {
        'CONCURRENT_REQUESTS': 2,
        'DOWNLOAD_DELAY': 5,
    }

    start_urls = [
        # World Bank Tunisia projects
        'https://projects.worldbank.org/en/projects-operations/projects-list?countrycode_exact=TN',
        'https://www.banquemondiale.org/fr/country/tunisia/projects',

        # AFD - Agence Française de Développement
        'https://www.afd.fr/fr/page-region-pays/tunisie',
        'https://www.afd.fr/fr/carte-des-projets?country=TN',

        # EIB - European Investment Bank
        'https://www.eib.org/en/projects/all/index.htm?q=&sortColumn=loanParts.loanPartStatus.statusDate&sortDir=desc&pageNumber=0&itemPerPage=25&pageable=true&language=EN&defaultLanguage=EN&=&or=true&yearFrom=1959&yearTo=2026&ortrue&orc=TN',

        # EU funding - Tunisia
        'https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/opportunities/projects-results?keywords=tunisia',

        # USAID Tunisia
        'https://www.usaid.gov/tunisia/program-areas',

        # GIZ Tunisia
        'https://www.giz.de/en/worldwide/321.html',

        # African Development Bank
        'https://www.afdb.org/en/countries/north-africa/tunisia/tunisia-projects',

        # PNUD Tunisia
        'https://www.tn.undp.org/content/tunisia/fr/home/projects.html',
    ]

    FUNDING_KEYWORDS = [
        'financement', 'funding', 'subvention', 'grant',
        'projet', 'project', 'investissement', 'investment'
    ]

    def parse(self, response):
        """Parse funding project pages"""

        # Extract project listings
        for project in response.css('div.project-item, tr.project-row, div.card'):
            title = project.css('h3::text, td.title::text, a.title::text').get()
            beneficiary = project.css('span.beneficiary::text, td.company::text').get()
            amount = project.css('span.amount::text, td.amount::text').get()
            date = project.css('span.date::text, td.date::text').get()
            url = project.css('a::attr(href)').get()

            if title:
                text = title.lower()

                # Extract Tunisia company names
                companies = re.findall(r'\b[A-Z][A-Z\s&]+\b', title)

                if beneficiary:
                    companies.append(beneficiary)

                for company in set(companies[:3]):
                    if len(company.strip()) > 3:
                        yield {
                            'signal_type': 'funding',
                            'company_name': company.strip(),
                            'title': f'International funding: {title.strip()}',
                            'detail': f'{company} received international funding from {response.url}. Amount: {amount if amount else "N/A"}',
                            'source_url': response.urljoin(url) if url else response.url,
                            'detected_at': date or datetime.now().isoformat(),
                            'source_site': 'International Funders',
                            'under_audit': True  # International funding = audit requirement
                        }

        # Follow pagination
        next_page = response.css('a.next, li.next a::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

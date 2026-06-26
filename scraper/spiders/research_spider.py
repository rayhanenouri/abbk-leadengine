"""
SPIDER 8: RESEARCH CENTERS SPIDER
Scrapes university research labs and national research centers

Detects:
- role_detected signal (20 points - engineering researchers)
- training_detected signal (40 points - university partnerships)

Target sources:
- University research labs
- CERTE, CRBT national research centers
- Research center databases
"""

import scrapy
from datetime import datetime


class ResearchSpider(scrapy.Spider):
    name = 'research'

    custom_settings = {
        'CONCURRENT_REQUESTS': 2,
        'DOWNLOAD_DELAY': 4,
    }

    start_urls = [
        # CERTE - Centre d'Etudes et de Recherches des Télécommunications
        'http://www.certe.rnrt.tn/',

        # CRBT - Centre de Recherches et des Technologies des Eaux
        'http://www.certe.rnrt.tn/article85.html',

        # INRST - Institut National de Recherche Scientifique et Technique
        'http://www.inrst.rnrt.tn/',

        # Universities research directories
        'http://www.enit.rnu.tn/fr/recherche',
        'http://www.esstt.rnu.tn/fra/recherche.html',
        'http://www.insat.rnu.tn/Fr/Accueil_46_15',

        # Ministry of Higher Education research directory
        'http://www.mes.tn/index.php?id=129',

        # Tunisia research portal
        'http://www.recherche.tn/',
    ]

    def parse(self, response):
        """Parse research center pages"""

        # Look for partner companies and collaborative projects
        partners = response.css('div.partner, div.partenaire, li.company')

        for partner in partners:
            company_name = partner.css('::text, a::text').get()
            link = partner.css('a::attr(href)').get()

            if company_name and len(company_name.strip()) > 3:
                yield {
                    'signal_type': 'role_detected',
                    'company_name': company_name.strip(),
                    'title': 'Research partnership detected',
                    'detail': f'{company_name} has research collaboration with {response.url}',
                    'source_url': response.urljoin(link) if link else response.url,
                    'detected_at': datetime.now().isoformat(),
                    'source_site': 'Tunisia Research Centers'
                }

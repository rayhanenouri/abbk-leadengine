"""
SPIDER 3: TRAINING SPIDER
Scrapes ISET websites and training centers

Detects:
- training_detected signal (40 points - HIGHEST)

Target sources:
- ISET regional campuses
- Training center partner pages
- University engineering programs
"""

import scrapy
from datetime import datetime


class TrainingSpider(scrapy.Spider):
    name = 'training'

    custom_settings = {
        'CONCURRENT_REQUESTS': 2,
        'DOWNLOAD_DELAY': 4,
    }

    # ISET campuses - ALL regional campuses
    start_urls = [
        # ISET Tunis region
        'http://www.isetkh.rnu.tn/partenaires.php',
        'http://www.isetkh.rnu.tn/formation/',
        'http://www.isetrades.rnu.tn/partenaires',
        'http://www.isetrades.rnu.tn/formation',

        # ISET other regions
        'http://www.isetso.rnu.tn/index.php/partenaires',
        'http://www.isetso.rnu.tn/formation',
        'http://www.isetnabeul.rnu.tn/formation/',
        'http://www.isetnabeul.rnu.tn/partenaires/',
        'http://www.isetjendouba.rnu.tn/',
        'http://www.isetbizerte.rnu.tn/partenaires',
        'http://www.isetsfax.rnu.tn/partenaires',
        'http://www.isetsousse.rnu.tn/partenaires',
        'http://www.isetgafsa.rnu.tn/',
        'http://www.isetkef.rnu.tn/',
        'http://www.isetkairouan.rnu.tn/',

        # Universities - engineering schools
        'http://www.enit.rnu.tn/fr/node/152',  # Partenaires
        'http://www.esstt.rnu.tn/fra/partenaires.html',
        'http://www.insat.rnu.tn/Fr/Accueil_46_14',

        # ATFP - Agence Tunisienne de la Formation Professionnelle
        'http://www.emploi.nat.tn/fo/Fr/global.php?code=17',

        # Private training centers
        'https://www.centres-formation.tn/cao-cfao/',
        'https://www.centres-formation.tn/solidworks/',
    ]

    TRAINING_KEYWORDS = [
        'solidworks', 'formation', 'training', 'partenaire',
        'cao', 'cfao', 'dassault', 'certification'
    ]

    def parse(self, response):
        """Parse training center pages"""

        page_text = response.css('body::text').getall()
        content = ' '.join(page_text).lower()

        # Check if page mentions SOLIDWORKS or CAD training
        if any(kw in content for kw in self.TRAINING_KEYWORDS):

            # Extract company mentions from partner sections
            partners = response.css('div.partner, div.partenaire, ul.partners li')

            for partner in partners:
                company_name = partner.css('::text').get()
                link = partner.css('a::attr(href)').get()

                if company_name and len(company_name.strip()) > 3:
                    yield {
                        'signal_type': 'training_detected',
                        'company_name': company_name.strip(),
                        'title': 'Training partnership detected',
                        'detail': f'{company_name} has training partnership with {response.url}',
                        'source_url': response.url,
                        'detected_at': datetime.now().isoformat(),
                        'source_site': 'ISET Training Centers'
                    }

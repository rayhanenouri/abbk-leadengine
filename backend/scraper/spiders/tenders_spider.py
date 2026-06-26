"""
SPIDER 4: TENDERS SPIDER
Scrapes TUNEPS and public procurement platforms

Detects:
- tender_detected signal (30 points)

Target sources:
- TUNEPS (Tunisia public procurement)
- Ministry tender announcements
"""

import scrapy
from datetime import datetime
import re


class TendersSpider(scrapy.Spider):
    name = 'tenders'

    custom_settings = {
        'CONCURRENT_REQUESTS': 2,
        'DOWNLOAD_DELAY': 5,
    }

    start_urls = [
        # TUNEPS - Tunisia National Electronic Procurement
        'https://www.tuneps.tn/Fr/appelsoffres_0_46',  # Equipment tenders
        'https://www.tuneps.tn/Fr/appelsoffres_0_47',  # Manufacturing tenders
        'https://www.tuneps.tn/Fr/appelsoffres_0_3',   # Industry tenders
        'https://www.tuneps.tn/Fr/appelsoffres_0_8',   # Technology tenders

        # Ministry of Industry
        'http://www.industrie.gov.tn/Fr/appels-doffres_11_49',

        # Ministry of Higher Education and Research
        'http://www.mes.tn/index.php?id=165',

        # HAICOP - Haute Instance de la Commande Publique
        'http://www.haicop.tn/ar/archive.php?id_menu=42',

        # Marchés Publics
        'http://www.marchespublics.gov.tn/',

        # JORT - Journal Officiel
        'http://www.iort.gov.tn/WD120AWP/WD120Awp.exe/CTX_3050-321-sKwqCVYoGD/AffichageCadre/SYNC_-777891774',
    ]

    def parse(self, response):
        """Parse tender listing pages"""

        # TUNEPS tender structure
        for tender in response.css('div.tender-item, tr.tender-row'):
            title = tender.css('td.title a::text, h3 a::text').get()
            tender_url = tender.css('td.title a::attr(href), h3 a::attr(href)').get()
            company = tender.css('td.company::text, span.company::text').get()
            date = tender.css('td.date::text, span.date::text').get()

            if title and ('machine' in title.lower() or 'equipment' in title.lower() or
                         'machine' in title.lower() or 'équipement' in title.lower()):

                # Extract company from title if not in separate field
                if not company:
                    company_match = re.search(r'pour\s+([A-Z][A-Za-z\s&]+)', title)
                    if company_match:
                        company = company_match.group(1)

                if company:
                    yield {
                        'signal_type': 'tender_detected',
                        'company_name': company.strip(),
                        'title': f'Public tender: {title.strip()}',
                        'detail': f'{company} won or submitted tender for new equipment/machines',
                        'source_url': response.urljoin(tender_url) if tender_url else response.url,
                        'detected_at': date or datetime.now().isoformat(),
                        'source_site': 'TUNEPS Public Tenders'
                    }

        # Follow pagination
        next_page = response.css('a.next, li.next a::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

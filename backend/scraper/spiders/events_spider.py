"""
SPIDER 7: EVENTS SPIDER
Scrapes engineering events and conferences

Detects:
- event_attendance signal (10 points)

Target sources:
- SOLIDWORKS regional events
- Tunisia engineering salons
- Industry conferences
- Trade shows
"""

import scrapy
from datetime import datetime


class EventsSpider(scrapy.Spider):
    name = 'events'

    custom_settings = {
        'CONCURRENT_REQUESTS': 4,
        'DOWNLOAD_DELAY': 3,
    }

    start_urls = [
        # SOLIDWORKS events
        'https://www.solidworks.com/sw/events.htm',

        # Tunisia trade shows and salons
        'https://www.cepex.nat.tn/fr/calendrier-des-salons',
        'https://www.tunisiatradefairs.com/',

        # UTICA - Union Tunisienne de l'Industrie, du Commerce et de l'Artisanat
        'https://www.utica.org.tn/Fr/actualites_17_57',

        # APII events
        'http://www.tunisieindustrie.nat.tn/fr/activites.asp',

        # Tunisia Engineering Expo
        'https://www.expofairs.com/tunisia/engineering-exhibitions/',

        # Automotive Tunisia events
        'https://taa.tn/fr/actualites',
        'https://taa.tn/fr/evenements',
    ]

    EVENT_KEYWORDS = [
        'salon', 'expo', 'conference', 'forum',
        'workshop', 'atelier', 'seminar', 'seminaire',
        'foire', 'exhibition', 'show'
    ]

    def parse(self, response):
        """Parse event pages to extract participant companies"""

        # Find event listings
        for event in response.css('div.event-item, article.event, div.salon-item'):
            title = event.css('h2::text, h3::text, h4::text').get()
            date = event.css('span.date::text, time::text').get()
            url = event.css('a::attr(href)').get()

            if title and any(kw in title.lower() for kw in self.EVENT_KEYWORDS):
                # Follow link to get participants
                if url:
                    yield response.follow(
                        url,
                        callback=self.parse_event_page,
                        meta={'event_title': title, 'event_date': date}
                    )

        # Follow pagination
        next_page = response.css('a.next::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_event_page(self, response):
        """Extract participant companies from event page"""

        event_title = response.meta.get('event_title', 'Engineering Event')
        event_date = response.meta.get('event_date', datetime.now().isoformat())

        # Look for exhibitors/participants sections
        participants = response.css('div.exhibitor, li.participant, div.company-list li')

        for participant in participants:
            company_name = participant.css('::text').get()

            if company_name and len(company_name.strip()) > 3:
                yield {
                    'signal_type': 'event_attendance',
                    'company_name': company_name.strip(),
                    'title': f'Event attendance: {event_title}',
                    'detail': f'{company_name} participated in {event_title} on {event_date}',
                    'source_url': response.url,
                    'detected_at': event_date,
                    'source_site': 'Tunisia Engineering Events'
                }

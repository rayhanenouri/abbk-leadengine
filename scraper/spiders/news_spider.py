"""
SPIDER 2: NEWS SPIDER
Scrapes businessnews.com.tn and other Tunisia business news sites

Detects:
- news signal (25 points)
- tender_detected signal (30 points)

Target keywords:
- nouveau projet
- expansion
- investissement
- appel d'offres
- tender
"""

import scrapy
from datetime import datetime
import re


class NewsSpider(scrapy.Spider):
    name = 'news'

    custom_settings = {
        'CONCURRENT_REQUESTS': 4,
        'DOWNLOAD_DELAY': 3,
    }

    start_urls = [
        # businessnews.com.tn - ALL categories
        'https://www.businessnews.com.tn/category/economie',
        'https://www.businessnews.com.tn/category/industrie',
        'https://www.businessnews.com.tn/category/entreprises',
        'https://www.businessnews.com.tn/category/investissement',

        # managers.com.tn
        'https://www.managers.com.tn/category/actualites',
        'https://www.managers.com.tn/category/entreprises',
        'https://www.managers.com.tn/category/industrie',

        # tekiano.com
        'https://www.tekiano.com/category/business',
        'https://www.tekiano.com/category/economie',

        # webmanagercenter.com
        'https://www.webmanagercenter.com/category/actualite/economie/',
        'https://www.webmanagercenter.com/category/actualite/industrie/',

        # kapitalis.com
        'https://kapitalis.com/tunisie/category/economie/',

        # lapresse.tn
        'https://lapresse.tn/category/economie/',

        # tunisienumerique.com
        'https://www.tunisienumerique.com/category/economie/',
    ]

    # Keywords for signal detection
    NEWS_KEYWORDS = [
        'nouveau projet', 'expansion', 'investissement',
        'nouvelle usine', 'new factory', 'agrandissement',
        'recrutement', 'emploi', 'hiring'
    ]

    TENDER_KEYWORDS = [
        'appel d\'offres', 'tender', 'marché public',
        'adjudication', 'procurement', 'soumission'
    ]

    def parse(self, response):
        """Parse news article listing pages"""

        # businessnews.com.tn structure
        for article in response.css('article.post'):
            title = article.css('h2.entry-title a::text').get()
            url = article.css('h2.entry-title a::attr(href)').get()
            excerpt = article.css('div.entry-summary::text').get()
            date = article.css('time.entry-date::attr(datetime)').get()

            if title and url:
                # Extract company names (simple heuristic)
                text = f"{title} {excerpt or ''}".lower()

                # Check for tender signals
                if any(kw in text for kw in self.TENDER_KEYWORDS):
                    yield response.follow(url, callback=self.parse_article,
                                         meta={'signal_type': 'tender_detected', 'date': date})

                # Check for news signals
                elif any(kw in text for kw in self.NEWS_KEYWORDS):
                    yield response.follow(url, callback=self.parse_article,
                                         meta={'signal_type': 'news', 'date': date})

        # managers.com.tn structure
        for article in response.css('div.article-item'):
            title = article.css('h3 a::text').get()
            url = article.css('h3 a::attr(href)').get()

            if title and url:
                text = title.lower()

                if any(kw in text for kw in self.TENDER_KEYWORDS):
                    yield response.follow(url, callback=self.parse_article,
                                         meta={'signal_type': 'tender_detected'})
                elif any(kw in text for kw in self.NEWS_KEYWORDS):
                    yield response.follow(url, callback=self.parse_article,
                                         meta={'signal_type': 'news'})

        # Follow pagination
        next_page = response.css('a.next::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_article(self, response):
        """Parse individual article to extract company mentions"""

        title = response.css('h1.entry-title::text, h1.article-title::text').get()
        content = ' '.join(response.css('div.entry-content p::text, div.article-content p::text').getall())

        # Extract company names (Tunisia companies typically capitalized or in quotes)
        companies = re.findall(r'\b[A-Z][A-Z\s&]+\b', content)
        companies = [c.strip() for c in companies if len(c.strip()) > 3 and len(c.strip()) < 50]

        signal_type = response.meta.get('signal_type', 'news')
        date = response.meta.get('date', datetime.now().isoformat())

        for company in set(companies[:5]):  # Limit to first 5 unique mentions
            yield {
                'signal_type': signal_type,
                'company_name': company,
                'title': title.strip() if title else 'News mention',
                'detail': f'{company} mentioned in press: {title}',
                'source_url': response.url,
                'detected_at': date,
                'source_site': 'Tunisia Business News'
            }

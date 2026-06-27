#!/usr/bin/env python3
"""
Deep Company Enrichment Spider

For every company WITH a website, this spider:
1. Scrapes their entire website (about, team, products, news, jobs)
2. Searches for them on LinkedIn (company page)
3. Finds their Facebook/social media and extracts recent posts
4. Detects: engineering, CAD, simulation, manufacturing mentions
5. Detects: current hiring for engineers
6. Extracts: employee count, job roles, ISO/export/audit mentions
7. Stores everything in lead.scraped_data as structured JSON

This is the CORE value of the platform — real company intelligence.
"""

import asyncio
import re
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse

import scrapy
from scrapy.http import Response
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Browser, Page


class DeepEnrichmentSpider(scrapy.Spider):
    name = "deep_enrichment"

    # Keywords to detect
    ENGINEERING_KEYWORDS = [
        "CAD", "solidworks", "simulation", "FEA", "CFD", "conception", "bureau d'études",
        "mechanical design", "3D modeling", "product design", "engineering",
        "ingénierie", "mécanique", "électrique", "manufacturing", "fabrication",
        "CAO", "DAO", "simulation numérique", "calcul de structure",
        "AutoCAD", "CATIA", "Inventor", "SolidEdge", "NX", "Creo"
    ]

    HIRING_KEYWORDS = [
        "recrutement", "recrute", "hiring", "job opening", "career", "offre d'emploi",
        "ingénieur", "engineer", "designer", "dessinateur", "technicien",
        "bureau d'études", "R&D", "conception", "CAD designer"
    ]

    ISO_KEYWORDS = [
        "ISO 9001", "ISO 14001", "ISO 45001", "certification", "certifié",
        "audit", "qualité", "quality", "certified", "accrédité"
    ]

    EXPORT_KEYWORDS = [
        "export", "international", "worldwide", "global", "overseas",
        "clients internationaux", "marchés internationaux", "à l'étranger"
    ]

    MULTINATIONAL_KEYWORDS = [
        "filiale", "subsidiary", "groupe", "group", "multinational",
        "international presence", "offices worldwide", "global company"
    ]

    custom_settings = {
        'CONCURRENT_REQUESTS': 2,  # Slow down to be respectful
        'DOWNLOAD_DELAY': 2,
        'ROBOTSTXT_OBEY': True,
        'USER_AGENT': 'ABBK-LeadEngine-Bot/1.0 (Sales Intelligence; +https://abbk-tn.com)',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.browser: Optional[Browser] = None
        self.processed_count = 0

    async def start_browser(self):
        """Start Playwright browser for JS-heavy sites."""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=True)

    async def close_browser(self):
        """Close Playwright browser."""
        if self.browser:
            await self.browser.close()

    def start_requests(self):
        """
        Override to get companies from database.
        In production, this would query PostgreSQL for all leads with websites.
        """
        # Placeholder - will be populated by Celery task
        # The task will pass companies via meta
        companies = getattr(self, 'companies', [])

        for company in companies:
            if company.get('website'):
                yield scrapy.Request(
                    url=company['website'],
                    callback=self.parse_company_website,
                    meta={
                        'company_id': company['id'],
                        'company_name': company['name'],
                        'playwright': False  # Try with Scrapy first
                    },
                    errback=self.handle_error
                )

    def parse_company_website(self, response: Response):
        """
        Parse company website homepage and find key pages.
        Extract: about, team, products, news, jobs pages.
        """
        company_id = response.meta['company_id']
        company_name = response.meta['company_name']

        self.logger.info(f"🔍 Enriching {company_name} — {response.url}")

        soup = BeautifulSoup(response.text, 'html.parser')

        # Initialize enrichment data
        enrichment_data = {
            "company_id": company_id,
            "company_name": company_name,
            "website": response.url,
            "enriched_at": None,  # Will be set by caller
            "homepage": {
                "title": soup.title.text.strip() if soup.title else "",
                "meta_description": self.extract_meta_description(soup),
                "text_content": soup.get_text(separator=" ", strip=True)[:5000],  # First 5000 chars
            },
            "about": {},
            "team": {},
            "products": {},
            "news": {},
            "jobs": {},
            "social_media": {},
            "signals": {
                "has_engineering": False,
                "has_cad_software": False,
                "is_hiring_engineers": False,
                "has_iso_certification": False,
                "is_exporter": False,
                "is_multinational": False,
                "employee_count": None,
                "job_openings": []
            }
        }

        # Detect signals from homepage
        homepage_text = enrichment_data["homepage"]["text_content"].lower()
        enrichment_data["signals"].update(self.detect_signals(homepage_text))

        # Find key pages
        links = soup.find_all('a', href=True)
        key_pages = self.find_key_pages(links, response.url)

        # Store for now, will scrape key pages in follow-up requests
        response.meta['enrichment_data'] = enrichment_data
        response.meta['key_pages'] = key_pages

        # Follow about page
        if key_pages.get('about'):
            yield scrapy.Request(
                url=key_pages['about'],
                callback=self.parse_about_page,
                meta=response.meta,
                errback=self.handle_error
            )

        # Follow jobs/careers page
        if key_pages.get('jobs'):
            yield scrapy.Request(
                url=key_pages['jobs'],
                callback=self.parse_jobs_page,
                meta=response.meta,
                errback=self.handle_error
            )

        # Follow products page
        if key_pages.get('products'):
            yield scrapy.Request(
                url=key_pages['products'],
                callback=self.parse_products_page,
                meta=response.meta,
                errback=self.handle_error
            )

        # Follow news page
        if key_pages.get('news'):
            yield scrapy.Request(
                url=key_pages['news'],
                callback=self.parse_news_page,
                meta=response.meta,
                errback=self.handle_error
            )

        # Search LinkedIn (will be implemented with Apify)
        yield self.search_linkedin(company_name, response.meta)

        # Search Facebook (will be implemented)
        yield self.search_facebook(company_name, response.meta)

        # Return enrichment data
        yield enrichment_data

    def parse_about_page(self, response: Response):
        """Parse About/Team page."""
        soup = BeautifulSoup(response.text, 'html.parser')
        text_content = soup.get_text(separator=" ", strip=True)

        enrichment_data = response.meta['enrichment_data']
        enrichment_data['about'] = {
            "url": response.url,
            "text": text_content[:3000],  # First 3000 chars
        }

        # Detect more signals
        signals = self.detect_signals(text_content.lower())
        enrichment_data['signals'].update(signals)

        # Try to extract employee count
        employee_count = self.extract_employee_count(text_content)
        if employee_count:
            enrichment_data['signals']['employee_count'] = employee_count

        return enrichment_data

    def parse_jobs_page(self, response: Response):
        """Parse Jobs/Careers page."""
        soup = BeautifulSoup(response.text, 'html.parser')
        text_content = soup.get_text(separator=" ", strip=True)

        enrichment_data = response.meta['enrichment_data']
        enrichment_data['jobs'] = {
            "url": response.url,
            "text": text_content[:3000],
        }

        # Detect hiring signals
        job_openings = self.extract_job_openings(text_content)
        enrichment_data['signals']['job_openings'] = job_openings

        if job_openings:
            enrichment_data['signals']['is_hiring_engineers'] = True

        return enrichment_data

    def parse_products_page(self, response: Response):
        """Parse Products/Services page."""
        soup = BeautifulSoup(response.text, 'html.parser')
        text_content = soup.get_text(separator=" ", strip=True)

        enrichment_data = response.meta['enrichment_data']
        enrichment_data['products'] = {
            "url": response.url,
            "text": text_content[:3000],
        }

        # Detect engineering/manufacturing signals
        signals = self.detect_signals(text_content.lower())
        enrichment_data['signals'].update(signals)

        return enrichment_data

    def parse_news_page(self, response: Response):
        """Parse News/Press page."""
        soup = BeautifulSoup(response.text, 'html.parser')
        text_content = soup.get_text(separator=" ", strip=True)

        enrichment_data = response.meta['enrichment_data']
        enrichment_data['news'] = {
            "url": response.url,
            "text": text_content[:3000],
        }

        return enrichment_data

    def search_linkedin(self, company_name: str, meta: dict):
        """
        Search for company on LinkedIn.
        Will use Apify LinkedIn Company Scraper.
        """
        # Placeholder - will be implemented with Apify
        meta['enrichment_data']['social_media']['linkedin'] = {
            "url": None,
            "employees": None,
            "description": None,
            "industry": None
        }
        return meta['enrichment_data']

    def search_facebook(self, company_name: str, meta: dict):
        """
        Search for company on Facebook.
        Extract recent posts and activity.
        """
        # Placeholder - will be implemented
        meta['enrichment_data']['social_media']['facebook'] = {
            "url": None,
            "recent_posts": []
        }
        return meta['enrichment_data']

    # ========== SIGNAL DETECTION ==========

    def detect_signals(self, text: str) -> Dict[str, Any]:
        """
        Detect buying signals from text content.
        Returns dict with boolean flags.
        """
        text_lower = text.lower()

        return {
            "has_engineering": any(kw.lower() in text_lower for kw in self.ENGINEERING_KEYWORDS),
            "has_cad_software": any(kw.lower() in text_lower for kw in ["CAD", "solidworks", "autocad", "catia", "CAO"]),
            "is_hiring_engineers": any(kw.lower() in text_lower for kw in self.HIRING_KEYWORDS),
            "has_iso_certification": any(kw.lower() in text_lower for kw in self.ISO_KEYWORDS),
            "is_exporter": any(kw.lower() in text_lower for kw in self.EXPORT_KEYWORDS),
            "is_multinational": any(kw.lower() in text_lower for kw in self.MULTINATIONAL_KEYWORDS),
        }

    def extract_employee_count(self, text: str) -> Optional[int]:
        """Extract employee count from text like '150 employees' or '50 collaborateurs'."""
        patterns = [
            r'(\d+)\s+(?:employees|employés|collaborateurs|salariés|personnes)',
            r'(?:team of|équipe de)\s+(\d+)',
            r'(\d+)\s+(?:member team|person team)'
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1))

        return None

    def extract_job_openings(self, text: str) -> List[Dict[str, str]]:
        """
        Extract job opening titles from jobs page.
        Returns list of dicts with title and detected role type.
        """
        job_openings = []

        # Look for job titles
        job_patterns = [
            r'(?:ingénieur|engineer|designer|dessinateur|technicien)\s+[\w\s]+',
            r'(?:mechanical|electrical|software)\s+engineer',
            r'CAD\s+designer',
            r'bureau\s+d\'études',
        ]

        for pattern in job_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                title = match.group(0).strip()
                job_openings.append({
                    "title": title,
                    "is_engineering": True
                })

        # Deduplicate
        seen = set()
        unique_jobs = []
        for job in job_openings:
            title_lower = job['title'].lower()
            if title_lower not in seen:
                seen.add(title_lower)
                unique_jobs.append(job)

        return unique_jobs[:10]  # Max 10

    # ========== HELPERS ==========

    def find_key_pages(self, links: List, base_url: str) -> Dict[str, str]:
        """
        Find key pages from navigation links.
        Returns dict with about, jobs, products, news URLs.
        """
        key_pages = {}

        about_keywords = ['about', 'qui-sommes-nous', 'a-propos', 'notre-entreprise', 'equipe', 'team']
        jobs_keywords = ['careers', 'jobs', 'recrutement', 'offres', 'emploi', 'carriere']
        products_keywords = ['products', 'services', 'produits', 'solutions', 'realisations']
        news_keywords = ['news', 'actualites', 'blog', 'presse', 'press']

        for link in links:
            href = link.get('href', '')
            text = link.get_text(strip=True).lower()

            # Make absolute URL
            absolute_url = urljoin(base_url, href)

            # Check if it's same domain
            if urlparse(absolute_url).netloc != urlparse(base_url).netloc:
                continue

            # Categorize
            href_lower = href.lower()

            if not key_pages.get('about') and any(kw in href_lower or kw in text for kw in about_keywords):
                key_pages['about'] = absolute_url

            if not key_pages.get('jobs') and any(kw in href_lower or kw in text for kw in jobs_keywords):
                key_pages['jobs'] = absolute_url

            if not key_pages.get('products') and any(kw in href_lower or kw in text for kw in products_keywords):
                key_pages['products'] = absolute_url

            if not key_pages.get('news') and any(kw in href_lower or kw in text for kw in news_keywords):
                key_pages['news'] = absolute_url

        return key_pages

    def extract_meta_description(self, soup: BeautifulSoup) -> str:
        """Extract meta description from page."""
        meta = soup.find('meta', attrs={'name': 'description'})
        if meta and meta.get('content'):
            return meta['content'].strip()

        meta = soup.find('meta', attrs={'property': 'og:description'})
        if meta and meta.get('content'):
            return meta['content'].strip()

        return ""

    def handle_error(self, failure):
        """Handle request errors."""
        self.logger.error(f"❌ Error: {failure.value}")

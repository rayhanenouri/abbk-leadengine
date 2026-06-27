#!/usr/bin/env python3
"""
Deep Company Enricher

Scrapes a company's entire web presence to extract real business intelligence:
- Website: all pages (about, team, products, news, jobs)
- LinkedIn: company page, employee count, recent posts
- Facebook: page and recent activity
- Detects: engineering, CAD, hiring, ISO, export signals

This is the CORE VALUE of the platform.
"""

import re
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse
from datetime import datetime

import httpx
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential


class DeepCompanyEnricher:
    """
    Deep enrichment for a single company.
    Scrapes all available online data.
    """

    # Signal detection keywords
    ENGINEERING_KEYWORDS = [
        "CAD", "solidworks", "simulation", "FEA", "CFD", "conception",
        "bureau d'études", "mechanical design", "3D modeling", "product design",
        "engineering", "ingénierie", "mécanique", "électrique",
        "manufacturing", "fabrication", "CAO", "DAO", "simulation numérique",
        "calcul de structure", "AutoCAD", "CATIA", "Inventor", "SolidEdge", "NX", "Creo"
    ]

    HIRING_KEYWORDS = [
        "recrutement", "recrute", "hiring", "job opening", "career",
        "offre d'emploi", "ingénieur", "engineer", "designer", "dessinateur",
        "technicien", "bureau d'études", "R&D", "conception", "CAD designer"
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

    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers={
                "User-Agent": "ABBK-LeadEngine-Bot/1.0 (Sales Intelligence; +https://abbk-tn.com)"
            }
        )

    async def enrich_company(
        self,
        company_id: int,
        company_name: str,
        website: str
    ) -> Dict[str, Any]:
        """
        Perform deep enrichment on a company.

        Returns comprehensive intelligence dict.
        """

        enrichment = {
            "company_id": company_id,
            "company_name": company_name,
            "website": website,
            "enriched_at": datetime.utcnow().isoformat(),
            "homepage": {},
            "about": {},
            "team": {},
            "products": {},
            "news": {},
            "jobs": {},
            "social_media": {
                "linkedin": {},
                "facebook": {}
            },
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

        # Step 1: Scrape homepage
        homepage_data = await self.scrape_homepage(website)
        if not homepage_data:
            return enrichment

        enrichment["homepage"] = homepage_data

        # Detect signals from homepage
        enrichment["signals"].update(
            self.detect_signals(homepage_data.get("text_content", ""))
        )

        # Step 2: Find and scrape key pages
        key_pages = homepage_data.get("key_pages", {})

        if key_pages.get("about"):
            about_data = await self.scrape_page(key_pages["about"])
            if about_data:
                enrichment["about"] = about_data
                enrichment["signals"].update(self.detect_signals(about_data.get("text", "")))

                # Try to extract employee count from about page
                employee_count = self.extract_employee_count(about_data.get("text", ""))
                if employee_count:
                    enrichment["signals"]["employee_count"] = employee_count

        if key_pages.get("jobs"):
            jobs_data = await self.scrape_page(key_pages["jobs"])
            if jobs_data:
                enrichment["jobs"] = jobs_data

                # Extract job openings
                job_openings = self.extract_job_openings(jobs_data.get("text", ""))
                if job_openings:
                    enrichment["signals"]["job_openings"] = job_openings
                    enrichment["signals"]["is_hiring_engineers"] = True

        if key_pages.get("products"):
            products_data = await self.scrape_page(key_pages["products"])
            if products_data:
                enrichment["products"] = products_data
                enrichment["signals"].update(self.detect_signals(products_data.get("text", "")))

        if key_pages.get("news"):
            news_data = await self.scrape_page(key_pages["news"])
            if news_data:
                enrichment["news"] = news_data

        # Step 3: Search LinkedIn (placeholder - will use Apify)
        linkedin_data = await self.search_linkedin(company_name)
        enrichment["social_media"]["linkedin"] = linkedin_data

        # Step 4: Search Facebook (placeholder)
        facebook_data = await self.search_facebook(company_name)
        enrichment["social_media"]["facebook"] = facebook_data

        return enrichment

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def scrape_homepage(self, url: str) -> Optional[Dict[str, Any]]:
        """Scrape company homepage."""

        try:
            response = await self.client.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract basic info
            data = {
                "url": url,
                "title": soup.title.text.strip() if soup.title else "",
                "meta_description": self._extract_meta_description(soup),
                "text_content": soup.get_text(separator=" ", strip=True)[:5000],
                "key_pages": {}
            }

            # Find key pages
            links = soup.find_all('a', href=True)
            data["key_pages"] = self._find_key_pages(links, url)

            return data

        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None

    @retry(stop=stop_after_attempt(2), wait=wait_exponential(min=1, max=5))
    async def scrape_page(self, url: str) -> Optional[Dict[str, Any]]:
        """Scrape a specific page."""

        try:
            response = await self.client.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            return {
                "url": url,
                "title": soup.title.text.strip() if soup.title else "",
                "text": soup.get_text(separator=" ", strip=True)[:3000]
            }

        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None

    async def search_linkedin(self, company_name: str) -> Dict[str, Any]:
        """
        Search LinkedIn for company page.
        Placeholder - will be implemented with Apify LinkedIn Company Scraper.
        """
        # TODO: Implement with Apify
        return {
            "url": None,
            "employees": None,
            "description": None,
            "industry": None,
            "recent_hires": []
        }

    async def search_facebook(self, company_name: str) -> Dict[str, Any]:
        """
        Search Facebook for company page.
        Placeholder - will be implemented.
        """
        # TODO: Implement Facebook scraping
        return {
            "url": None,
            "recent_posts": []
        }

    # ========== SIGNAL DETECTION ==========

    def detect_signals(self, text: str) -> Dict[str, bool]:
        """Detect buying signals from text content."""

        text_lower = text.lower()

        return {
            "has_engineering": any(kw.lower() in text_lower for kw in self.ENGINEERING_KEYWORDS),
            "has_cad_software": any(kw.lower() in text_lower for kw in ["CAD", "solidworks", "autocad", "catia", "CAO", "inventor", "creo"]),
            "is_hiring_engineers": any(kw.lower() in text_lower for kw in self.HIRING_KEYWORDS),
            "has_iso_certification": any(kw.lower() in text_lower for kw in self.ISO_KEYWORDS),
            "is_exporter": any(kw.lower() in text_lower for kw in self.EXPORT_KEYWORDS),
            "is_multinational": any(kw.lower() in text_lower for kw in self.MULTINATIONAL_KEYWORDS),
        }

    def extract_employee_count(self, text: str) -> Optional[int]:
        """Extract employee count from text."""

        patterns = [
            r'(\d+)\s+(?:employees|employés|collaborateurs|salariés|personnes)',
            r'(?:team of|équipe de)\s+(\d+)',
            r'(\d+)\s+(?:member team|person team)',
            r'effectif[:\s]+(\d+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                count = int(match.group(1))
                # Sanity check (1-100,000 employees)
                if 1 <= count <= 100000:
                    return count

        return None

    def extract_job_openings(self, text: str) -> List[Dict[str, str]]:
        """Extract job openings from jobs page text."""

        job_openings = []

        # Patterns for engineering job titles
        job_patterns = [
            r'(?:ingénieur|engineer|designer|dessinateur|technicien)\s+[\w\sé\-]+',
            r'(?:mechanical|electrical|software|civil|industrial)\s+engineer',
            r'CAD\s+(?:designer|engineer)',
            r'bureau\s+d\'études',
            r'responsable\s+(?:technique|production|R&D)',
        ]

        for pattern in job_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                title = match.group(0).strip()

                # Filter out common false positives
                if len(title) < 10 or len(title) > 100:
                    continue

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

        return unique_jobs[:10]  # Max 10 jobs

    # ========== HELPERS ==========

    def _find_key_pages(self, links: List, base_url: str) -> Dict[str, str]:
        """Find about, jobs, products, news pages from nav links."""

        key_pages = {}

        about_keywords = ['about', 'qui-sommes-nous', 'a-propos', 'notre-entreprise', 'equipe', 'team', 'société', 'company']
        jobs_keywords = ['careers', 'jobs', 'recrutement', 'offres', 'emploi', 'carriere', 'rejoignez']
        products_keywords = ['products', 'services', 'produits', 'solutions', 'realisations', 'portfolio']
        news_keywords = ['news', 'actualites', 'blog', 'presse', 'press', 'events']

        for link in links:
            href = link.get('href', '')
            text = link.get_text(strip=True).lower()

            if not href:
                continue

            # Make absolute URL
            absolute_url = urljoin(base_url, href)

            # Check if same domain
            if urlparse(absolute_url).netloc != urlparse(base_url).netloc:
                continue

            href_lower = href.lower()

            # Categorize
            if not key_pages.get('about') and any(kw in href_lower or kw in text for kw in about_keywords):
                key_pages['about'] = absolute_url

            if not key_pages.get('jobs') and any(kw in href_lower or kw in text for kw in jobs_keywords):
                key_pages['jobs'] = absolute_url

            if not key_pages.get('products') and any(kw in href_lower or kw in text for kw in products_keywords):
                key_pages['products'] = absolute_url

            if not key_pages.get('news') and any(kw in href_lower or kw in text for kw in news_keywords):
                key_pages['news'] = absolute_url

        return key_pages

    def _extract_meta_description(self, soup: BeautifulSoup) -> str:
        """Extract meta description."""

        meta = soup.find('meta', attrs={'name': 'description'})
        if meta and meta.get('content'):
            return meta['content'].strip()

        meta = soup.find('meta', attrs={'property': 'og:description'})
        if meta and meta.get('content'):
            return meta['content'].strip()

        return ""

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()

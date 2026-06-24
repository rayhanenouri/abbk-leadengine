"""
Universal AI-Powered Web Scraper

Uses Playwright for rendering + Claude API for intelligent extraction.
Works on ANY website without CSS selectors.

This is the CORRECT approach for production:
- Future-proof (AI adapts to HTML changes)
- No brittle CSS selectors
- Handles JavaScript-heavy sites
- Extracts structured data from any page
"""
import asyncio
import logging
from typing import List, Dict, Any, Optional
from playwright.async_api import async_playwright, Browser, Page
import anthropic
import os
from datetime import datetime

logger = logging.getLogger(__name__)


class UniversalScraper:
    """
    AI-powered universal scraper using Playwright + Claude API.

    No CSS selectors needed - Claude extracts structured data from HTML.
    """

    def __init__(self, anthropic_api_key: Optional[str] = None):
        self.anthropic_api_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY must be set in environment")

        self.claude_client = anthropic.Anthropic(api_key=self.anthropic_api_key)

    async def scrape_business_directory(self, url: str, source_name: str) -> List[Dict[str, Any]]:
        """
        Scrape a business directory URL and extract company data.

        Args:
            url: URL to scrape
            source_name: Name of the source (e.g., "mecatronic.tn")

        Returns:
            List of company dictionaries with fields:
            - company_name
            - website
            - phone
            - sector
            - city
            - description
            - country
            - source
            - source_url
        """
        logger.info(f"Scraping business directory: {url}")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            try:
                # Navigate and wait for content
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_timeout(2000)  # Wait for dynamic content

                # Get page HTML
                html_content = await page.content()

                # Extract text content for better Claude processing
                text_content = await page.evaluate("""
                    () => {
                        // Remove script and style tags
                        const scripts = document.querySelectorAll('script, style, nav, footer, header');
                        scripts.forEach(s => s.remove());
                        return document.body.innerText;
                    }
                """)

                await browser.close()

                # Use Claude to extract structured company data
                companies = await self._extract_companies_with_claude(
                    html_content=html_content[:50000],  # Limit to 50K chars
                    text_content=text_content[:30000],
                    url=url,
                    source_name=source_name
                )

                logger.info(f"Extracted {len(companies)} companies from {url}")
                return companies

            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")
                await browser.close()
                return []

    async def scrape_job_board(self, url: str, source_name: str) -> List[Dict[str, Any]]:
        """
        Scrape a job board URL and extract hiring signals.

        Returns job postings with:
        - signal_type: "new_hire"
        - company_name
        - job_title
        - location
        - source
        - source_url
        - detail
        """
        logger.info(f"Scraping job board: {url}")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_timeout(2000)

                # Get page content
                text_content = await page.evaluate("() => document.body.innerText")

                await browser.close()

                # Use Claude to extract job postings
                jobs = await self._extract_jobs_with_claude(
                    text_content=text_content[:30000],
                    url=url,
                    source_name=source_name
                )

                logger.info(f"Extracted {len(jobs)} job postings from {url}")
                return jobs

            except Exception as e:
                logger.error(f"Error scraping job board {url}: {e}")
                await browser.close()
                return []

    async def scrape_news_article(self, url: str, source_name: str) -> List[Dict[str, Any]]:
        """
        Scrape a news article and extract company signals.

        Returns signals with:
        - signal_type: funding, news, export_signal, audit_signal, multinational_signal
        - company_name
        - title
        - detail
        - source
        - source_url
        """
        logger.info(f"Scraping news article: {url}")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_timeout(2000)

                text_content = await page.evaluate("() => document.body.innerText")

                await browser.close()

                # Use Claude to extract company signals from news
                signals = await self._extract_news_signals_with_claude(
                    text_content=text_content[:30000],
                    url=url,
                    source_name=source_name
                )

                logger.info(f"Extracted {len(signals)} signals from {url}")
                return signals

            except Exception as e:
                logger.error(f"Error scraping news {url}: {e}")
                await browser.close()
                return []

    async def _extract_companies_with_claude(
        self,
        html_content: str,
        text_content: str,
        url: str,
        source_name: str
    ) -> List[Dict[str, Any]]:
        """
        Use Claude API to extract company data from HTML/text.
        """
        prompt = f"""Extract all company information from this business directory page.

URL: {url}
Source: {source_name}

Return a JSON array of companies. For each company, extract:
- company_name (required)
- website (URL if available)
- phone (phone number if available)
- sector (industry/sector if mentioned)
- city (location/city if mentioned)
- description (brief description if available)

Focus on engineering, manufacturing, industrial, automotive companies.

Text content:
{text_content}

Return ONLY valid JSON array, no markdown, no explanations:
[{{"company_name": "...", "website": "...", ...}}, ...]

If no companies found, return empty array: []
"""

        try:
            response = self.claude_client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )

            # Parse Claude response
            import json
            response_text = response.content[0].text.strip()

            # Remove markdown code blocks if present
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]

            companies = json.loads(response_text)

            # Add metadata
            for company in companies:
                company["country"] = "Tunisia"  # Default for most sources
                company["source"] = source_name
                company["source_url"] = url

                # Detect country from URL or company name
                if "south-africa" in url.lower() or ".za" in url.lower():
                    company["country"] = "South Africa"
                elif "nigeria" in url.lower() or "lagos" in url.lower():
                    company["country"] = "Nigeria"
                elif "tanzania" in url.lower():
                    company["country"] = "Tanzania"

            return companies

        except Exception as e:
            logger.error(f"Error extracting companies with Claude: {e}")
            return []

    async def _extract_jobs_with_claude(
        self,
        text_content: str,
        url: str,
        source_name: str
    ) -> List[Dict[str, Any]]:
        """
        Use Claude API to extract job postings.
        """
        prompt = f"""Extract all engineering job postings from this job board page.

URL: {url}
Source: {source_name}

Return a JSON array of jobs. For each job, extract:
- company_name (required - the hiring company)
- job_title (required - the position title)
- location (city/location if mentioned)

Focus ONLY on engineering jobs:
- Ingénieur conception, CAD designer, Bureau d'études
- Mechanical engineer, Simulation engineer
- Manufacturing, R&D, SOLIDWORKS

Text content:
{text_content}

Return ONLY valid JSON array:
[{{"company_name": "...", "job_title": "...", "location": "..."}}, ...]

If no relevant jobs found, return: []
"""

        try:
            response = self.claude_client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )

            import json
            response_text = response.content[0].text.strip()

            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]

            jobs = json.loads(response_text)

            # Add metadata
            for job in jobs:
                job["signal_type"] = "new_hire"
                job["source"] = source_name
                job["source_url"] = url
                job["detail"] = f"Hiring {job.get('job_title', 'engineering role')}"

            return jobs

        except Exception as e:
            logger.error(f"Error extracting jobs with Claude: {e}")
            return []

    async def _extract_news_signals_with_claude(
        self,
        text_content: str,
        url: str,
        source_name: str
    ) -> List[Dict[str, Any]]:
        """
        Use Claude API to extract company signals from news articles.
        """
        prompt = f"""Extract business signals from this news article.

URL: {url}

Identify companies mentioned and their signals:
- funding (investment, financing, levée de fonds)
- export_signal (international contracts, exports)
- audit_signal (ISO certification, audit, compliance)
- multinational_signal (subsidiary, international group)
- news (expansion, growth, new factory)

Return JSON array:
[{{
  "company_name": "...",
  "signal_type": "funding",
  "title": "brief title",
  "detail": "what happened"
}}, ...]

Text:
{text_content}

Return ONLY valid JSON array or []:
"""

        try:
            response = self.claude_client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )

            import json
            response_text = response.content[0].text.strip()

            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]

            signals = json.loads(response_text)

            # Add metadata
            for signal in signals:
                signal["source"] = source_name
                signal["source_url"] = url
                signal["detected_at"] = datetime.utcnow().isoformat()

            return signals

        except Exception as e:
            logger.error(f"Error extracting news signals with Claude: {e}")
            return []


# Convenience functions
async def scrape_url(url: str, url_type: str = "directory") -> List[Dict[str, Any]]:
    """
    Scrape a URL and return extracted data.

    Args:
        url: URL to scrape
        url_type: "directory", "jobs", or "news"

    Returns:
        List of extracted items (companies, jobs, or signals)
    """
    scraper = UniversalScraper()

    # Detect source name from URL
    from urllib.parse import urlparse
    domain = urlparse(url).netloc

    if url_type == "directory":
        return await scraper.scrape_business_directory(url, domain)
    elif url_type == "jobs":
        return await scraper.scrape_job_board(url, domain)
    elif url_type == "news":
        return await scraper.scrape_news_article(url, domain)
    else:
        raise ValueError(f"Unknown url_type: {url_type}")

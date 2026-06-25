"""
Simple web scraper without AI - works immediately.
Uses Playwright + basic text extraction.

Use this until ANTHROPIC_API_KEY is added to .env
"""
import asyncio
import logging
import re
from typing import List, Dict, Any
from playwright.async_api import async_playwright
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


async def scrape_directory_simple(url: str, source_name: str) -> List[Dict[str, Any]]:
    """
    Simple directory scraper - extracts text and finds company-like patterns.
    No AI needed - works immediately.
    """
    logger.info(f"Scraping directory (simple mode): {url}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(2000)

            # Get all text
            text = await page.evaluate("() => document.body.innerText")

            # Get all links
            links = await page.evaluate("""
                () => {
                    const links = Array.from(document.querySelectorAll('a[href]'));
                    return links.map(a => ({
                        text: a.innerText.trim(),
                        href: a.href
                    })).filter(l => l.text && l.text.length > 2 && l.text.length < 100);
                }
            """)

            await browser.close()

            # Extract company-like names from links
            companies = []
            seen = set()

            for link in links[:100]:  # Limit to first 100 links
                name = link['text'].strip()
                href = link['href']

                # Skip navigation/common words
                if name.lower() in ['accueil', 'home', 'contact', 'about', 'login', 'register']:
                    continue

                # Look for company patterns
                if len(name) > 3 and (
                    any(word in name.lower() for word in ['sarl', 'sa', 'group', 'engineering', 'industries', 'technologies']) or
                    (len(name.split()) >= 2 and name[0].isupper())
                ):
                    if name not in seen:
                        seen.add(name)

                        # Detect if link looks like a website
                        website = None
                        if 'http' in href and source_name not in href:
                            website = href

                        companies.append({
                            'company_name': name,
                            'website': website,
                            'country': 'Tunisia',
                            'source': source_name,
                            'source_url': url,
                        })

            logger.info(f"Found {len(companies)} potential companies from {url}")
            return companies[:50]  # Max 50 per source

        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            await browser.close()
            return []


async def scrape_jobs_simple(url: str, source_name: str) -> List[Dict[str, Any]]:
    """
    Simple job board scraper.
    """
    logger.info(f"Scraping jobs (simple mode): {url}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(2000)

            text = await page.evaluate("() => document.body.innerText")

            await browser.close()

            # Find engineering keywords
            engineering_keywords = ['ingénieur', 'engineer', 'cad', 'solidworks', 'mechanical', 'design', 'bureau']

            jobs = []
            lines = text.split('\n')

            for i, line in enumerate(lines[:500]):  # Check first 500 lines
                line_lower = line.lower()

                # If line contains engineering keyword
                if any(kw in line_lower for kw in engineering_keywords):
                    # Try to find company name in nearby lines
                    company_name = None
                    for j in range(max(0, i-3), min(len(lines), i+3)):
                        nearby_line = lines[j].strip()
                        if len(nearby_line) > 5 and len(nearby_line) < 60:
                            # Looks like a company name
                            if any(c.isupper() for c in nearby_line):
                                company_name = nearby_line
                                break

                    if company_name:
                        jobs.append({
                            'signal_type': 'new_hire',
                            'company_name': company_name,
                            'job_title': line.strip()[:200],
                            'source': source_name,
                            'source_url': url,
                            'detail': f"Hiring {line.strip()[:100]}",
                        })

            # Deduplicate
            unique_jobs = []
            seen_companies = set()
            for job in jobs:
                if job['company_name'] not in seen_companies:
                    seen_companies.add(job['company_name'])
                    unique_jobs.append(job)

            logger.info(f"Found {len(unique_jobs)} job signals from {url}")
            return unique_jobs[:30]  # Max 30 per source

        except Exception as e:
            logger.error(f"Error scraping jobs {url}: {e}")
            await browser.close()
            return []


async def scrape_url_simple(url: str, url_type: str = "directory") -> List[Dict[str, Any]]:
    """
    Simple scraper - works without AI.
    """
    domain = urlparse(url).netloc.replace('www.', '')

    if url_type == "directory" or url_type == "training":
        return await scrape_directory_simple(url, domain)
    elif url_type == "jobs":
        return await scrape_jobs_simple(url, domain)
    elif url_type == "news":
        # For news, just return empty for now
        return []
    else:
        return []

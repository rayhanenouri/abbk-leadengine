"""
PROPER Web Scraper - Site-specific extraction logic
Extracts REAL company data from each verified source
"""
import asyncio
import logging
import re
from typing import List, Dict, Any
from playwright.async_api import async_playwright
from urllib.parse import urlparse
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


async def scrape_taa_tn(url: str) -> List[Dict[str, Any]]:
    """
    Scrape TAA (Tunisian Automotive Association) members.
    URL: https://taa.tn/fr/membres

    Structure: <img alt="COMPANY NAME" /> inside .membre-card
    """
    logger.info(f"Scraping TAA members from {url}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(2000)

            html = await page.content()
            await browser.close()

            soup = BeautifulSoup(html, 'html.parser')
            companies = []

            # Find all membre-card divs with images
            membre_cards = soup.find_all('div', class_='membre-card')

            for card in membre_cards:
                img = card.find('img', class_='membre-logo')
                if img and img.get('alt'):
                    company_name = img.get('alt').strip()

                    # Skip if empty or too short
                    if len(company_name) < 3:
                        continue

                    # Get detail link if available
                    link = card.find('a')
                    detail_url = None
                    if link and link.get('href'):
                        detail_url = f"https://taa.tn{link.get('href')}"

                    companies.append({
                        'company_name': company_name,
                        'website': detail_url,
                        'country': 'Tunisia',
                        'sector': 'Automotive',
                        'source': 'taa.tn',
                        'source_url': url,
                    })

            logger.info(f"Found {len(companies)} companies from TAA")
            return companies

        except Exception as e:
            logger.error(f"Error scraping TAA: {e}")
            await browser.close()
            return []


async def scrape_mecatronic_tn(url: str) -> List[Dict[str, Any]]:
    """
    Scrape Mecatronic members.
    URL: https://mecatronic.tn/membres/
    """
    logger.info(f"Scraping Mecatronic members from {url}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(3000)

            html = await page.content()
            await browser.close()

            soup = BeautifulSoup(html, 'html.parser')
            companies = []

            # Look for company listings - adapt based on actual structure
            # Common patterns: h2, h3, .company-name, .member-name, etc.
            company_elements = soup.find_all(['h2', 'h3', 'h4'], class_=re.compile(r'member|company|entreprise', re.I))

            # Also try finding links in member sections
            if not company_elements:
                member_sections = soup.find_all(['div', 'li'], class_=re.compile(r'member|company', re.I))
                for section in member_sections:
                    name_elem = section.find(['h2', 'h3', 'h4', 'strong', 'a'])
                    if name_elem:
                        company_elements.append(name_elem)

            for elem in company_elements:
                company_name = elem.get_text().strip()

                # Clean and validate
                if len(company_name) < 3 or len(company_name) > 100:
                    continue

                # Skip common non-company words
                skip_words = ['membre', 'members', 'nos membres', 'liste', 'accueil']
                if any(word in company_name.lower() for word in skip_words):
                    continue

                companies.append({
                    'company_name': company_name,
                    'country': 'Tunisia',
                    'sector': 'Engineering/Manufacturing',
                    'source': 'mecatronic.tn',
                    'source_url': url,
                })

            logger.info(f"Found {len(companies)} companies from Mecatronic")
            return companies

        except Exception as e:
            logger.error(f"Error scraping Mecatronic: {e}")
            await browser.close()
            return []


async def scrape_tunisieindustrie(url: str) -> List[Dict[str, Any]]:
    """
    Scrape Tunisia Industry database.
    URLs:
    - https://www.tunisieindustrie.nat.tn/fr/dbi.asp
    - https://www.tunisieindustrie.nat.tn/fr/dbs.asp
    """
    logger.info(f"Scraping Tunisia Industry from {url}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(3000)

            html = await page.content()
            await browser.close()

            soup = BeautifulSoup(html, 'html.parser')
            companies = []

            # Tunisia Industry typically has table structures
            rows = soup.find_all('tr')

            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    # First cell usually has company name
                    company_name = cells[0].get_text().strip()

                    if len(company_name) > 3 and len(company_name) < 100:
                        # Check if looks like a company (has capital letters or specific words)
                        if any(c.isupper() for c in company_name):
                            companies.append({
                                'company_name': company_name,
                                'country': 'Tunisia',
                                'source': 'tunisieindustrie.nat.tn',
                                'source_url': url,
                            })

            # Deduplicate
            seen = set()
            unique_companies = []
            for company in companies:
                if company['company_name'] not in seen:
                    seen.add(company['company_name'])
                    unique_companies.append(company)

            logger.info(f"Found {len(unique_companies)} companies from Tunisia Industry")
            return unique_companies

        except Exception as e:
            logger.error(f"Error scraping Tunisia Industry: {e}")
            await browser.close()
            return []


async def scrape_url_proper(url: str) -> List[Dict[str, Any]]:
    """
    Route to proper scraper based on URL.
    """
    domain = urlparse(url).netloc.lower()

    if 'taa.tn' in domain:
        return await scrape_taa_tn(url)
    elif 'mecatronic.tn' in domain:
        return await scrape_mecatronic_tn(url)
    elif 'tunisieindustrie' in domain:
        return await scrape_tunisieindustrie(url)
    else:
        logger.warning(f"No specific scraper for {domain}, skipping")
        return []

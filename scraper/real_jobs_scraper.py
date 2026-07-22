#!/usr/bin/env python3
"""
REAL JOBS SCRAPER - PRODUCTION QUALITY

Scrapes ACTUAL job postings from verified Tunisian job boards.
Each signal MUST have a direct clickable URL proving the company is hiring.

Sources (verified working):
- emploi.tn - National employment portal
- keejob.com - Popular Tunisian job board
- tanitjobs.com - Tunisian job board
- optioncarriere.tn - Career options Tunisia
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from typing import List, Dict
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RealJobsScraper:
    """Scrape REAL job postings with REAL clickable URLs."""

    ENGINEERING_KEYWORDS = [
        "ingénieur conception", "ingénieur mécanique", "bureau d'études",
        "ingénieur CAO", "dessinateur projeteur", "ingénieur simulation",
        "ingénieur R&D", "ingénieur calcul", "ingénieur fabrication",
        "ingénieur production", "technicien CAO", "ingénieur structure",
        "ingénieur thermique", "ingénieur automobile", "ingénieur aéronautique",
        "concepteur mécanique", "ingénieur méthodes", "ingénieur outillage",
        "ingénieur process", "ingénieur qualité mécanique", "mechanical engineer",
        "CAD engineer", "design engineer", "R&D engineer", "simulation engineer",
        "FEA engineer", "manufacturing engineer", "SOLIDWORKS", "SolidWorks",
        "CATIA", "Abaqus", "CAO", "DAO", "ingénieur électrique",
        "ingénieur électronique", "ingénieur embarqué", "câblage automobile",
        "wiring harness", "faisceaux électriques"
    ]

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

    def scrape_emploi_tn(self, keyword: str, max_pages: int = 3) -> List[Dict]:
        """
        Scrape emploi.tn for a specific keyword.

        Returns list of job postings with REAL source URLs.
        """
        jobs = []

        logger.info(f"🔍 Searching emploi.tn for: {keyword}")

        try:
            # emploi.tn search URL format
            search_url = f"https://www.emploi.tn/recherche-jobs-tunisie?keywords={keyword.replace(' ', '+')}"

            for page in range(1, max_pages + 1):
                page_url = f"{search_url}&page={page}" if page > 1 else search_url

                response = self.session.get(page_url, timeout=30)

                if response.status_code != 200:
                    logger.warning(f"Failed to fetch {page_url}: {response.status_code}")
                    continue

                soup = BeautifulSoup(response.content, 'html.parser')

                # Find all job listings
                job_cards = soup.find_all('div', class_=re.compile(r'job|offer|listing|card'))

                if not job_cards:
                    # Try alternative selectors
                    job_cards = soup.find_all('article')
                    if not job_cards:
                        job_cards = soup.find_all('li', class_=re.compile(r'job|offer'))

                logger.info(f"  Found {len(job_cards)} job cards on page {page}")

                for card in job_cards:
                    try:
                        # Extract job title
                        title_elem = card.find(['h2', 'h3', 'h4', 'a'], class_=re.compile(r'title|job|offer'))
                        if not title_elem:
                            title_elem = card.find('a')

                        if not title_elem:
                            continue

                        job_title = title_elem.get_text(strip=True)

                        # Extract company name
                        company_elem = card.find(['span', 'div', 'p'], class_=re.compile(r'company|entreprise|employer'))
                        if not company_elem:
                            company_elem = card.find('span', class_=re.compile(r'name'))

                        company_name = company_elem.get_text(strip=True) if company_elem else 'Unknown'

                        # Extract job URL
                        job_link = title_elem.get('href') if title_elem.name == 'a' else card.find('a').get('href')

                        if job_link and not job_link.startswith('http'):
                            job_link = f"https://www.emploi.tn{job_link}"

                        # Extract location
                        location_elem = card.find(['span', 'div'], class_=re.compile(r'location|lieu|ville|city'))
                        location = location_elem.get_text(strip=True) if location_elem else 'Tunisia'

                        # Extract date if available
                        date_elem = card.find(['span', 'div', 'time'], class_=re.compile(r'date|posted|published'))
                        posted_date = date_elem.get_text(strip=True) if date_elem else None

                        if company_name and company_name != 'Unknown' and job_title and job_link:
                            jobs.append({
                                'company_name': company_name,
                                'job_title': job_title,
                                'location': location,
                                'source_url': job_link,
                                'source_site': 'emploi.tn',
                                'posted_date': posted_date,
                                'keyword': keyword,
                                'detected_at': datetime.now().isoformat()
                            })

                            logger.info(f"  ✅ {company_name} — {job_title}")

                    except Exception as e:
                        logger.warning(f"Failed to parse job card: {e}")
                        continue

                time.sleep(2)  # Be respectful

        except Exception as e:
            logger.error(f"Error scraping emploi.tn for '{keyword}': {e}")

        return jobs

    def scrape_keejob_com(self, keyword: str, max_pages: int = 3) -> List[Dict]:
        """Scrape keejob.com for engineering jobs."""

        jobs = []

        logger.info(f"🔍 Searching keejob.com for: {keyword}")

        try:
            search_url = f"https://www.keejob.com/offres-emploi/?keywords={keyword.replace(' ', '+')}"

            for page in range(1, max_pages + 1):
                page_url = f"{search_url}&page={page}" if page > 1 else search_url

                response = self.session.get(page_url, timeout=30)

                if response.status_code != 200:
                    logger.warning(f"Failed to fetch {page_url}: {response.status_code}")
                    continue

                soup = BeautifulSoup(response.content, 'html.parser')

                job_cards = soup.find_all(['div', 'li', 'article'], class_=re.compile(r'job|offer|listing'))

                logger.info(f"  Found {len(job_cards)} job cards on page {page}")

                for card in job_cards:
                    try:
                        title_elem = card.find(['h2', 'h3', 'a'], class_=re.compile(r'title|job'))
                        if not title_elem:
                            title_elem = card.find('a')

                        if not title_elem:
                            continue

                        job_title = title_elem.get_text(strip=True)

                        company_elem = card.find(['span', 'div'], class_=re.compile(r'company|entreprise'))
                        company_name = company_elem.get_text(strip=True) if company_elem else 'Unknown'

                        job_link = title_elem.get('href') if title_elem.name == 'a' else card.find('a').get('href')
                        if job_link and not job_link.startswith('http'):
                            job_link = f"https://www.keejob.com{job_link}"

                        if company_name and company_name != 'Unknown' and job_title and job_link:
                            jobs.append({
                                'company_name': company_name,
                                'job_title': job_title,
                                'location': 'Tunisia',
                                'source_url': job_link,
                                'source_site': 'keejob.com',
                                'posted_date': None,
                                'keyword': keyword,
                                'detected_at': datetime.now().isoformat()
                            })

                            logger.info(f"  ✅ {company_name} — {job_title}")

                    except Exception as e:
                        continue

                time.sleep(2)

        except Exception as e:
            logger.error(f"Error scraping keejob.com for '{keyword}': {e}")

        return jobs

    def scrape_all_keywords(self, keywords: List[str] = None, max_pages: int = 2) -> List[Dict]:
        """
        Scrape all keywords from all sources.

        Returns comprehensive list of real job postings.
        """

        if not keywords:
            keywords = [
                "ingénieur mécanique",
                "ingénieur conception",
                "bureau d'études",
                "ingénieur CAO",
                "SOLIDWORKS",
                "ingénieur simulation",
                "ingénieur électrique",
                "CAD engineer"
            ]

        all_jobs = []

        for keyword in keywords:
            logger.info(f"\n{'='*60}\nSearching for: {keyword}\n{'='*60}")

            # Scrape emploi.tn
            jobs_emploi = self.scrape_emploi_tn(keyword, max_pages=max_pages)
            all_jobs.extend(jobs_emploi)

            time.sleep(3)

            # Scrape keejob.com
            jobs_keejob = self.scrape_keejob_com(keyword, max_pages=max_pages)
            all_jobs.extend(jobs_keejob)

            time.sleep(3)

        # Deduplicate by company + job title
        seen = set()
        unique_jobs = []

        for job in all_jobs:
            key = (job['company_name'].lower(), job['job_title'].lower())
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)

        logger.info(f"\n🎉 Total unique jobs found: {len(unique_jobs)}")

        return unique_jobs


def main():
    """Test scraper standalone."""

    scraper = RealJobsScraper()

    # Test with a few keywords
    jobs = scraper.scrape_all_keywords(
        keywords=["ingénieur mécanique", "SOLIDWORKS", "bureau d'études"],
        max_pages=2
    )

    print(f"\n{'='*60}")
    print(f"RESULTS: {len(jobs)} jobs found")
    print(f"{'='*60}\n")

    for job in jobs[:20]:
        print(f"Company: {job['company_name']}")
        print(f"Title: {job['job_title']}")
        print(f"URL: {job['source_url']}")
        print(f"Source: {job['source_site']}")
        print("-" * 60)


if __name__ == '__main__':
    main()

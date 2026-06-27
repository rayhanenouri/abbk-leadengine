#!/usr/bin/env python3
"""
REAL SCRAPING SOLUTION:
1. Find company URLs via Google search
2. Scrape each website for signals
3. Save real detected signals to database
"""

import asyncio
import sys
from pathlib import Path
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime
import re
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.session import AsyncSessionLocal
from app.models.models import Lead, LeadSignal
from sqlalchemy import select

# Signal detection keywords
TRAINING_KEYWORDS = ['formation solidworks', 'training', 'cao', 'cfao', 'iset', 'formation professionnelle']
HIRING_KEYWORDS = ['recrute', 'recrutement', 'candidature', 'postuler', 'carriere', 'offre emploi']
SOLIDWORKS_KEYWORDS = ['solidworks', 'dassault', 'simulia', 'abaqus', '3dexperience']
ENGINEERING_KEYWORDS = ['ingenieur', 'engineer', 'bureau etudes', 'cad', 'cao', 'mechanical']

async def find_company_url(session, company_name):
    """Search Google to find company's official website"""

    # Clean company name for search
    search_query = f"{company_name} Tunisia"
    google_url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        async with session.get(google_url, headers=headers, timeout=15) as response:
            if response.status != 200:
                return None

            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')

            # Find first real URL (not google.com, not wikipedia)
            for link in soup.find_all('a', href=True):
                href = link['href']

                # Extract URL from Google redirect
                if '/url?q=' in href:
                    url = href.split('/url?q=')[1].split('&')[0]

                    # Filter out non-company sites
                    if any(x in url.lower() for x in ['google', 'youtube', 'facebook', 'linkedin', 'wikipedia']):
                        continue

                    # Validate URL
                    if url.startswith('http') and '.' in url:
                        return url

    except Exception as e:
        print(f"    Error finding URL: {e}")

    return None

async def scrape_website_for_signals(session, company_name, website):
    """Scrape company website and detect real signals"""

    signals = []

    try:
        async with session.get(website, timeout=15, ssl=False, headers={'User-Agent': 'Mozilla/5.0'}) as response:
            if response.status != 200:
                return signals

            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            text = soup.get_text().lower()

            # 1. Training signal (40 points - HIGHEST)
            if any(kw in text for kw in TRAINING_KEYWORDS):
                signals.append({
                    'type': 'training_detected',
                    'title': 'Training/Formation mentioned',
                    'detail': f'{company_name} website mentions training or formation programs',
                    'url': website
                })

            # 2. Hiring signal (20 points - HIGH)
            if any(kw in text for kw in HIRING_KEYWORDS):
                signals.append({
                    'type': 'new_hire',
                    'title': 'Hiring/Recruitment section found',
                    'detail': f'{company_name} has recruitment or career section on website',
                    'url': website + '/careers'
                })

            # 3. SOLIDWORKS logo detected (10 points)
            if any(kw in text for kw in SOLIDWORKS_KEYWORDS):
                signals.append({
                    'type': 'logo_detected',
                    'title': 'CAD software detected',
                    'detail': f'{company_name} website mentions SOLIDWORKS or CAD software',
                    'url': website
                })

            # 4. Engineering roles detected (20 points)
            if any(kw in text for kw in ENGINEERING_KEYWORDS):
                signals.append({
                    'type': 'role_detected',
                    'title': 'Engineering roles mentioned',
                    'detail': f'{company_name} has engineering team or bureau d\'études',
                    'url': website + '/team'
                })

    except Exception as e:
        print(f"    Error scraping website: {e}")

    return signals

async def process_all_companies():
    """Find URLs and scrape all 380 companies"""

    print("=" * 60)
    print("REAL SCRAPING - FINDING URLs AND DETECTING SIGNALS")
    print("=" * 60)
    print()

    async with AsyncSessionLocal() as db:
        # Get all companies
        result = await db.execute(select(Lead))
        leads = list(result.scalars().all())

        print(f"📊 Total companies: {len(leads)}")
        print(f"⏱️  Estimated time: {len(leads) * 5 // 60} minutes\n")

        connector = aiohttp.TCPConnector(limit=3, ssl=False)
        timeout = aiohttp.ClientTimeout(total=20)

        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:

            total_signals = 0
            companies_with_signals = 0

            for idx, lead in enumerate(leads):
                print(f"[{idx+1}/{len(leads)}] {lead.company_name}")

                # Step 1: Find URL if not exists
                if not lead.website:
                    print(f"  🔍 Searching for URL...")
                    url = await find_company_url(session, lead.company_name)

                    if url:
                        lead.website = url
                        print(f"  ✓ Found: {url}")
                    else:
                        print(f"  ✗ URL not found")
                        continue

                # Step 2: Scrape website for signals
                print(f"  🌐 Scraping {lead.website}")
                signals = await scrape_website_for_signals(session, lead.company_name, lead.website)

                if signals:
                    print(f"  ✅ Found {len(signals)} signals:")
                    for sig in signals:
                        print(f"     - {sig['title']}")

                        # Save to database
                        signal_obj = LeadSignal(
                            lead_id=lead.id,
                            signal_type=sig['type'],
                            title=sig['title'],
                            detail=sig['detail'],
                            source_url=sig['url'],
                            detected_at=datetime.now()
                        )
                        db.add(signal_obj)

                    total_signals += len(signals)
                    companies_with_signals += 1
                else:
                    print(f"  - No signals detected")

                print()

                # Save progress every 10 companies
                if (idx + 1) % 10 == 0:
                    await db.commit()
                    print(f"💾 Progress saved: {idx+1}/{len(leads)} companies")
                    print(f"   Signals found so far: {total_signals}")
                    print(f"   Companies with signals: {companies_with_signals}\n")

                # Rate limiting
                await asyncio.sleep(2)

            # Final save
            await db.commit()

    print("\n" + "=" * 60)
    print("✅ REAL SCRAPING COMPLETE")
    print("=" * 60)
    print(f"Total signals detected: {total_signals}")
    print(f"Companies with signals: {companies_with_signals}")
    print(f"Success rate: {companies_with_signals}/{len(leads)} ({companies_with_signals*100//len(leads)}%)")

if __name__ == "__main__":
    asyncio.run(process_all_companies())

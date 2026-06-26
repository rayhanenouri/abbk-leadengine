#!/usr/bin/env python3
"""
For each company in database:
1. Find their real website via Google
2. Scrape website for signals
3. Save signals to database
"""

import asyncio
import sys
from pathlib import Path
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime
import re

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.session import AsyncSessionLocal
from app.models.models import Lead, LeadSignal
from sqlalchemy import select

KEYWORDS = {
    'training': ['formation', 'training', 'solidworks', 'cao', 'cfao', 'certification'],
    'hiring': ['recrute', 'recrutement', 'candidature', 'carriere', 'postuler'],
    'engineering': ['ingenieur', 'engineer', 'bureau etudes', 'cad', 'cao'],
    'cad_software': ['solidworks', 'catia', 'autocad', 'inventor', 'fusion360']
}

async def find_website(session, company_name):
    """Google search for company website"""
    search_query = f"{company_name} Tunisia site"
    google_url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"

    try:
        async with session.get(google_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10) as response:
            if response.status != 200:
                return None

            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')

            for link in soup.find_all('a', href=True):
                href = link['href']
                if '/url?q=' in href:
                    url = href.split('/url?q=')[1].split('&')[0]
                    if url.startswith('http') and not any(x in url.lower() for x in ['google', 'facebook', 'linkedin', 'wikipedia']):
                        return url
    except:
        pass

    return None

async def scrape_company_website(session, lead, db):
    """Scrape company website for signals"""

    if not lead.website or 'taa.tn' in lead.website or 'tunisieindustrie' in lead.website:
        # Need to find real website
        website = await find_website(session, lead.company_name)
        if website:
            lead.website = website
            await db.flush()
        else:
            return 0

    # Scrape the website
    try:
        async with session.get(lead.website, ssl=False, timeout=15, headers={'User-Agent': 'Mozilla/5.0'}) as response:
            if response.status != 200:
                return 0

            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            text = soup.get_text().lower()

            signals_added = 0

            # Check training
            if any(kw in text for kw in KEYWORDS['training']):
                existing = await db.execute(
                    select(LeadSignal).where(
                        LeadSignal.lead_id == lead.id,
                        LeadSignal.signal_type == 'training_detected'
                    )
                )
                if not existing.scalar_one_or_none():
                    db.add(LeadSignal(
                        lead_id=lead.id,
                        signal_type='training_detected',
                        title='Training/CAD software mentioned',
                        detail=f'{lead.company_name} website mentions training or CAD software',
                        source_url=lead.website,
                        detected_at=datetime.now()
                    ))
                    signals_added += 1

            # Check hiring
            if any(kw in text for kw in KEYWORDS['hiring']):
                existing = await db.execute(
                    select(LeadSignal).where(
                        LeadSignal.lead_id == lead.id,
                        LeadSignal.signal_type == 'new_hire'
                    )
                )
                if not existing.scalar_one_or_none():
                    db.add(LeadSignal(
                        lead_id=lead.id,
                        signal_type='new_hire',
                        title='Hiring/Recruitment section found',
                        detail=f'{lead.company_name} has careers section',
                        source_url=lead.website,
                        detected_at=datetime.now()
                    ))
                    signals_added += 1

            # Check engineering
            if any(kw in text for kw in KEYWORDS['engineering']):
                existing = await db.execute(
                    select(LeadSignal).where(
                        LeadSignal.lead_id == lead.id,
                        LeadSignal.signal_type == 'role_detected'
                    )
                )
                if not existing.scalar_one_or_none():
                    db.add(LeadSignal(
                        lead_id=lead.id,
                        signal_type='role_detected',
                        title='Engineering roles mentioned',
                        detail=f'{lead.company_name} has engineering team',
                        source_url=lead.website,
                        detected_at=datetime.now()
                    ))
                    signals_added += 1

            return signals_added

    except Exception as e:
        return 0

async def scrape_all():
    """Scrape all companies"""

    print("="*70)
    print("SCRAPING ALL 1020 COMPANIES FOR REAL SIGNALS")
    print("="*70)
    print()

    async with AsyncSessionLocal() as db:
        # Get companies without signals
        result = await db.execute(
            select(Lead)
            .outerjoin(LeadSignal, Lead.id == LeadSignal.lead_id)
            .where(LeadSignal.id.is_(None))
            .limit(200)  # Process 200 companies at a time
        )
        leads = list(result.scalars().all())

        print(f"Found {len(leads)} companies without signals")
        print("Starting scraping...\n")

        connector = aiohttp.TCPConnector(limit=5, ssl=False)
        timeout = aiohttp.ClientTimeout(total=20)

        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            total_signals = 0

            for idx, lead in enumerate(leads, 1):
                print(f"[{idx}/{len(leads)}] {lead.company_name}")

                signals = await scrape_company_website(session, lead, db)

                if signals > 0:
                    print(f"  ✓ Added {signals} signals")
                    total_signals += signals
                else:
                    print(f"  - No signals found")

                if idx % 20 == 0:
                    await db.commit()
                    print(f"\n💾 Progress saved: {idx}/{len(leads)}, {total_signals} signals total\n")

                await asyncio.sleep(2)  # Rate limit

            await db.commit()

            print(f"\n{'='*70}")
            print(f"✅ COMPLETED")
            print(f"   Total signals added: {total_signals}")
            print("="*70)

if __name__ == "__main__":
    asyncio.run(scrape_all())

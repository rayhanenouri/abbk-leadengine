#!/usr/bin/env python3
"""
Scrape TAA (Tunisia Automotive Association) members
This site WORKS - we already got 8 companies from it
"""

import asyncio
import sys
from pathlib import Path
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.session import AsyncSessionLocal
from app.models.models import Lead, LeadSignal
from sqlalchemy import select

async def scrape_taa_members():
    """Scrape all TAA member companies"""

    print("=" * 70)
    print("SCRAPING TAA MEMBERS - TUNISIA AUTOMOTIVE ASSOCIATION")
    print("=" * 70)
    print()

    url = "https://taa.tn/fr/membres"

    async with aiohttp.ClientSession() as session:
        async with session.get(url, ssl=False) as response:
            if response.status != 200:
                print(f"Error: {response.status}")
                return

            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')

            # Find all member links
            members = soup.find_all('a', href=lambda x: x and '/membre/' in x)

            print(f"Found {len(members)} TAA member companies\n")

            async with AsyncSessionLocal() as db:
                saved = 0

                for member in members:
                    company_name = member.get_text(strip=True)
                    member_url = f"https://taa.tn{member['href']}"

                    if not company_name or len(company_name) < 3:
                        continue

                    print(f"  [{saved+1}/{len(members)}] {company_name}")

                    # Check if company exists
                    result = await db.execute(
                        select(Lead).where(Lead.company_name == company_name)
                    )
                    lead = result.scalar_one_or_none()

                    # Create if doesn't exist
                    if not lead:
                        lead = Lead(
                            company_name=company_name,
                            sector="Automotive",
                            city="Tunis",
                            country="Tunisia",
                            website=member_url,
                            is_multinational=True,  # TAA members are often multinational
                            status="new",
                            scraped_data={
                                "source": "TAA Members",
                                "scraped_at": datetime.now().isoformat()
                            }
                        )
                        db.add(lead)
                        await db.flush()
                        print(f"      ✓ Created new lead")

                    # Scrape member page for signals
                    try:
                        async with session.get(member_url, ssl=False, timeout=10) as page_response:
                            if page_response.status == 200:
                                page_html = await page_response.text()
                                page_soup = BeautifulSoup(page_html, 'html.parser')
                                page_text = page_soup.get_text().lower()

                                signals_added = 0

                                # Check for training
                                if any(kw in page_text for kw in ['formation', 'training', 'solidworks']):
                                    # Check if signal exists
                                    existing = await db.execute(
                                        select(LeadSignal).where(
                                            LeadSignal.lead_id == lead.id,
                                            LeadSignal.signal_type == 'training_detected'
                                        )
                                    )
                                    if not existing.scalar_one_or_none():
                                        signal = LeadSignal(
                                            lead_id=lead.id,
                                            signal_type='training_detected',
                                            title='Training/Formation mentioned',
                                            detail=f'{company_name} mentions training or CAD software',
                                            source_url=member_url,
                                            detected_at=datetime.now()
                                        )
                                        db.add(signal)
                                        signals_added += 1

                                # Check for engineering roles
                                if any(kw in page_text for kw in ['ingenieur', 'engineer', 'bureau', 'cad', 'cao']):
                                    existing = await db.execute(
                                        select(LeadSignal).where(
                                            LeadSignal.lead_id == lead.id,
                                            LeadSignal.signal_type == 'role_detected'
                                        )
                                    )
                                    if not existing.scalar_one_or_none():
                                        signal = LeadSignal(
                                            lead_id=lead.id,
                                            signal_type='role_detected',
                                            title='Engineering roles mentioned',
                                            detail=f'{company_name} has engineering team',
                                            source_url=member_url,
                                            detected_at=datetime.now()
                                        )
                                        db.add(signal)
                                        signals_added += 1

                                if signals_added > 0:
                                    print(f"      ✓ Added {signals_added} signals")

                    except Exception as e:
                        print(f"      ✗ Error scraping page: {e}")

                    saved += 1

                    # Save every 10 companies
                    if saved % 10 == 0:
                        await db.commit()
                        print(f"\n  💾 Saved progress: {saved}/{len(members)}\n")

                    await asyncio.sleep(1)  # Rate limit

                # Final save
                await db.commit()

                print(f"\n" + "=" * 70)
                print(f"✅ COMPLETED")
                print(f"   Total TAA members processed: {saved}")
                print("=" * 70)

if __name__ == "__main__":
    asyncio.run(scrape_taa_members())

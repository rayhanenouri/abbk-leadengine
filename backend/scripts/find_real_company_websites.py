#!/usr/bin/env python3
"""
CRITICAL FIX: Find real company websites from TAA directory pages.

Problem: Companies have TAA directory URLs, not their actual websites.
Solution: Scrape TAA pages to extract real company website URLs.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx
from bs4 import BeautifulSoup
from sqlalchemy import select, update
from app.db.session import AsyncSessionLocal
from app.models.models import Lead


async def extract_real_website_from_taa(taa_url: str) -> str | None:
    """Extract actual company website from TAA directory page."""

    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            response = await client.get(taa_url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Look for website link in TAA page
            # Common patterns: <a href="http://companywebsite.com">Site web</a>
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                text = link.get_text(strip=True).lower()

                # Skip TAA internal links
                if 'taa.tn' in href:
                    continue

                # Look for external website links
                if any(keyword in text for keyword in ['site', 'web', 'website', 'www', 'http']):
                    if href.startswith('http'):
                        return href

                # Also check if href is a clear external domain
                if href.startswith('http') and 'taa.tn' not in href:
                    # Verify it's not a social media link
                    if not any(sm in href for sm in ['facebook', 'linkedin', 'twitter', 'instagram', 'youtube']):
                        return href

            return None

    except Exception as e:
        print(f"  Error scraping {taa_url}: {e}")
        return None


async def find_real_websites():
    """Find real company websites for all companies with TAA directory URLs."""

    print("\n" + "=" * 70)
    print("🔍 FINDING REAL COMPANY WEBSITES FROM TAA DIRECTORY")
    print("=" * 70 + "\n")

    async with AsyncSessionLocal() as db:
        # Get all companies with TAA directory URLs
        result = await db.execute(
            select(Lead).where(
                Lead.website.like('%taa.tn%')
            )
        )
        companies = result.scalars().all()

        print(f"Found {len(companies)} companies with TAA directory URLs\n")

        found = 0
        not_found = 0

        for i, company in enumerate(companies, 1):
            print(f"[{i}/{len(companies)}] {company.company_name:40}", end=" ")

            # Try to extract real website from TAA page
            real_website = await extract_real_website_from_taa(company.website)

            if real_website:
                print(f"✅ {real_website}")

                # Update company with real website
                await db.execute(
                    update(Lead)
                    .where(Lead.id == company.id)
                    .values(website=real_website)
                )
                found += 1
            else:
                print(f"❌ No website found - setting to NULL")

                # Set website to NULL (company has no web presence)
                await db.execute(
                    update(Lead)
                    .where(Lead.id == company.id)
                    .values(website=None)
                )
                not_found += 1

            # Rate limiting
            await asyncio.sleep(2)

        await db.commit()

        print(f"\n✅ Complete!")
        print(f"   Real websites found: {found}")
        print(f"   No website found: {not_found}")
        print(f"\n{'=' * 70}\n")


if __name__ == "__main__":
    asyncio.run(find_real_websites())

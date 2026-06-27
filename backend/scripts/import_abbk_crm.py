#!/usr/bin/env python3
"""
Import ABBK CRM Database (501 companies from their SolidWorks/Dassault system)
"""

import sys
import asyncio
import pandas as pd
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.session import AsyncSessionLocal
from app.models.models import Lead
from sqlalchemy import select

async def import_abbk_crm():
    """Import 501 ABBK companies from CRM export"""

    print("🔄 Reading ABBK CRM database...")
    df = pd.read_excel('/app/ANOUARDAOUD2.xls', engine='openpyxl')

    print(f"   Total rows: {len(df)}")
    print(f"   Columns: CompanyName, City, Country, JobTitle, etc.\n")

    imported = 0
    skipped = 0
    duplicates = 0

    async with AsyncSessionLocal() as db:
        for idx, row in df.iterrows():
            try:
                # Extract company name
                company_name = str(row['CompanyName']).strip() if pd.notna(row.get('CompanyName')) else None

                if not company_name or company_name == 'nan' or len(company_name) < 2:
                    skipped += 1
                    continue

                # Check duplicate
                result = await db.execute(
                    select(Lead).where(Lead.company_name == company_name)
                )
                existing = result.scalars().first()

                if existing:
                    duplicates += 1
                    continue

                # Extract fields
                city = str(row['City']).strip() if pd.notna(row.get('City')) else None
                country = str(row['Country']).strip() if pd.notna(row.get('Country')) else "Tunisia"
                phone = str(row['ContactPhone']).strip() if pd.notna(row.get('ContactPhone')) else None
                email = str(row['EmailAddress']).strip() if pd.notna(row.get('EmailAddress')) else None
                job_title = str(row['JobTitle']).strip() if pd.notna(row.get('JobTitle')) else None
                lead_date = row.get('LeadDate')
                linkedin = str(row['LinkedIn Profile']).strip() if pd.notna(row.get('LinkedIn Profile')) else None

                # Determine sector from job title or product
                sector = "Engineering"
                if pd.notna(row.get('JobTitle')):
                    title_lower = str(row['JobTitle']).lower()
                    if 'automotive' in title_lower or 'auto' in title_lower:
                        sector = "Automotive"
                    elif 'electronic' in title_lower or 'electric' in title_lower:
                        sector = "Electronics"
                    elif 'aerospace' in title_lower or 'aviation' in title_lower:
                        sector = "Aerospace"
                    elif 'construction' in title_lower or 'building' in title_lower:
                        sector = "Construction"
                    elif 'mechanical' in title_lower or 'mecanique' in title_lower:
                        sector = "Mechanical Engineering"
                    elif 'manufacturing' in title_lower:
                        sector = "Manufacturing"

                # Check if multinational (non-Tunisia country or international indicators)
                is_multinational = False
                if country and country != "Tunisia":
                    is_multinational = True
                if company_name and any(x in company_name.upper() for x in ['INTERNATIONAL', 'GLOBAL', 'GROUP', 'CORPORATION']):
                    is_multinational = True

                # Create lead (phone not in model, store in scraped_data)
                lead = Lead(
                    company_name=company_name,
                    sector=sector,
                    city=city,
                    country=country or "Tunisia",
                    website=None,  # Not in CRM
                    linkedin_url=linkedin,
                    is_multinational=is_multinational,
                    is_exporter=False,  # Will detect from signals
                    under_audit=False,  # Will detect from signals
                    status="new",
                    scraped_data={
                        "source": "ABBK CRM Export",
                        "imported_at": datetime.now().isoformat(),
                        "lead_date": str(lead_date) if pd.notna(lead_date) else None,
                        "contact_phone": phone,
                        "contact_email": email,
                        "contact_job_title": job_title,
                        "product_interest": str(row['Product']) if pd.notna(row.get('Product')) else None,
                    }
                )

                db.add(lead)
                imported += 1

                if imported % 50 == 0:
                    print(f"   ✓ Imported {imported} companies...")
                    await db.commit()

            except Exception as e:
                print(f"   ✗ Error on row {idx}: {e}")
                skipped += 1
                continue

        await db.commit()

    print(f"\n✅ ABBK CRM Import Complete!")
    print(f"   ✓ Imported: {imported} companies")
    print(f"   ⊘ Duplicates: {duplicates}")
    print(f"   ✗ Skipped: {skipped}")
    print(f"\n📊 Total leads in database: {imported}")

if __name__ == "__main__":
    asyncio.run(import_abbk_crm())

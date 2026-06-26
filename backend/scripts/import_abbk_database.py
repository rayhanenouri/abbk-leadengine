#!/usr/bin/env python3
"""
Import ABBK's Excel database into LeadEngine
Converts .xls to leads with proper structure
"""

import sys
import asyncio
import pandas as pd
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.session import AsyncSessionLocal
from app.models.models import Lead
from sqlalchemy import select

async def import_abbk_database():
    """Import ABBK Excel database"""

    # Read Excel file
    xls_path = Path("/home/rayhanenouri/projects/abbk-leadengine/ANOUARDAOUD2.xls")

    if not xls_path.exists():
        # Try with xlsx extension
        xls_path = Path("/home/rayhanenouri/projects/abbk-leadengine/ANOUARDAOUD2.xlsx")

    print(f"Reading {xls_path}...")
    df = pd.read_excel(xls_path, engine='xlrd' if str(xls_path).endswith('.xls') else 'openpyxl')

    print(f"Columns found: {df.columns.tolist()}")
    print(f"Total rows: {len(df)}")
    print(f"\nFirst 3 rows:")
    print(df.head(3))

    # Map columns (will adjust based on what we see)
    # Common patterns: Company/Société/Entreprise, Secteur/Activité, Ville/City

    imported = 0
    skipped = 0

    async with AsyncSessionLocal() as db:
        for idx, row in df.iterrows():
            try:
                # Try to extract company name from various column names
                company_name = None
                for col in ['Company', 'Société', 'Entreprise', 'Nom', 'Name', 'company', 'société']:
                    if col in df.columns and pd.notna(row.get(col)):
                        company_name = str(row[col]).strip()
                        break

                if not company_name:
                    # Use first column as company name
                    company_name = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else None

                if not company_name or company_name == 'nan':
                    skipped += 1
                    continue

                # Check if already exists
                result = await db.execute(
                    select(Lead).where(Lead.company_name == company_name)
                )
                existing = result.scalars().first()

                if existing:
                    print(f"  Skipping duplicate: {company_name}")
                    skipped += 1
                    continue

                # Extract other fields
                sector = None
                for col in ['Secteur', 'Sector', 'Activité', 'Activity', 'Industry']:
                    if col in df.columns and pd.notna(row.get(col)):
                        sector = str(row[col]).strip()
                        break

                city = None
                for col in ['Ville', 'City', 'Gouvernorat', 'Region']:
                    if col in df.columns and pd.notna(row.get(col)):
                        city = str(row[col]).strip()
                        break

                website = None
                for col in ['Website', 'Site', 'URL', 'web']:
                    if col in df.columns and pd.notna(row.get(col)):
                        website = str(row[col]).strip()
                        break

                phone = None
                for col in ['Phone', 'Tel', 'Téléphone', 'Contact']:
                    if col in df.columns and pd.notna(row.get(col)):
                        phone = str(row[col]).strip()
                        break

                # Create lead
                lead = Lead(
                    company_name=company_name,
                    sector=sector or "Manufacturing",
                    city=city or "Tunis",
                    country="Tunisia",
                    website=website,
                    phone=phone,
                    status="new",
                    scraped_data={"source": "ABBK Database", "imported_at": "2026-06-26"}
                )

                db.add(lead)
                imported += 1

                if imported % 10 == 0:
                    print(f"  Imported {imported} companies...")

            except Exception as e:
                print(f"  Error on row {idx}: {e}")
                skipped += 1
                continue

        await db.commit()

    print(f"\n✅ Import complete!")
    print(f"   Imported: {imported}")
    print(f"   Skipped: {skipped}")
    print(f"   Total in DB: {imported}")

if __name__ == "__main__":
    asyncio.run(import_abbk_database())

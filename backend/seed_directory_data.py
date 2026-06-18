#!/usr/bin/env python3
"""
Seed script to simulate directory scraping results.
Inserts sample Tunisian companies as if they were scraped from annuaire.tn.
"""
import asyncio
from datetime import datetime
from sqlalchemy import select, or_
from app.db.session import AsyncSessionLocal
from app.models.models import Lead, LeadStatus


# Sample Tunisian companies from various directories
SAMPLE_COMPANIES = [
    {
        "company_name": "Société Tunisienne de l'Électricité et du Gaz (STEG)",
        "website": "https://www.steg.com.tn",
        "phone": "+216 71 341 311",
        "sector": "Energy & Utilities",
        "city": "Tunis",
        "description": "Tunisian national electricity and gas company",
        "source": "annuaire.tn",
    },
    {
        "company_name": "Tunisie Telecom",
        "website": "https://www.tunisietelecom.tn",
        "phone": "+216 71 840 000",
        "sector": "Telecommunications",
        "city": "Tunis",
        "description": "Leading telecommunications operator",
        "source": "annuaire.tn",
    },
    {
        "company_name": "Groupe Chimique Tunisien",
        "website": "https://www.gct.com.tn",
        "phone": "+216 76 696 300",
        "sector": "Chemical Manufacturing",
        "city": "Gabès",
        "description": "Phosphate processing and fertilizer production",
        "source": "annuaire.tn",
    },
    {
        "company_name": "SITS - Société Industrielle de Textile",
        "website": "https://www.sits.com.tn",
        "phone": "+216 74 275 000",
        "sector": "Textile Manufacturing",
        "city": "Mahdia",
        "description": "Industrial textile production",
        "source": "annuaire.tn",
    },
    {
        "company_name": "Clinique El Amen",
        "website": "https://www.elamen.com.tn",
        "phone": "+216 71 860 100",
        "sector": "Healthcare",
        "city": "Tunis",
        "description": "Private hospital and medical center",
        "source": "pagesjaunes.tn",
    },
    {
        "company_name": "Société Frigorifique et Brasserie de Tunis (SFBT)",
        "website": "https://www.sfbt.com.tn",
        "phone": "+216 71 234 000",
        "sector": "Food & Beverage",
        "city": "Tunis",
        "description": "Brewery and beverage production",
        "source": "annuaire.tn",
    },
    {
        "company_name": "Société des Ciments d'Enfidha",
        "website": "https://www.ciments-enfidha.com.tn",
        "phone": "+216 73 360 300",
        "sector": "Construction Materials",
        "city": "Enfidha",
        "description": "Cement manufacturing",
        "source": "kompass.tn",
    },
    {
        "company_name": "Auto Hall Tunisie",
        "website": "https://www.autohall.tn",
        "phone": "+216 71 947 000",
        "sector": "Automotive Distribution",
        "city": "Tunis",
        "description": "Vehicle import and distribution",
        "source": "annuaire.tn",
    },
    {
        "company_name": "SOTACIB Kairouan",
        "website": "https://www.sotacib.com",
        "phone": "+216 77 226 000",
        "sector": "Cement Manufacturing",
        "city": "Kairouan",
        "description": "Cement production plant",
        "source": "kompass.tn",
    },
    {
        "company_name": "Bureau d'Études Technique BET-SCET",
        "website": "https://www.scet-tunisie.com",
        "phone": "+216 71 783 200",
        "sector": "Engineering Consulting",
        "city": "Tunis",
        "description": "Engineering and technical consulting",
        "source": "annuaire.tn",
    },
    {
        "company_name": "Société Tunisienne des Industries de Raffinage (STIR)",
        "website": "https://www.stir.com.tn",
        "phone": "+216 72 298 600",
        "sector": "Oil & Gas Refining",
        "city": "Bizerte",
        "description": "Oil refinery and petrochemical",
        "source": "annuaire.tn",
    },
    {
        "company_name": "Industrielle d'Appareillage et de Matériel Électrique",
        "website": "https://www.iame.com.tn",
        "phone": "+216 71 780 200",
        "sector": "Electrical Equipment",
        "city": "Ben Arous",
        "description": "Electrical equipment manufacturing",
        "source": "kompass.tn",
    },
    {
        "company_name": "Aéroports de Tunisie",
        "website": "https://www.oaca.nat.tn",
        "phone": "+216 71 755 000",
        "sector": "Aviation Infrastructure",
        "city": "Tunis",
        "description": "Airport management and operations",
        "source": "pagesjaunes.tn",
    },
    {
        "company_name": "Société Tunisienne de Sidérurgie (METAP)",
        "website": "https://www.metap.com.tn",
        "phone": "+216 72 400 500",
        "sector": "Steel Manufacturing",
        "city": "Menzel Bourguiba",
        "description": "Steel production and metal works",
        "source": "kompass.tn",
    },
    {
        "company_name": "Les Cimenteries de Bizerte (CBZ)",
        "website": "https://www.cbz.com.tn",
        "phone": "+216 72 590 400",
        "sector": "Cement Manufacturing",
        "city": "Bizerte",
        "description": "Cement factory and construction materials",
        "source": "annuaire.tn",
    },
    {
        "company_name": "Tunisie Profil Aluminium",
        "website": "https://www.tpa.com.tn",
        "phone": "+216 71 428 100",
        "sector": "Aluminum Manufacturing",
        "city": "Mégrine",
        "description": "Aluminum extrusion and profiles",
        "source": "kompass.tn",
    },
    {
        "company_name": "Société Tunisienne d'Acier (STA)",
        "website": "https://www.sta.com.tn",
        "phone": "+216 71 570 600",
        "sector": "Steel Manufacturing",
        "city": "Radès",
        "description": "Steel rebar and construction steel",
        "source": "annuaire.tn",
    },
    {
        "company_name": "Office National de l'Assainissement (ONAS)",
        "website": "https://www.onas.nat.tn",
        "phone": "+216 71 843 711",
        "sector": "Water & Sanitation",
        "city": "Tunis",
        "description": "National sanitation and wastewater management",
        "source": "pagesjaunes.tn",
    },
    {
        "company_name": "Société Nationale de Cellulose et de Papier Alfa",
        "website": "https://www.sncpa.com.tn",
        "phone": "+216 76 230 600",
        "sector": "Paper Manufacturing",
        "city": "Kasserine",
        "description": "Cellulose and paper production",
        "source": "annuaire.tn",
    },
    {
        "company_name": "Amen Bank",
        "website": "https://www.amenbank.com.tn",
        "phone": "+216 71 835 500",
        "sector": "Banking & Finance",
        "city": "Tunis",
        "description": "Commercial bank and financial services",
        "source": "pagesjaunes.tn",
    },
    {
        "company_name": "Société de Transport de Tunis (TRANSTU)",
        "website": "https://www.transtu.tn",
        "phone": "+216 71 560 300",
        "sector": "Public Transportation",
        "city": "Tunis",
        "description": "Public transport buses and metro",
        "source": "annuaire.tn",
    },
    {
        "company_name": "Délice Danone",
        "website": "https://www.delice.com.tn",
        "phone": "+216 71 940 200",
        "sector": "Dairy Products",
        "city": "Tunis",
        "description": "Dairy products and beverages",
        "source": "annuaire.tn",
    },
]


async def seed_companies():
    """Insert sample companies into database."""
    async with AsyncSessionLocal() as session:
        imported = 0
        skipped = 0

        for company_data in SAMPLE_COMPANIES:
            company_name = company_data["company_name"]
            website = company_data.get("website")

            # Check for duplicates
            duplicate_query = select(Lead).where(
                or_(
                    Lead.website == website if website else False,
                    Lead.company_name == company_name
                )
            )
            result = await session.execute(duplicate_query)
            existing = result.scalar_one_or_none()

            if existing:
                print(f"⏭️  Skipped duplicate: {company_name}")
                skipped += 1
                continue

            # Create new lead
            new_lead = Lead(
                company_name=company_name,
                website=website,
                country="Tunisia",
                city=company_data.get("city"),
                sector=company_data.get("sector"),
                status=LeadStatus.new,
                scraped_data={
                    company_data.get("source"): {
                        "phone": company_data.get("phone"),
                        "description": company_data.get("description"),
                        "scraped_at": datetime.utcnow().isoformat(),
                        "method": "seed_script",
                    }
                }
            )

            session.add(new_lead)
            print(f"✅ Added: {company_name} ({company_data.get('city')})")
            imported += 1

        await session.commit()

        print("\n" + "=" * 60)
        print(f"✅ Import complete!")
        print(f"   Imported: {imported}")
        print(f"   Skipped:  {skipped}")
        print(f"   Total:    {len(SAMPLE_COMPANIES)}")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(seed_companies())

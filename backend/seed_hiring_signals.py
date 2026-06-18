#!/usr/bin/env python3
"""
Seed hiring signals for existing leads.
Simulates job board scraping results.
"""
import asyncio
from datetime import datetime
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.models import Lead, LeadSignal


# Sample hiring signals - engineering roles at our existing companies
HIRING_SIGNALS = [
    {
        "company_name": "Bureau d'Études Technique BET-SCET",
        "job_title": "Ingénieur Conception Mécanique",
        "source": "emploi.tn",
        "detail": "Expérience SOLIDWORKS requise, 3-5 ans d'expérience",
    },
    {
        "company_name": "Groupe Chimique Tunisien",
        "job_title": "Ingénieur Calcul et Simulation",
        "source": "keejob.com",
        "detail": "Maîtrise Abaqus ou ANSYS, bureau d'études",
    },
    {
        "company_name": "STMicroelectronics Tunisia",
        "job_title": "CAD Designer - Electronics",
        "source": "emploi.tn",
        "detail": "SOLIDWORKS Electrical, conception circuits",
    },
    {
        "company_name": "Leoni Tunisia",
        "job_title": "Ingénieur R&D Automobile",
        "source": "keejob.com",
        "detail": "Développement produits automobiles, CAO 3D",
    },
    {
        "company_name": "Auto Hall Tunisie",
        "job_title": "Dessinateur Bureau d'Études",
        "source": "emploi.tn",
        "detail": "CAO/DAO, conception mécanique",
    },
    {
        "company_name": "Société Tunisienne de Sidérurgie (METAP)",
        "job_title": "Ingénieur Méthodes Fabrication",
        "source": "keejob.com",
        "detail": "Conception outils, SOLIDWORKS CAM",
    },
    {
        "company_name": "Tunisie Profil Aluminium",
        "job_title": "Ingénieur Conception Profilés",
        "source": "emploi.tn",
        "detail": "Conception profilés aluminium, CAO 3D",
    },
    {
        "company_name": "Poulina Group",
        "job_title": "Ingénieur Bureau d'Études",
        "source": "keejob.com",
        "detail": "Projets industriels, conception équipements",
    },
    {
        "company_name": "ENIT",
        "job_title": "Enseignant-Chercheur Génie Mécanique",
        "source": "emploi.tn",
        "detail": "Formation SOLIDWORKS, recherche CAO",
    },
    {
        "company_name": "Société des Ciments d'Enfidha",
        "job_title": "Ingénieur Maintenance Industrielle",
        "source": "keejob.com",
        "detail": "Conception pièces de rechange, CAO",
    },
]


async def seed_hiring_signals():
    """Create hiring signals for existing leads."""
    async with AsyncSessionLocal() as session:
        created = 0
        skipped = 0
        not_found = 0

        for signal_data in HIRING_SIGNALS:
            company_name = signal_data["company_name"]

            # Find the lead
            result = await session.execute(
                select(Lead).where(Lead.company_name == company_name)
            )
            lead = result.scalar_one_or_none()

            if not lead:
                print(f"⚠️  Lead not found: {company_name}")
                not_found += 1
                continue

            # Check if signal already exists
            existing = await session.execute(
                select(LeadSignal).where(
                    LeadSignal.lead_id == lead.id,
                    LeadSignal.signal_type == 'new_hire',
                    LeadSignal.title.contains(signal_data["job_title"])
                )
            )

            if existing.scalar_one_or_none():
                print(f"⏭️  Signal exists: {company_name} - {signal_data['job_title']}")
                skipped += 1
                continue

            # Create signal
            signal = LeadSignal(
                lead_id=lead.id,
                signal_type='new_hire',
                title=f"Hiring {signal_data['job_title']}",
                detail=signal_data["detail"],
                source_url=f"https://{signal_data['source']}/offre/exemple",
                detected_at=datetime.utcnow()
            )

            session.add(signal)
            print(f"✅ Created: {company_name} → {signal_data['job_title']}")
            created += 1

        await session.commit()

        print("\n" + "=" * 60)
        print(f"✅ Hiring signals seeded!")
        print(f"   Created:   {created}")
        print(f"   Skipped:   {skipped}")
        print(f"   Not found: {not_found}")
        print(f"   Total:     {len(HIRING_SIGNALS)}")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(seed_hiring_signals())

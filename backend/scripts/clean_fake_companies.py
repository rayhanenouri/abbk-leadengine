#!/usr/bin/env python3
"""
Remove fake companies (page titles, navigation links) from database
Keep only REAL company names
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.session import AsyncSessionLocal
from app.models.models import Lead
from sqlalchemy import select, delete, or_

async def clean_database():
    print("="*70)
    print("CLEANING FAKE COMPANIES FROM DATABASE")
    print("="*70)
    print()

    # List of fake "companies" (page titles, navigation)
    fake_names = [
        'Actualités', 'Base d\'entreprises', 'Base d\'entreprise', 'Aller au contenu principal',
        'Our News', 'Our tools', 'Our projects', 'Events & Gallery',
        'Membres', 'Cluster', 'privacy policy', 'Politique de management',
        'Fiche de l\'adherent', 'Accès aux marchés', 'Adhésion',
        'Commitments', 'Certifications', 'Brochures', 'Consulter',
        'Airports', 'History', 'Organization', 'LEARN MORE', 'LISTS',
        'View Details', 'Power', 'Vidéos', 'Réglementations', 'Réglementation',
        'Photos', 'Appui aux PME', 'A propos CETIME', 'A propos du CETIME',
        'Notre ADN', 'Formation et certification métiers', 'Expertise Technique',
        'Essais sur piles et batteries', 'Essais Mécaniques', 'Essais sur câbles',
        'Essais sur les appareils Electrodomestiques', 'Essais sur les appareils Electroménagers',
        'Essais sur articles culinaires', 'Essais sur lampes',
        'Autres Contrôles techniques à l'importation',
        'Plateforme Électronique', 'Plateforme Mécanique',
        'Stages et PFE', 'Les événements', 'Coopération internationale',
        'Emploi et compétence', 'Performance économique',
        'Essais électriques'
    ]

    async with AsyncSessionLocal() as db:
        # Count before
        before = await db.execute(select(func.count()).select_from(Lead))
        total_before = before.scalar()

        # Delete fake companies
        conditions = [Lead.company_name == name for name in fake_names]

        result = await db.execute(
            delete(Lead).where(or_(*conditions))
        )

        await db.commit()

        # Count after
        after = await db.execute(select(func.count()).select_from(Lead))
        total_after = after.scalar()

        print(f"Before: {total_before} companies")
        print(f"After: {total_after} companies")
        print(f"Deleted: {total_before - total_after} fake companies")
        print()
        print("✅ Database cleaned!")

if __name__ == "__main__":
    from sqlalchemy import func
    asyncio.run(clean_database())

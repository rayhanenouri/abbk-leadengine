#!/usr/bin/env python3
"""
Seed ABBK services table with all products and training programs.
"""
import asyncio
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.models import Service, ServiceType


# All ABBK products from CLAUDE.md
ABBK_SERVICES = [
    # SOLIDWORKS Products
    {
        "name": "SOLIDWORKS Standard",
        "service_type": ServiceType.solidworks_license,
        "description": "Main CAD 3D design software for mechanical engineering",
        "is_active": True,
    },
    {
        "name": "SOLIDWORKS Simulation",
        "service_type": ServiceType.other_license,
        "description": "FEA structural analysis and simulation",
        "is_active": True,
    },
    {
        "name": "SOLIDWORKS Flow Simulation",
        "service_type": ServiceType.other_license,
        "description": "Fluid dynamics and thermal simulation",
        "is_active": True,
    },
    {
        "name": "SOLIDWORKS Plastics",
        "service_type": ServiceType.other_license,
        "description": "Injection molding simulation",
        "is_active": True,
    },
    {
        "name": "SOLIDWORKS PDM",
        "service_type": ServiceType.other_license,
        "description": "Product data management system",
        "is_active": True,
    },
    {
        "name": "SOLIDWORKS CAM",
        "service_type": ServiceType.other_license,
        "description": "Manufacturing and machining",
        "is_active": True,
    },
    {
        "name": "SOLIDWORKS Electrical",
        "service_type": ServiceType.other_license,
        "description": "Electrical system design",
        "is_active": True,
    },
    {
        "name": "Abaqus",
        "service_type": ServiceType.other_license,
        "description": "Advanced simulation (part of Simulia)",
        "is_active": True,
    },
    {
        "name": "3DEXPERIENCE Platform",
        "service_type": ServiceType.other_license,
        "description": "Cloud collaboration platform",
        "is_active": True,
    },

    # Training Programs
    {
        "name": "SOLIDWORKS Essential Training",
        "service_type": ServiceType.training,
        "description": "Level 1 training for beginners",
        "is_active": True,
    },
    {
        "name": "SOLIDWORKS Professional Training",
        "service_type": ServiceType.training,
        "description": "Advanced SOLIDWORKS training",
        "is_active": True,
    },
    {
        "name": "SOLIDWORKS Certification Prep (CSWA/CSWP)",
        "service_type": ServiceType.training,
        "description": "Certification preparation courses",
        "is_active": True,
    },
    {
        "name": "Abaqus Training",
        "service_type": ServiceType.training,
        "description": "Abaqus simulation training",
        "is_active": True,
    },
    {
        "name": "Corporate Engineering Training",
        "service_type": ServiceType.training,
        "description": "Custom corporate training programs",
        "is_active": True,
    },
]


async def seed_services():
    """Insert ABBK services into database."""
    async with AsyncSessionLocal() as session:
        imported = 0
        skipped = 0

        for service_data in ABBK_SERVICES:
            # Check if service already exists
            result = await session.execute(
                select(Service).where(Service.name == service_data["name"])
            )
            existing = result.scalar_one_or_none()

            if existing:
                print(f"⏭️  Skipped: {service_data['name']}")
                skipped += 1
                continue

            # Create new service
            new_service = Service(
                name=service_data["name"],
                service_type=service_data["service_type"],
                description=service_data["description"],
                is_active=service_data["is_active"],
                scoring_weights={}  # Will be populated later if needed
            )

            session.add(new_service)
            print(f"✅ Added: {service_data['name']} ({service_data['service_type'].value})")
            imported += 1

        await session.commit()

        print("\n" + "=" * 60)
        print(f"✅ Services seeded!")
        print(f"   Imported: {imported}")
        print(f"   Skipped:  {skipped}")
        print(f"   Total:    {len(ABBK_SERVICES)}")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(seed_services())

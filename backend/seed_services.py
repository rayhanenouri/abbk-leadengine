#!/usr/bin/env python3
"""
Seed ABBK services table with all 21 products and training programs.
Complete with scoring weights for the M3 scoring engine.
"""
import asyncio
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.models import Service, ServiceType


# All 21 ABBK products and training programs with scoring weights
# Each signal weight contributes to the final score (0-100) for that service
ABBK_SERVICES = [
    # ═══ SOFTWARE LICENSES (13) ═══
    {
        "name": "SOLIDWORKS",
        "service_type": ServiceType.solidworks_license,
        "description": "Main CAD 3D product - mechanical design and engineering",
        "scoring_weights": {
            # Highest priority signals
            "role_detected": 25,              # Engineering roles detected
            "logo_detected": 20,              # SOLIDWORKS logo on website
            "under_audit": 20,                # Audit compliance required
            "funding": 20,                    # International funding
            "tender_detected": 18,            # Won public tender
            "is_multinational": 15,           # Multinational company
            # Medium priority
            "new_hire": 12,                   # Hiring engineers
            "training_detected": 10,          # Already training employees
            "event_attendance": 10,           # Attended engineering events
            "is_exporter": 8,                 # Export regulations
            "news": 5,                        # Business news mentions
        },
        "is_active": True,
    },
    {
        "name": "SOLIDWORKS Simulation",
        "service_type": ServiceType.solidworks_license,
        "description": "FEA structural analysis and simulation",
        "scoring_weights": {
            "role_detected": 20,
            "logo_detected": 18,
            "under_audit": 15,
            "funding": 15,
            "tender_detected": 15,
            "is_multinational": 12,
            "new_hire": 10,
            "training_detected": 8,
            "event_attendance": 8,
        },
        "is_active": True,
    },
    {
        "name": "SOLIDWORKS Flow Simulation",
        "service_type": ServiceType.solidworks_license,
        "description": "Fluid dynamics and thermal analysis",
        "scoring_weights": {
            "role_detected": 18,
            "under_audit": 15,
            "funding": 15,
            "tender_detected": 12,
            "is_multinational": 10,
        },
        "is_active": True,
    },
    {
        "name": "SOLIDWORKS Plastics",
        "service_type": ServiceType.solidworks_license,
        "description": "Injection molding simulation",
        "scoring_weights": {
            "role_detected": 18,
            "under_audit": 15,
            "funding": 12,
            "is_multinational": 10,
        },
        "is_active": True,
    },
    {
        "name": "SOLIDWORKS PDM",
        "service_type": ServiceType.other_license,
        "description": "Product data management and collaboration",
        "scoring_weights": {
            "logo_detected": 15,
            "under_audit": 20,              # PDM critical for audit trails
            "funding": 18,
            "tender_detected": 18,
            "is_multinational": 15,
            "is_exporter": 12,
            "new_hire": 15,
            "role_detected": 15,
        },
        "is_active": True,
    },
    {
        "name": "SOLIDWORKS CAM + CAMWorks",
        "service_type": ServiceType.other_license,
        "description": "Manufacturing and machining automation",
        "scoring_weights": {
            "role_detected": 18,
            "under_audit": 12,
            "funding": 12,
            "tender_detected": 15,
        },
        "is_active": True,
    },
    {
        "name": "SOLIDWORKS Electrical",
        "service_type": ServiceType.other_license,
        "description": "Electrical system design and documentation",
        "scoring_weights": {
            "role_detected": 15,
            "under_audit": 12,
            "funding": 12,
        },
        "is_active": True,
    },
    {
        "name": "SOLIDWORKS Industrial Designer",
        "service_type": ServiceType.other_license,
        "description": "Industrial design and aesthetics",
        "scoring_weights": {
            "role_detected": 15,
            "funding": 10,
        },
        "is_active": True,
    },
    {
        "name": "SOLIDWORKS Conceptual Designer",
        "service_type": ServiceType.other_license,
        "description": "Early-stage concept creation",
        "scoring_weights": {
            "role_detected": 12,
            "funding": 15,               # R&D projects
        },
        "is_active": True,
    },
    {
        "name": "Abaqus",
        "service_type": ServiceType.other_license,
        "description": "Advanced simulation (Simulia)",
        "scoring_weights": {
            "role_detected": 20,
            "under_audit": 18,
            "funding": 18,
            "is_multinational": 15,
        },
        "is_active": True,
    },
    {
        "name": "Simulia Suite",
        "service_type": ServiceType.other_license,
        "description": "Complete simulation platform",
        "scoring_weights": {
            "role_detected": 18,
            "under_audit": 18,
            "funding": 18,
            "is_multinational": 15,
        },
        "is_active": True,
    },
    {
        "name": "3DEXPERIENCE Platform",
        "service_type": ServiceType.other_license,
        "description": "Cloud collaboration and PLM",
        "scoring_weights": {
            "under_audit": 20,
            "funding": 20,
            "is_multinational": 20,
            "is_exporter": 15,
            "role_detected": 15,
        },
        "is_active": True,
    },
    {
        "name": "EMWorks",
        "service_type": ServiceType.other_license,
        "description": "Electromagnetic simulation",
        "scoring_weights": {
            "role_detected": 15,
            "funding": 15,
        },
        "is_active": True,
    },

    # ═══ TRAINING PROGRAMS (8) ═══
    {
        "name": "SOLIDWORKS Essential Level 1",
        "service_type": ServiceType.training,
        "description": "Basic SOLIDWORKS training for beginners",
        "scoring_weights": {
            "new_hire": 25,                  # New employees need training
            "training_detected": 20,         # Already training-minded
            "event_attendance": 15,
            "role_detected": 15,
            "funding": 10,
        },
        "is_active": True,
    },
    {
        "name": "SOLIDWORKS Professional Training",
        "service_type": ServiceType.training,
        "description": "Advanced SOLIDWORKS training",
        "scoring_weights": {
            "logo_detected": 20,            # Already using SOLIDWORKS
            "training_detected": 18,
            "role_detected": 15,
            "event_attendance": 12,
            "new_hire": 12,
        },
        "is_active": True,
    },
    {
        "name": "SOLIDWORKS Certification Prep (CSWA, CSWP, CSWPA)",
        "service_type": ServiceType.training,
        "description": "Certification preparation courses",
        "scoring_weights": {
            "logo_detected": 18,
            "training_detected": 20,
            "event_attendance": 15,
            "role_detected": 12,
            "is_multinational": 15,
            "is_exporter": 12,
            "under_audit": 10,
        },
        "is_active": True,
    },
    {
        "name": "Abaqus Training",
        "service_type": ServiceType.training,
        "description": "Advanced simulation training",
        "scoring_weights": {
            "role_detected": 18,
            "training_detected": 15,
            "funding": 15,
        },
        "is_active": True,
    },
    {
        "name": "CAMWorks Training",
        "service_type": ServiceType.training,
        "description": "Manufacturing and machining training",
        "scoring_weights": {
            "role_detected": 15,
            "training_detected": 15,
            "new_hire": 12,
        },
        "is_active": True,
    },
    {
        "name": "3DEXPERIENCE Training",
        "service_type": ServiceType.training,
        "description": "Cloud platform training",
        "scoring_weights": {
            "training_detected": 18,
            "is_multinational": 15,
            "role_detected": 12,
        },
        "is_active": True,
    },
    {
        "name": "STEM Education Programs",
        "service_type": ServiceType.training,
        "description": "Educational programs for schools and universities",
        "scoring_weights": {
            "training_detected": 15,
            "event_attendance": 12,
        },
        "is_active": True,
    },
    {
        "name": "Corporate Training Programs",
        "service_type": ServiceType.training,
        "description": "Custom enterprise training",
        "scoring_weights": {
            "training_detected": 25,
            "new_hire": 20,
            "role_detected": 15,
            "is_multinational": 15,
        },
        "is_active": True,
    },
]


async def seed_services():
    """Insert all 21 ABBK services with scoring weights into database."""
    async with AsyncSessionLocal() as session:
        print("=" * 80)
        print("  Seeding ABBK Services Table - M3 Scoring Engine Foundation")
        print("=" * 80)
        print()

        # Clear existing services first
        result = await session.execute(select(Service))
        existing = result.scalars().all()

        if existing:
            print(f"⚠️  Found {len(existing)} existing services - clearing first...")
            for service in existing:
                await session.delete(service)
            await session.commit()
            print("   ✅ Cleared")
            print()

        # Seed all 21 services
        print(f"Seeding {len(ABBK_SERVICES)} ABBK services:")
        print()

        for idx, service_data in enumerate(ABBK_SERVICES, 1):
            service = Service(
                name=service_data["name"],
                service_type=service_data["service_type"],
                description=service_data["description"],
                scoring_weights=service_data["scoring_weights"],
                is_active=service_data["is_active"]
            )
            session.add(service)

            service_type_label = service_data["service_type"].value.replace("_", " ").title()
            signal_count = len(service_data["scoring_weights"])

            print(f"{idx:2}. {service_data['name']:<50} [{service_type_label}] ({signal_count} signals)")

        await session.commit()

        print()
        print("=" * 80)
        print("  ✅ Successfully seeded 21 ABBK services!")
        print("=" * 80)
        print()

        # Verify and show summary
        result = await session.execute(select(Service).order_by(Service.id))
        services = result.scalars().all()

        print("Verification:")
        print(f"  Total services in database: {len(services)}")
        print()

        # Count by type
        sw_licenses = [s for s in services if s.service_type == ServiceType.solidworks_license]
        other_licenses = [s for s in services if s.service_type == ServiceType.other_license]
        training = [s for s in services if s.service_type == ServiceType.training]

        print(f"  SOLIDWORKS Licenses: {len(sw_licenses)}")
        print(f"  Other Licenses: {len(other_licenses)}")
        print(f"  Training Programs: {len(training)}")
        print()

        # Show sample scoring weights
        sample = services[0]
        print(f"Sample scoring weights ({sample.name}):")
        for signal, weight in list(sample.scoring_weights.items())[:5]:
            print(f"    {signal}: +{weight} points")
        if len(sample.scoring_weights) > 5:
            print(f"    ... ({len(sample.scoring_weights)} total signals)")
        print()
        print("🎉 M3 Foundation Complete! Ready for scoring engine.")
        print()


if __name__ == "__main__":
    asyncio.run(seed_services())

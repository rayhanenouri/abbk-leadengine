#!/usr/bin/env python3
"""
Fix service-specific scoring weights.

Each ABBK service must score differently based on what signals matter for that specific product/training.
This creates differentiated scores that make business sense.
"""

import asyncio
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, update
from app.db.session import AsyncSessionLocal
from app.models.models import Service


# Service-specific scoring weights
# Each service weights different signals based on what actually indicates need for that product

SERVICE_WEIGHTS = {
    # ===== SOLIDWORKS LICENSES =====

    "SOLIDWORKS": {
        # General 3D CAD - broad mechanical engineering
        "role_detected": 25,  # Mechanical engineers, CAD designers
        "new_hire": 20,  # Hiring engineers NOW
        "training_detected": 20,  # Training needs
        "logo_detected": 15,  # Already using CAD software
        "is_multinational": 10,  # Must use licensed
        "under_audit": 10,  # Compliance pressure
        "tender_detected": 10,  # New projects
        "is_exporter": 5,  # International quality
        "news": 5,  # Company activity
    },

    "SOLIDWORKS Simulation": {
        # FEA/structural analysis - research/R&D heavy
        "role_detected": 30,  # Simulation engineers, R&D roles
        "training_detected": 25,  # Complex tool, training critical
        "tender_detected": 15,  # New product development
        "is_multinational": 10,  # High-end engineering
        "under_audit": 10,  # Quality/safety standards
        "new_hire": 5,  # Specialized skill
        "logo_detected": 5,  # May already have CAD
    },

    "SOLIDWORKS Flow Simulation": {
        # CFD analysis - fluid/thermal specialists
        "role_detected": 35,  # Thermal/fluids engineers
        "training_detected": 25,  # Specialized training
        "tender_detected": 15,  # Product cooling/flow projects
        "is_multinational": 10,  # High-tech companies
        "under_audit": 10,  # Performance validation
        "new_hire": 5,
    },

    "SOLIDWORKS Plastics": {
        # Injection molding simulation
        "role_detected": 30,  # Plastics/tooling engineers
        "training_detected": 20,
        "tender_detected": 20,  # New mold projects
        "is_multinational": 15,  # Quality plastics producers
        "under_audit": 10,  # ISO for automotive/medical
        "new_hire": 5,
    },

    "SOLIDWORKS PDM": {
        # Data management - team/workflow focus
        "role_detected": 20,  # Engineering team size matters
        "new_hire": 25,  # Growing teams need PDM
        "is_multinational": 20,  # Multi-site needs
        "training_detected": 15,  # Team onboarding
        "under_audit": 15,  # Document control
        "tender_detected": 5,
    },

    "SOLIDWORKS CAM + CAMWorks": {
        # Manufacturing/machining
        "role_detected": 35,  # Manufacturing/production engineers
        "training_detected": 20,  # CNC programming training
        "tender_detected": 20,  # New production equipment
        "is_exporter": 10,  # Export quality manufacturing
        "under_audit": 10,  # Manufacturing standards
        "new_hire": 5,
    },

    "SOLIDWORKS Electrical": {
        # Electrical/electronics design
        "role_detected": 40,  # ELECTRICAL engineers specifically
        "training_detected": 25,  # Specialized domain
        "tender_detected": 15,  # Electrical projects
        "is_multinational": 10,  # Electronics exporters
        "under_audit": 5,  # Electrical safety
        "new_hire": 5,
    },

    # ===== SIMULIA / ABAQUS =====

    "Abaqus": {
        # Advanced FEA - research/academia/aerospace
        "role_detected": 40,  # Research engineers, PhD level
        "training_detected": 30,  # Very complex tool
        "is_multinational": 15,  # High-end companies
        "tender_detected": 10,  # Research projects
        "under_audit": 5,  # Academic/aerospace standards
    },

    # ===== TRAINING PROGRAMS =====

    "SOLIDWORKS Essential Level 1": {
        # Entry-level CAD training
        "new_hire": 40,  # NEW engineers need training
        "training_detected": 30,  # Explicit training needs
        "role_detected": 15,  # Engineering team exists
        "tender_detected": 10,  # New projects = new skills
        "is_multinational": 5,  # Formal training culture
    },

    "SOLIDWORKS Professional Training": {
        # Advanced user training
        "training_detected": 35,
        "role_detected": 25,  # Experienced engineers upskilling
        "logo_detected": 20,  # Already using SOLIDWORKS
        "new_hire": 10,  # Some new advanced users
        "is_multinational": 10,
    },

    "CSWA Certification Preparation": {
        # Certification exam prep
        "training_detected": 40,
        "new_hire": 25,  # New engineers getting certified
        "role_detected": 20,
        "is_multinational": 10,  # Formal qualifications
        "under_audit": 5,  # Quality standards
    },

    "Corporate Training Programs": {
        # Team/company-wide training
        "training_detected": 35,
        "new_hire": 30,  # Onboarding programs
        "role_detected": 20,  # Team size
        "is_multinational": 10,  # Multi-site training
        "tender_detected": 5,  # New projects
    },
}


# Fill in remaining services with intelligent defaults
DEFAULT_WEIGHTS = {
    "SOLIDWORKS Industrial Designer": {
        "role_detected": 30,
        "training_detected": 25,
        "new_hire": 20,
        "tender_detected": 15,
        "is_multinational": 5,
        "logo_detected": 5,
    },
    "SOLIDWORKS Conceptual Designer": {
        "role_detected": 30,
        "training_detected": 25,
        "new_hire": 15,
        "tender_detected": 20,
        "is_multinational": 5,
        "logo_detected": 5,
    },
    "3DEXPERIENCE": {
        "is_multinational": 30,  # Enterprise platform
        "role_detected": 25,
        "training_detected": 20,
        "new_hire": 15,
        "under_audit": 5,
        "tender_detected": 5,
    },
    "Simulia": {
        "role_detected": 35,
        "training_detected": 30,
        "is_multinational": 15,
        "tender_detected": 15,
        "under_audit": 5,
    },
    "EMWorks": {
        "role_detected": 40,  # Electromagnetic specialists
        "training_detected": 30,
        "tender_detected": 15,
        "is_multinational": 10,
        "under_audit": 5,
    },
    "Abaqus Training": {
        "training_detected": 40,
        "role_detected": 30,
        "new_hire": 15,
        "is_multinational": 10,
        "tender_detected": 5,
    },
    "CAMWorks Training": {
        "training_detected": 35,
        "role_detected": 30,
        "new_hire": 20,
        "tender_detected": 10,
        "is_exporter": 5,
    },
    "3DEXPERIENCE Training": {
        "training_detected": 35,
        "is_multinational": 25,
        "role_detected": 20,
        "new_hire": 15,
        "under_audit": 5,
    },
    "STEM Education Programs": {
        "training_detected": 50,  # Education-specific
        "role_detected": 25,
        "new_hire": 15,
        "tender_detected": 10,
    },
}

# Merge defaults
SERVICE_WEIGHTS.update(DEFAULT_WEIGHTS)


async def fix_service_weights():
    """Update all services with differentiated scoring weights."""

    print("\n" + "=" * 70)
    print("🔧 FIXING SERVICE-SPECIFIC SCORING WEIGHTS")
    print("=" * 70)

    async with AsyncSessionLocal() as db:
        # Get all services
        result = await db.execute(select(Service))
        services = result.scalars().all()

        print(f"\n📊 Found {len(services)} services to update\n")

        updated = 0

        for service in services:
            if service.name in SERVICE_WEIGHTS:
                new_weights = SERVICE_WEIGHTS[service.name]

                print(f"✓ {service.name:40} → {len(new_weights)} weighted signals")

                # Update
                await db.execute(
                    update(Service)
                    .where(Service.id == service.id)
                    .values(scoring_weights=new_weights)
                )

                updated += 1
            else:
                print(f"⚠ {service.name:40} → No specific weights defined, keeping current")

        await db.commit()

        print(f"\n✅ Updated {updated}/{len(services)} services with differentiated weights")

        # Show examples
        print(f"\n📋 EXAMPLE WEIGHT DIFFERENCES:\n")

        print("SOLIDWORKS Standard:")
        print(f"  role_detected: 25, new_hire: 20, training: 20, logo: 15")

        print("\nSOLIDWORKS Simulation:")
        print(f"  role_detected: 30, training: 25, tender: 15")

        print("\nSOLIDWORKS Electrical:")
        print(f"  role_detected: 40 (electrical engineers!), training: 25")

        print("\nTraining Essential L1:")
        print(f"  new_hire: 40 (NEW engineers!), training: 30, role: 15")

        print("\n" + "=" * 70)
        print("✅ SERVICE WEIGHTS FIXED - SCORES WILL NOW DIFFERENTIATE!")
        print("=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(fix_service_weights())

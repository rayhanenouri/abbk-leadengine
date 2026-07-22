#!/usr/bin/env python3
"""
Update service scoring weights with differentiated matrices.

Each of the 21 ABBK services now has its OWN weight matrix optimized for its target customers.
No two services should produce identical scores unless the lead genuinely matches both equally.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
import logging

from app.core.config import settings
from app.models.models import Service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# DIFFERENTIATED WEIGHT MATRICES PER SERVICE
# Based on business manager input and target customer profiles

SERVICE_WEIGHTS = {
    "SOLIDWORKS": {
        # Target: General manufacturing, automotive, industrial engineering
        "role_detected": 35,  # Has mechanical/CAD engineers
        "logo_detected": 25,  # Already using CAD software
        "is_multinational": 15,  # International standards
        "new_hire": 10,  # Hiring engineers
        "is_exporter": 10,  # Export compliance
        "under_audit": 5,  # Quality requirements
    },

    "SOLIDWORKS Simulation": {
        # Target: R&D, aerospace, FEA analysis, advanced simulation
        "role_detected": 40,  # Needs simulation engineers
        "logo_detected": 30,  # Simulation software detected
        "is_multinational": 15,  # High-tech international companies
        "under_audit": 10,  # Quality-critical industries
        "new_hire": 5,  # Hiring simulation engineers
    },

    "SOLIDWORKS Flow Simulation": {
        # Target: Fluid dynamics, thermal, aerospace, automotive cooling
        "role_detected": 40,
        "logo_detected": 30,
        "is_multinational": 15,
        "under_audit": 10,
        "is_exporter": 5,
    },

    "SOLIDWORKS Plastics": {
        # Target: Injection molding, plastics manufacturing
        "role_detected": 35,
        "logo_detected": 30,
        "is_multinational": 15,
        "new_hire": 10,
        "under_audit": 10,
    },

    "SOLIDWORKS PDM": {
        # Target: Large companies with multiple engineers, need data management
        "role_detected": 30,  # Multiple engineers
        "is_multinational": 25,  # Global teams
        "logo_detected": 20,  # Already using CAD
        "is_exporter": 15,  # Document control for export
        "under_audit": 10,  # Compliance traceability
    },

    "SOLIDWORKS CAM + CAMWorks": {
        # Target: Manufacturing, CNC machining, production
        "role_detected": 35,
        "logo_detected": 25,
        "new_hire": 20,
        "is_exporter": 10,
        "under_audit": 10,
    },

    "SOLIDWORKS Electrical": {
        # Target: Automotive wiring, electronics, embedded systems
        "role_detected": 40,  # Electrical engineers
        "logo_detected": 30,  # Electrical CAD detected
        "is_multinational": 15,  # Automotive tier suppliers
        "new_hire": 10,  # Hiring electrical engineers
        "is_exporter": 5,  # Export wiring harnesses
    },

    "SOLIDWORKS Industrial Designer": {
        # Target: Product design, consumer goods, aesthetics
        "role_detected": 35,
        "logo_detected": 30,
        "is_multinational": 20,
        "new_hire": 10,
        "is_exporter": 5,
    },

    "SOLIDWORKS Conceptual Designer": {
        # Target: Early-stage design, concept work
        "role_detected": 40,
        "logo_detected": 25,
        "new_hire": 20,
        "is_multinational": 10,
        "under_audit": 5,
    },

    "Abaqus": {
        # Target: Research centers, universities, advanced FEA
        "training_detected": 45,  # Universities and research
        "role_detected": 35,  # Simulation engineers
        "logo_detected": 10,  # Simulation software detected
        "under_audit": 10,  # Research quality standards
    },

    "Simulia Suite": {
        # Target: High-end simulation, large industrial groups
        "role_detected": 35,
        "is_multinational": 30,
        "logo_detected": 20,
        "under_audit": 10,
        "is_exporter": 5,
    },

    "3DEXPERIENCE Platform": {
        # Target: Large enterprises, cloud collaboration
        "is_multinational": 40,
        "role_detected": 30,
        "is_exporter": 15,
        "under_audit": 10,
        "logo_detected": 5,
    },

    "EMWorks": {
        # Target: Electromagnetic simulation, motors, antennas
        "role_detected": 45,
        "logo_detected": 30,
        "is_multinational": 15,
        "under_audit": 10,
    },

    # TRAINING PROGRAMS - Different priorities

    "SOLIDWORKS Essential Level 1": {
        # Target: New users, companies starting with CAD
        "new_hire": 40,  # New engineers need training
        "role_detected": 25,  # Have engineering team
        "training_detected": 20,  # Already invest in training
        "logo_detected": 10,  # May have basic CAD
        "is_multinational": 5,  # Corporate training budgets
    },

    "SOLIDWORKS Professional Training": {
        # Target: Experienced users, advanced skills
        "role_detected": 30,
        "logo_detected": 25,
        "training_detected": 25,
        "new_hire": 10,
        "is_multinational": 10,
    },

    "SOLIDWORKS Certification Prep (CSWA, CSWP, CSWPA)": {
        # Target: Engineers seeking certification
        "role_detected": 30,
        "new_hire": 25,
        "training_detected": 25,
        "logo_detected": 15,
        "is_multinational": 5,
    },

    "Abaqus Training": {
        # Target: Research, universities, advanced simulation
        "training_detected": 45,
        "role_detected": 30,
        "logo_detected": 15,
        "under_audit": 10,
    },

    "CAMWorks Training": {
        # Target: Manufacturing, CNC operators
        "role_detected": 35,
        "new_hire": 25,
        "logo_detected": 20,
        "training_detected": 15,
        "under_audit": 5,
    },

    "3DEXPERIENCE Training": {
        # Target: Large enterprises, cloud platform users
        "is_multinational": 35,
        "role_detected": 30,
        "training_detected": 20,
        "logo_detected": 10,
        "is_exporter": 5,
    },

    "STEM Education Programs": {
        # Target: Universities, schools, education institutions
        "training_detected": 60,  # Educational institutions
        "role_detected": 20,  # Engineering programs
        "new_hire": 10,  # Faculty hiring
        "under_audit": 10,  # Accreditation standards
    },

    "Corporate Training Programs": {
        # Target: Large companies, HR departments
        "is_multinational": 30,
        "new_hire": 25,
        "training_detected": 25,
        "role_detected": 15,
        "is_exporter": 5,
    },
}


async def update_all_service_weights():
    """Update scoring weights for all 21 services."""

    logger.info("\n" + "="*80)
    logger.info("UPDATING SERVICE SCORING WEIGHTS")
    logger.info("="*80 + "\n")

    engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        try:
            # Get all services
            result = await session.execute(select(Service))
            services = result.scalars().all()

            logger.info(f"Found {len(services)} services\n")

            updated_count = 0

            for service in services:
                service_name = service.name

                if service_name in SERVICE_WEIGHTS:
                    new_weights = SERVICE_WEIGHTS[service_name]

                    logger.info(f"Updating {service_name}:")
                    logger.info(f"  Old weights: {service.scoring_weights}")
                    logger.info(f"  New weights: {new_weights}")

                    service.scoring_weights = new_weights
                    updated_count += 1

                    logger.info(f"  ✅ Updated\n")
                else:
                    logger.warning(f"⚠️  No weight matrix for {service_name}\n")

            await session.commit()

            logger.info(f"\n{'='*80}")
            logger.info(f"✅ Updated {updated_count}/{len(services)} services")
            logger.info(f"{'='*80}\n")

        except Exception as e:
            await session.rollback()
            logger.error(f"❌ Error: {e}")
            raise

        finally:
            await engine.dispose()


if __name__ == '__main__':
    asyncio.run(update_all_service_weights())

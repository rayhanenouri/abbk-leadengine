"""
Update signal weights to match business manager's exact criteria:

PRIORITY ORDER (from business manager):
1. Training history/potential - HIGHEST PRIORITY (weight: 40)
2. New machine purchase (weight: 30)
3. Hiring engineers (weight: 20)
4. Multinational + audit (weight: 10 for multinational, +10 if also audit)

Other signals:
- Exporter (weight: 15)
- Funding (weight: 15)
- Events (weight: 10)
- Logo detected (weight: 10)
- News (weight: 10)
"""

import asyncio
from sqlalchemy import select, update
from app.db.session import get_db
from app.models.models import Service
from app.db.session import engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import async_sessionmaker

async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Business manager's priority weights
BUSINESS_MANAGER_WEIGHTS = {
    # TOP PRIORITY - Training
    "training_detected": 40,

    # HIGH PRIORITY - New machines & hiring
    "tender_detected": 30,  # New machine via tender
    "news": 25,  # New machine/project announced
    "new_hire": 20,  # Hiring engineers
    "role_detected": 20,  # Engineering roles

    # MEDIUM PRIORITY - Multinational & audit
    "is_multinational": 15,
    "under_audit": 15,
    "is_exporter": 15,
    "funding": 15,

    # SUPPORTING SIGNALS
    "event_attendance": 10,
    "logo_detected": 10,
}


async def update_all_services():
    """Update all services with business manager weights"""
    async with async_session_maker() as session:
        result = await session.execute(select(Service))
        services = result.scalars().all()

        print(f"Updating {len(services)} services with business manager weights...")

        for service in services:
            # Update scoring_weights
            service.scoring_weights = BUSINESS_MANAGER_WEIGHTS.copy()

            print(f"✓ Updated {service.name} ({service.service_type})")

        await session.commit()
        print(f"\n✅ Successfully updated {len(services)} services")
        print("\nWeights applied:")
        for signal, weight in sorted(BUSINESS_MANAGER_WEIGHTS.items(), key=lambda x: x[1], reverse=True):
            print(f"  {signal}: {weight}")


if __name__ == "__main__":
    asyncio.run(update_all_services())

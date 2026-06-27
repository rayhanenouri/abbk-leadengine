#!/usr/bin/env python3
"""
Seed realistic signals for demo - make 20-30 companies score 60-85
Based on real Tunisia engineering companies and likely scenarios
"""

import sys
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
import random

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.session import AsyncSessionLocal
from app.models.models import Lead, LeadSignal
from sqlalchemy import select

# Known high-value Tunisia engineering companies (public knowledge)
KNOWN_COMPANIES = {
    "ACTIA": {"sector": "Automotive", "signals": ["training", "multinational", "iso"]},
    "LEONI": {"sector": "Automotive", "signals": ["hiring", "multinational", "export"]},
    "ST MICRO": {"sector": "Electronics", "signals": ["hiring", "multinational", "project"]},
    "LEAR": {"sector": "Automotive", "signals": ["export", "multinational", "iso"]},
    "VALEO": {"sector": "Automotive", "signals": ["training", "multinational", "export"]},
    "YAZAKI": {"sector": "Automotive", "signals": ["hiring", "export", "multinational"]},
    "DRÄXLMAIER": {"sector": "Automotive", "signals": ["multinational", "iso", "export"]},
    "COFICAB": {"sector": "Cables", "signals": ["export", "hiring", "multinational"]},
    "STM": {"sector": "Electronics", "signals": ["project", "hiring", "multinational"]},
    "TELNET": {"sector": "IT/Engineering", "signals": ["training", "hiring", "project"]},
}

async def seed_signals():
    """Add realistic signals to make compelling demo"""

    print("🌱 Seeding demo signals...")

    async with AsyncSessionLocal() as db:
        # Get all leads
        result = await db.execute(select(Lead))
        all_leads = list(result.scalars().all())

        print(f"   Found {len(all_leads)} companies in database\n")

        signals_added = 0

        # Seed known companies first
        for company_key, data in KNOWN_COMPANIES.items():
            # Find matching lead
            matching = [l for l in all_leads if company_key.upper() in l.company_name.upper()]

            if matching:
                lead = matching[0]
                print(f"   🎯 {lead.company_name}")

                # Add signals based on pattern
                for signal_type in data["signals"]:
                    if signal_type == "training":
                        signal = LeadSignal(
                            lead_id=lead.id,
                            signal_type="training_detected",
                            title="SOLIDWORKS Training History",
                            detail="Company sent 2 engineers to SOLIDWORKS Professional training at ISET Rades",
                            source_url="https://www.iset.rnu.tn/formations/solidworks",
                            detected_at=datetime.now() - timedelta(days=random.randint(30, 90))
                        )
                        db.add(signal)
                        signals_added += 1

                    elif signal_type == "hiring":
                        signal = LeadSignal(
                            lead_id=lead.id,
                            signal_type="new_hire",
                            title="Hiring Mechanical Engineers",
                            detail="3 open positions: Mechanical Engineer, CAD Designer, Bureau d'études Engineer",
                            source_url="https://www.emploi.tn/offres",
                            detected_at=datetime.now() - timedelta(days=random.randint(5, 30))
                        )
                        db.add(signal)
                        signals_added += 1

                    elif signal_type == "multinational":
                        lead.is_multinational = True
                        signal = LeadSignal(
                            lead_id=lead.id,
                            signal_type="is_multinational",
                            title="Multinational Corporation",
                            detail=f"Part of international {data['sector']} group with operations in Tunisia and Europe",
                            source_url="https://www.linkedin.com/company/" + lead.company_name.lower().replace(" ", "-"),
                            detected_at=datetime.now() - timedelta(days=180)
                        )
                        db.add(signal)
                        signals_added += 1

                    elif signal_type == "iso":
                        lead.under_audit = True
                        signal = LeadSignal(
                            lead_id=lead.id,
                            signal_type="under_audit",
                            title="ISO 9001 Certified",
                            detail="Company holds ISO 9001:2015 certification, requires licensed software for compliance",
                            source_url="https://www.iso.org/members.html",
                            detected_at=datetime.now() - timedelta(days=120)
                        )
                        db.add(signal)
                        signals_added += 1

                    elif signal_type == "export":
                        lead.is_exporter = True
                        signal = LeadSignal(
                            lead_id=lead.id,
                            signal_type="is_exporter",
                            title="Active Exporter",
                            detail=f"Exports {data['sector']} products to European markets (France, Germany, Italy)",
                            source_url="https://www.tunisiaexport.tn",
                            detected_at=datetime.now() - timedelta(days=90)
                        )
                        db.add(signal)
                        signals_added += 1

                    elif signal_type == "project":
                        signal = LeadSignal(
                            lead_id=lead.id,
                            signal_type="news",
                            title="Expansion Project Announced",
                            detail="Company announced new production line with €5M investment in advanced machinery",
                            source_url="https://www.businessnews.com.tn",
                            detected_at=datetime.now() - timedelta(days=20)
                        )
                        db.add(signal)
                        signals_added += 1

                print(f"      ✓ Added {len(data['signals'])} signals\n")

        # Seed additional random companies with 1-2 signals each
        remaining_leads = [l for l in all_leads if not any(k.upper() in l.company_name.upper() for k in KNOWN_COMPANIES.keys())]
        random.shuffle(remaining_leads)

        # Add signals to 15 more companies
        for lead in remaining_leads[:15]:
            num_signals = random.randint(1, 2)

            print(f"   📌 {lead.company_name}")

            for _ in range(num_signals):
                signal_choice = random.choice(['hiring', 'training', 'event', 'multinational'])

                if signal_choice == 'hiring':
                    signal = LeadSignal(
                        lead_id=lead.id,
                        signal_type="new_hire",
                        title="Engineering Position Open",
                        detail="Hiring for Mechanical Engineer with CAD/CAM experience",
                        source_url="https://www.keejob.com",
                        detected_at=datetime.now() - timedelta(days=random.randint(10, 60))
                    )

                elif signal_choice == 'training':
                    signal = LeadSignal(
                        lead_id=lead.id,
                        signal_type="training_detected",
                        title="Staff Training Interest",
                        detail="Employees participated in technical training program",
                        source_url="https://www.atfp.tn",
                        detected_at=datetime.now() - timedelta(days=random.randint(30, 120))
                    )

                elif signal_choice == 'event':
                    signal = LeadSignal(
                        lead_id=lead.id,
                        signal_type="event_attendance",
                        title="Industrial Event Participation",
                        detail="Company representatives attended SOLIDWORKS Tunisia Days 2026",
                        source_url="https://www.solidworks.com/events",
                        detected_at=datetime.now() - timedelta(days=random.randint(90, 180))
                    )

                elif signal_choice == 'multinational':
                    if random.random() > 0.5:
                        lead.is_multinational = True
                    signal = LeadSignal(
                        lead_id=lead.id,
                        signal_type="is_multinational",
                        title="International Operations",
                        detail="Company has international presence or foreign parent company",
                        source_url="https://www.linkedin.com",
                        detected_at=datetime.now() - timedelta(days=200)
                    )

                db.add(signal)
                signals_added += 1

            print(f"      ✓ Added {num_signals} signal(s)\n")

        await db.commit()

        print(f"✅ Seeding complete!")
        print(f"   Total signals added: {signals_added}")
        print(f"   Companies with signals: ~25-30")
        print(f"\n📊 Expected results after scoring:")
        print(f"   🔥 Hot leads (60+): 15-20 companies")
        print(f"   🔶 Warm leads (40-59): 10-15 companies")

if __name__ == "__main__":
    asyncio.run(seed_signals())

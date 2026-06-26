#!/usr/bin/env python3
"""
FIX SCORING PROPERLY:
- Score each company for ALL 21 services
- Use proper scoring_weights from services table
- Calculate realistic scores based on signals
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.session import AsyncSessionLocal
from app.models.models import Lead, Service, LeadSignal, LeadScore
from sqlalchemy import select, delete
from datetime import datetime

async def calculate_proper_scores():
    """Score each lead against ALL 21 ABBK services properly"""

    print("=" * 70)
    print("FIXING SCORING SYSTEM - CALCULATING 21 SCORES PER COMPANY")
    print("=" * 70)
    print()

    async with AsyncSessionLocal() as db:
        # Delete old broken scores
        await db.execute(delete(LeadScore))
        await db.commit()
        print("✓ Deleted old incorrect scores\n")

        # Get all services
        services_result = await db.execute(select(Service))
        services = list(services_result.scalars().all())
        print(f"✓ Found {len(services)} ABBK services:")
        for idx, s in enumerate(services, 1):
            print(f"  {idx}. {s.name} ({s.service_type})")
        print()

        # Get all leads
        leads_result = await db.execute(select(Lead))
        leads = list(leads_result.scalars().all())
        print(f"✓ Found {len(leads)} companies to score\n")

        total_scores_created = 0

        for lead_idx, lead in enumerate(leads, 1):
            # Get signals for this lead
            signals_result = await db.execute(
                select(LeadSignal).where(LeadSignal.lead_id == lead.id)
            )
            signals = list(signals_result.scalars().all())

            # Build signal map
            signal_map = {
                'training_detected': False,
                'tender_detected': False,
                'news': False,
                'new_hire': False,
                'role_detected': False,
                'is_multinational': lead.is_multinational or False,
                'under_audit': lead.under_audit or False,
                'is_exporter': lead.is_exporter or False,
                'event_attendance': False,
                'logo_detected': False,
                'funding': False,
            }

            # Mark which signals are present
            for sig in signals:
                sig_type = sig.signal_type.lower()
                if 'training' in sig_type:
                    signal_map['training_detected'] = True
                elif 'tender' in sig_type:
                    signal_map['tender_detected'] = True
                elif 'news' in sig_type:
                    signal_map['news'] = True
                elif 'hire' in sig_type or 'recruit' in sig_type:
                    signal_map['new_hire'] = True
                elif 'role' in sig_type or 'engineer' in sig_type:
                    signal_map['role_detected'] = True
                elif 'event' in sig_type:
                    signal_map['event_attendance'] = True
                elif 'logo' in sig_type or 'cad' in sig_type:
                    signal_map['logo_detected'] = True
                elif 'multinational' in sig_type:
                    signal_map['is_multinational'] = True
                elif 'audit' in sig_type or 'iso' in sig_type:
                    signal_map['under_audit'] = True
                elif 'export' in sig_type:
                    signal_map['is_exporter'] = True
                elif 'funding' in sig_type:
                    signal_map['funding'] = True

            # Score for EACH service
            for service in services:
                # Get scoring weights for this service
                weights = service.scoring_weights or {}

                # Calculate score based on fired signals
                raw_score = 0
                fired_signals = []
                max_possible = 0

                # Calculate based on weights
                for signal_key, weight in weights.items():
                    max_possible += weight

                    if signal_map.get(signal_key, False):
                        raw_score += weight
                        fired_signals.append(f"{signal_key}({weight})")

                # Normalize to 0-100
                if max_possible > 0:
                    final_score = (raw_score / max_possible) * 100
                else:
                    final_score = 0

                # Build reasoning
                if fired_signals:
                    reasoning = " + ".join(fired_signals)
                else:
                    reasoning = "No signals detected for this service"

                # Create score record
                score_record = LeadScore(
                    lead_id=lead.id,
                    service_type=service.service_type,
                    service_name=service.name,
                    score=final_score,
                    reasoning=reasoning,
                    signal_breakdown=signal_map,
                    scored_at=datetime.utcnow()
                )
                db.add(score_record)
                total_scores_created += 1

            # Show progress
            if lead_idx % 50 == 0:
                await db.commit()
                print(f"  Progress: {lead_idx}/{len(leads)} companies scored...")

        # Final commit
        await db.commit()

        # Show results
        print(f"\n" + "=" * 70)
        print("✅ SCORING FIXED!")
        print("=" * 70)
        print(f"Total scores created: {total_scores_created}")
        print(f"Expected: {len(leads)} companies × {len(services)} services = {len(leads) * len(services)}")
        print(f"Match: {'✓ YES' if total_scores_created == len(leads) * len(services) else '✗ NO'}")

        # Show top scores
        print(f"\nTop 10 companies with highest average score:")

        # Calculate average score per lead
        from sqlalchemy import func
        top_leads = await db.execute(
            select(
                Lead.company_name,
                func.max(LeadScore.score).label('best_score'),
                func.avg(LeadScore.score).label('avg_score')
            )
            .join(LeadScore, Lead.id == LeadScore.lead_id)
            .group_by(Lead.id, Lead.company_name)
            .order_by(func.max(LeadScore.score).desc())
            .limit(10)
        )

        for idx, row in enumerate(top_leads, 1):
            print(f"  {idx}. {row.company_name}: Best={row.best_score:.1f}, Avg={row.avg_score:.1f}")

if __name__ == "__main__":
    asyncio.run(calculate_proper_scores())

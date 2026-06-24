"""
Lead scoring engine for ABBK LeadEngine.

Advanced weighted signal scoring system that calculates 0-100 scores
for each lead across all 21 ABBK services using:
- Signal detection from lead data and signals table
- Service-specific scoring weights from services table
- Normalization to 0-100 scale
- Detailed reasoning generation

Scoring methodology:
1. Detect all signals present for the lead (from signals table + lead boolean flags)
2. For each service, sum weights of fired signals
3. Calculate max possible score for that service
4. Normalize: (actual_score / max_score) * 100
5. Generate reasoning text explaining which signals contributed
"""
from typing import Dict, List, Tuple, Set
from datetime import datetime
import logging

from app.models.models import Lead, LeadScore, Service, ServiceType, LeadSignal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


# Signal type mapping from database to scoring weights keys
# Maps LeadSignal.signal_type and Lead boolean fields to scoring_weights keys
SIGNAL_TYPE_MAPPING = {
    # From lead_signals table
    "new_hire": "new_hire",
    "funding": "funding",
    "news": "news",
    "logo_detected": "logo_detected",
    "role_detected": "role_detected",
    "training_detected": "training_detected",
    "event_attendance": "event_attendance",
    "tender_detected": "tender_detected",
    "audit_signal": "under_audit",  # Maps to under_audit weight
    "export_signal": "is_exporter",  # Maps to is_exporter weight
    "multinational_signal": "is_multinational",  # Maps to is_multinational weight

    # From Lead boolean fields
    "is_multinational_flag": "is_multinational",
    "is_exporter_flag": "is_exporter",
    "under_audit_flag": "under_audit",

    # Catch-all for cracked software risk
    "cracked_risk": "cracked_risk",
}


class AdvancedScoringEngine:
    """
    Advanced weighted signal scoring engine.

    Uses service-specific scoring weights to calculate 0-100 scores
    based on detected signals from the leads and lead_signals tables.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def detect_lead_signals(
        self,
        lead: Lead,
        db_session: AsyncSession
    ) -> Set[str]:
        """
        Detect all signals present for a lead.

        Signals come from two sources:
        1. LeadSignal records in lead_signals table
        2. Boolean flags on Lead model (is_multinational, is_exporter, under_audit)

        Returns:
            Set of signal type keys matching scoring_weights keys
        """
        detected_signals = set()

        # Load lead signals from database
        result = await db_session.execute(
            select(LeadSignal).where(LeadSignal.lead_id == lead.id)
        )
        lead_signals = result.scalars().all()

        # Map signal types from lead_signals table
        for signal in lead_signals:
            signal_key = SIGNAL_TYPE_MAPPING.get(signal.signal_type)
            if signal_key:
                detected_signals.add(signal_key)

        # Add boolean flags from Lead model
        if lead.is_multinational:
            detected_signals.add("is_multinational")

        if lead.is_exporter:
            detected_signals.add("is_exporter")

        if lead.under_audit:
            detected_signals.add("under_audit")

        return detected_signals

    def calculate_lead_score(
        self,
        lead: Lead,
        service: Service,
        detected_signals: Set[str]
    ) -> Tuple[float, str, Dict]:
        """
        Calculate weighted score for a lead-service pair.

        Args:
            lead: The lead to score
            service: The ABBK service to score for
            detected_signals: Set of signal keys detected for this lead

        Returns:
            Tuple of (score, reasoning, signal_breakdown)
        """
        if not service.scoring_weights:
            # Service has no weights - return 0
            return 0.0, "No scoring weights configured for this service", {}

        # Calculate actual score: sum of weights for fired signals
        actual_score = 0.0
        signal_breakdown = {}
        fired_signals = []

        for signal_type, weight in service.scoring_weights.items():
            if signal_type in detected_signals:
                actual_score += weight
                signal_breakdown[signal_type] = weight
                fired_signals.append((signal_type, weight))

        # Calculate max possible score for this service
        max_possible_score = sum(service.scoring_weights.values())

        # Normalize to 0-100 scale
        if max_possible_score > 0:
            normalized_score = (actual_score / max_possible_score) * 100
        else:
            normalized_score = 0.0

        # Generate detailed reasoning
        reasoning = self._generate_reasoning(
            lead=lead,
            service=service,
            normalized_score=normalized_score,
            fired_signals=fired_signals,
            detected_signals=detected_signals
        )

        return normalized_score, reasoning, signal_breakdown

    def _generate_reasoning(
        self,
        lead: Lead,
        service: Service,
        normalized_score: float,
        fired_signals: List[Tuple[str, float]],
        detected_signals: Set[str]
    ) -> str:
        """
        Generate human-readable reasoning for the score.

        HOT LEAD CRITERIA (from business manager):
        Priority order for hot leads:
        1. Training history or training potential (HIGHEST)
        2. Bought new machine needing licenses/training
        3. Hiring engineers who need licenses
        4. Multinational with audit requirements

        Also valuable:
        - Companies posting training history
        - Companies lacking training (website analysis)
        - New projects posted
        - Companies hiring any mechanical/electrical engineers
        """
        # HOT LEAD SCORING - BUSINESS MANAGER PRIORITY ORDER
        hot_lead_factors = []
        hot_lead_score = 0

        # 1. TRAINING (HIGHEST PRIORITY)
        if "training_detected" in detected_signals:
            hot_lead_factors.append("Has training history or potential (TOP PRIORITY)")
            hot_lead_score += 40

        # 2. NEW MACHINE PURCHASE
        if "news" in detected_signals or "tender_detected" in detected_signals:
            hot_lead_factors.append("Bought new machine or equipment (needs licenses/training)")
            hot_lead_score += 30

        # 3. HIRING ENGINEERS
        if "new_hire" in detected_signals or "role_detected" in detected_signals:
            hot_lead_factors.append("Hiring engineers NOW (mechanical/electrical/CAD)")
            hot_lead_score += 20

        # 4. MULTINATIONAL + AUDIT
        if "is_multinational" in detected_signals and "under_audit" in detected_signals:
            hot_lead_factors.append("Multinational under audit (product exported = must have licenses)")
            hot_lead_score += 10
        elif "is_multinational" in detected_signals:
            hot_lead_factors.append("Multinational company (export products = audit requirement)")
            hot_lead_score += 5
        elif "under_audit" in detected_signals:
            hot_lead_factors.append("Under audit (compliance deadline)")
            hot_lead_score += 8

        # Adjust normalized score based on hot lead criteria
        if hot_lead_score > 0:
            # Boost score if hot lead criteria are met
            normalized_score = min(100, normalized_score + hot_lead_score)

        # Priority classification based on hot lead criteria
        if normalized_score >= 70 or (hot_lead_score >= 40):  # Training or 2+ factors
            priority = "HOT LEAD"
            action = "CALL TODAY - High conversion probability"
        elif normalized_score >= 50 or (hot_lead_score >= 20):
            priority = "WARM LEAD"
            action = "Schedule call this week"
        elif normalized_score >= 30:
            priority = "POTENTIAL"
            action = "Add to pipeline for follow-up"
        else:
            priority = "RESEARCH NEEDED"
            action = "Gather more data before contact"

        reasoning_parts = [
            f"{priority} - Score: {normalized_score:.0f}/100 for {service.name}.",
        ]

        # Explain hot lead factors first (most important)
        if hot_lead_factors:
            reasoning_parts.append("Hot Lead Signals: " + "; ".join(hot_lead_factors) + ".")

        # Explain other fired signals
        if fired_signals:
            # Sort by weight descending
            fired_signals.sort(key=lambda x: x[1], reverse=True)

            signal_explanations = []
            for signal_type, weight in fired_signals[:5]:  # Top 5 signals
                # Skip if already mentioned in hot_lead_factors
                if signal_type not in ["training_detected", "new_hire", "role_detected", "is_multinational", "under_audit", "news", "tender_detected"]:
                    explanation = self._explain_signal(signal_type, weight, lead)
                    signal_explanations.append(explanation)

            if signal_explanations:
                reasoning_parts.append("Additional signals: " + "; ".join(signal_explanations) + ".")

        # Add recommended action
        reasoning_parts.append(f"Next Action: {action}.")

        return " ".join(reasoning_parts)

    def _explain_signal(self, signal_type: str, weight: float, lead: Lead) -> str:
        """
        Generate human-readable explanation for a signal.

        Business manager priorities:
        - Training history/potential = HIGHEST
        - New machine purchase = HIGH
        - Hiring engineers = HIGH
        - Multinational + audit = MEDIUM
        """
        explanations = {
            # TOP PRIORITY SIGNALS
            "training_detected": f"Training history or potential (TOP PRIORITY) (+{weight:.0f})",

            # HIGH PRIORITY SIGNALS
            "tender_detected": f"New machine/equipment purchase via tender (+{weight:.0f})",
            "news": f"New project or machine purchase announced (+{weight:.0f})",
            "new_hire": f"Hiring mechanical/electrical/CAD engineers (+{weight:.0f})",
            "role_detected": f"Engineering roles detected on website (+{weight:.0f})",

            # MEDIUM PRIORITY SIGNALS
            "is_multinational": f"Multinational (products exported = audit requirement) (+{weight:.0f})",
            "under_audit": f"Under audit/certification (cannot use unlicensed) (+{weight:.0f})",
            "is_exporter": f"Exports products internationally (+{weight:.0f})",

            # SUPPORTING SIGNALS
            "logo_detected": f"SOLIDWORKS/CAD software detected on website (+{weight:.0f})",
            "funding": f"International funding received (audit requirement) (+{weight:.0f})",
            "event_attendance": f"Attended engineering event (+{weight:.0f})",
            "cracked_risk": f"Potential unlicensed user (needs training approach) (+{weight:.0f})",
        }

        return explanations.get(
            signal_type,
            f"{signal_type} (+{weight:.0f})"
        )


async def score_lead(
    lead: Lead,
    services: List[Service],
    db_session: AsyncSession
) -> List[LeadScore]:
    """
    Score a single lead against all ABBK services using advanced weighted scoring.

    Args:
        lead: Lead to score
        services: List of ABBK services
        db_session: Database session

    Returns:
        List of LeadScore objects created
    """
    engine = AdvancedScoringEngine()

    # Detect all signals for this lead once (reuse for all services)
    detected_signals = await engine.detect_lead_signals(lead, db_session)

    logger.info(
        f"Detected {len(detected_signals)} signals for {lead.company_name}: "
        f"{', '.join(sorted(detected_signals))}"
    )

    scores_created = []

    for service in services:
        if not service.is_active:
            continue

        # Calculate weighted score
        score_value, reasoning, signal_breakdown = engine.calculate_lead_score(
            lead=lead,
            service=service,
            detected_signals=detected_signals
        )

        # Get old score before deleting (for notification comparison)
        from sqlalchemy import delete
        old_score_result = await db_session.execute(
            select(LeadScore).where(
                LeadScore.lead_id == lead.id,
                LeadScore.service_type == service.service_type,
                LeadScore.service_name == service.name
            )
        )
        old_score_record = old_score_result.scalar_one_or_none()
        old_score = old_score_record.score if old_score_record else 0.0

        # Delete old scores for this lead+service to avoid duplicates
        await db_session.execute(
            delete(LeadScore).where(
                LeadScore.lead_id == lead.id,
                LeadScore.service_type == service.service_type,
                LeadScore.service_name == service.name
            )
        )

        # Create new score record
        lead_score = LeadScore(
            lead_id=lead.id,
            service_type=service.service_type,
            service_name=service.name,
            score=score_value,
            reasoning=reasoning,
            signal_breakdown=signal_breakdown,
            scored_at=datetime.utcnow()
        )

        db_session.add(lead_score)
        scores_created.append(lead_score)

        logger.info(
            f"Scored {lead.company_name} for {service.name}: "
            f"{score_value:.1f}/100 ({len(signal_breakdown)} signals fired)"
        )

        # Record score history if score changed significantly (> 5 points)
        score_change = score_value - old_score
        if abs(score_change) >= 5:
            try:
                from app.models.models import ScoreHistory

                history = ScoreHistory(
                    lead_id=lead.id,
                    service_type=service.service_type,
                    service_name=service.name,
                    old_score=old_score,
                    new_score=score_value,
                    change=score_change,
                    reason=f"{len(detected_signals)} signals detected" if score_change > 0 else "Signal removed or weight adjusted"
                )
                db_session.add(history)
                logger.debug(f"Recorded score history: {lead.company_name} {score_change:+.1f}")
            except Exception as e:
                logger.warning(f"Failed to record score history: {e}")

        # Check for notification triggers (hot lead or score spike)
        # HOT LEAD = training history/potential OR 70+ score OR multiple priority signals
        try:
            from app.services.notification_service import (
                create_hot_lead_notification,
                create_score_spike_notification
            )

            # Hot lead criteria from business manager:
            # 1. Has training signal (HIGHEST priority)
            # 2. Score 70+ (multiple signals)
            # 3. Score spike of 30+ points
            is_hot_lead = (
                "training_detected" in detected_signals or
                score_value >= 70 or
                (score_value >= 60 and ("new_hire" in detected_signals or "tender_detected" in detected_signals))
            )

            if is_hot_lead and old_score < 70:
                await create_hot_lead_notification(
                    db_session, lead.id, score_value, old_score, service.name
                )
                logger.info(f"🔥 Created hot lead notification for {lead.company_name}")

            # Score spike: increased by 30+ points
            elif score_value - old_score >= 30:
                await create_score_spike_notification(
                    db_session, lead.id, score_value, old_score, service.name
                )
                logger.info(f"📈 Created score spike notification for {lead.company_name}")

        except Exception as e:
            logger.warning(f"Failed to create notification: {e}")

    return scores_created


async def score_all_leads(db_session: AsyncSession) -> Dict[str, int]:
    """
    Score all leads in the database against all active services.

    Uses the advanced weighted signal scoring engine.

    Returns:
        Dictionary with counts of leads and scores created
    """
    from sqlalchemy import select, delete

    # Get all active services
    services_result = await db_session.execute(
        select(Service).where(Service.is_active == True)
    )
    services = services_result.scalars().all()

    if not services:
        logger.warning("No active services found - cannot score leads")
        return {"leads_scored": 0, "scores_created": 0, "services": 0}

    # Get all leads
    leads_result = await db_session.execute(select(Lead))
    leads = leads_result.scalars().all()

    logger.info(
        f"Starting advanced weighted scoring: {len(leads)} leads × {len(services)} services"
    )

    # Clear all existing scores (fresh recalculation)
    await db_session.execute(delete(LeadScore))
    await db_session.flush()

    total_scores = 0
    leads_with_signals = 0

    for idx, lead in enumerate(leads, 1):
        scores = await score_lead(lead, services, db_session)
        total_scores += len(scores)

        # Count leads with at least one non-zero score
        if any(score.score > 0 for score in scores):
            leads_with_signals += 1

        if idx % 10 == 0:
            logger.info(f"Progress: {idx}/{len(leads)} leads scored")

    await db_session.commit()

    logger.info(
        f"✅ Advanced scoring complete: {len(leads)} leads × {len(services)} services = "
        f"{total_scores} scores created. {leads_with_signals} leads have signals."
    )

    return {
        "leads_scored": len(leads),
        "scores_created": total_scores,
        "services": len(services),
        "leads_with_signals": leads_with_signals
    }

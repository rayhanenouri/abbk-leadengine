"""
Lead scoring engine for ABBK LeadEngine.

Rule-based scoring system that assigns 0-100 scores to each lead
based on their fit for ABBK products and services.

Scoring signals:
- Sector match (engineering, manufacturing, industrial)
- City (Tunis and major cities score higher)
- Has website (company is established)
- Has phone (can be contacted)
- Company size indicators from name/description
"""
from typing import Dict, List, Tuple
from datetime import datetime
import logging

from app.models.models import Lead, LeadScore, Service, ServiceType

logger = logging.getLogger(__name__)


# High-value sectors for SOLIDWORKS and engineering software
HIGH_VALUE_SECTORS = {
    'engineering': 40,
    'bureau d etudes': 40,
    'ingenieur': 35,
    'manufacturing': 35,
    'fabrication': 35,
    'industrial': 35,
    'industrie': 35,
    'construction': 30,
    'btp': 30,
    'automotive': 35,
    'automobile': 35,
    'mechanical': 35,
    'mecanique': 35,
    'steel': 30,
    'metal': 30,
    'cement': 25,
    'ciment': 25,
    'aluminum': 30,
    'aluminium': 30,
    'electronics': 30,
    'electronique': 30,
    'electrical': 28,
    'electrique': 28,
    'oil': 25,
    'petrole': 25,
    'chemical': 25,
    'chimique': 25,
}

# Medium-value sectors
MEDIUM_VALUE_SECTORS = {
    'energy': 20,
    'utilities': 20,
    'telecom': 15,
    'aviation': 20,
    'infrastructure': 20,
    'water': 15,
    'sanitation': 15,
}

# Major cities with more engineering companies
MAJOR_CITIES = {
    'tunis': 10,
    'sfax': 8,
    'sousse': 7,
    'ariana': 8,
    'ben arous': 8,
    'manouba': 7,
    'bizerte': 6,
    'gabes': 6,
    'nabeul': 6,
}


class ScoringEngine:
    """
    Main scoring engine that calculates lead scores for all ABBK services.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def calculate_lead_score(
        self,
        lead: Lead,
        service: Service
    ) -> Tuple[float, str, Dict]:
        """
        Calculate score for a lead-service pair.

        Args:
            lead: The lead to score
            service: The ABBK service to score for

        Returns:
            Tuple of (score, reasoning, signal_breakdown)
        """
        score = 0.0
        signals = {}
        reasoning_parts = []

        # Base score from sector match
        sector_score = self._score_sector(lead.sector)
        if sector_score > 0:
            score += sector_score
            signals['sector_match'] = sector_score
            reasoning_parts.append(f"Sector '{lead.sector}' highly relevant (+{sector_score})")

        # City/location bonus
        city_score = self._score_city(lead.city)
        if city_score > 0:
            score += city_score
            signals['major_city'] = city_score
            reasoning_parts.append(f"Located in {lead.city} (+{city_score})")

        # Has website = established company
        if lead.website:
            score += 10
            signals['has_website'] = 10
            reasoning_parts.append("Has website - established company (+10)")

        # Has phone = contactable
        phone = self._extract_phone(lead)
        if phone:
            score += 5
            signals['has_phone'] = 5
            reasoning_parts.append("Phone available (+5)")

        # Company size indicators from name
        if self._is_large_company(lead.company_name):
            score += 15
            signals['large_company'] = 15
            reasoning_parts.append("Large/national company (+15)")

        # Service-specific scoring
        service_bonus = self._score_for_service(lead, service)
        if service_bonus > 0:
            score += service_bonus
            signals[f'{service.service_type}_fit'] = service_bonus
            reasoning_parts.append(f"Good fit for {service.name} (+{service_bonus})")

        # Cap at 100
        score = min(score, 100.0)

        # Generate reasoning text
        if score >= 70:
            priority = "HIGH PRIORITY"
        elif score >= 50:
            priority = "MEDIUM PRIORITY"
        elif score >= 30:
            priority = "LOW PRIORITY"
        else:
            priority = "RESEARCH NEEDED"

        reasoning = f"{priority} - Score: {score:.0f}/100. " + ". ".join(reasoning_parts)

        return score, reasoning, signals

    def _score_sector(self, sector: str) -> float:
        """Score based on sector match."""
        if not sector:
            return 0.0

        sector_lower = sector.lower()

        # Check high-value sectors
        for keyword, points in HIGH_VALUE_SECTORS.items():
            if keyword in sector_lower:
                return float(points)

        # Check medium-value sectors
        for keyword, points in MEDIUM_VALUE_SECTORS.items():
            if keyword in sector_lower:
                return float(points)

        return 0.0

    def _score_city(self, city: str) -> float:
        """Score based on city (major cities have more opportunities)."""
        if not city:
            return 0.0

        city_lower = city.lower()
        for major_city, points in MAJOR_CITIES.items():
            if major_city in city_lower:
                return float(points)

        return 0.0

    def _extract_phone(self, lead: Lead) -> str:
        """Extract phone from scraped_data."""
        if not lead.scraped_data:
            return None

        # Check all sources in scraped_data
        for source_data in lead.scraped_data.values():
            if isinstance(source_data, dict) and source_data.get('phone'):
                return source_data['phone']

        return None

    def _is_large_company(self, company_name: str) -> bool:
        """Detect if company is likely large/national."""
        if not company_name:
            return False

        name_lower = company_name.lower()

        # National/international company indicators
        indicators = [
            'groupe', 'group', 'holding',
            'societe nationale', 'national',
            'international', 'multinational',
            'office', 'steg', 'tunisie telecom',
            'banque', 'bank', 'assurance',
        ]

        return any(indicator in name_lower for indicator in indicators)

    def _score_for_service(self, lead: Lead, service: Service) -> float:
        """Additional scoring based on specific service type."""
        score = 0.0

        if service.service_type == ServiceType.solidworks_license:
            # SOLIDWORKS is for design, engineering, manufacturing
            if lead.sector and any(kw in lead.sector.lower() for kw in
                ['engineering', 'design', 'manufacturing', 'mechanical', 'bureau']):
                score += 10

        elif service.service_type == ServiceType.training:
            # Training fits education and companies with engineers
            if lead.sector and any(kw in lead.sector.lower() for kw in
                ['education', 'universite', 'engineering', 'industrial']):
                score += 10

        elif service.service_type == ServiceType.other_license:
            # Simulia, Abaqus for advanced simulation
            if lead.sector and any(kw in lead.sector.lower() for kw in
                ['automotive', 'aerospace', 'mechanical', 'civil']):
                score += 10

        return score


async def score_lead(lead: Lead, services: List[Service], db_session) -> List[LeadScore]:
    """
    Score a single lead against all ABBK services.

    Args:
        lead: Lead to score
        services: List of ABBK services
        db_session: Database session

    Returns:
        List of LeadScore objects created
    """
    engine = ScoringEngine()
    scores_created = []

    for service in services:
        if not service.is_active:
            continue

        # Calculate score
        score_value, reasoning, signal_breakdown = engine.calculate_lead_score(lead, service)

        # Create score record
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

        logger.info(f"Scored {lead.company_name} for {service.name}: {score_value:.1f}/100")

    return scores_created


async def score_all_leads(db_session) -> Dict[str, int]:
    """
    Score all leads in the database against all active services.

    Returns:
        Dictionary with counts of leads and scores created
    """
    from sqlalchemy import select

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

    total_scores = 0
    for lead in leads:
        scores = await score_lead(lead, services, db_session)
        total_scores += len(scores)

    await db_session.commit()

    logger.info(f"Scored {len(leads)} leads against {len(services)} services, created {total_scores} scores")

    return {
        "leads_scored": len(leads),
        "scores_created": total_scores,
        "services": len(services)
    }

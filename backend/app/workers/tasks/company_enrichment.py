"""
Company enrichment tasks.

Enriches existing leads with additional company data:
- Nombre d'employés (employee count)
- Nouveaux employés récents (recent hires)
- Actualité récente (recent news)
- Registre de commerce (commercial registry number)
- Secteur fiscal (tax sector classification)

Data sources:
- Public company registries
- LinkedIn (via Apify if available)
- News mentions (already scraped)
- Government open data portals
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import re

from sqlalchemy import select, update as sql_update
from sqlalchemy.ext.asyncio import AsyncSession

from app.workers.celery_app import celery_app
from app.db.session import AsyncSessionLocal
from app.models.models import Lead, LeadSignal

logger = logging.getLogger(__name__)


async def enrich_single_lead(db: AsyncSession, lead: Lead) -> Dict[str, Any]:
    """
    Enrich a single lead with additional company data.

    Args:
        db: Database session
        lead: Lead to enrich

    Returns:
        Dictionary with enrichment results
    """
    enrichment_data = {}
    changes_made = False

    try:
        # 1. Employee count from LinkedIn data (if available)
        if lead.scraped_data and 'linkedin' in lead.scraped_data:
            linkedin_data = lead.scraped_data['linkedin']
            if 'employee_count' in linkedin_data:
                enrichment_data['employee_count'] = linkedin_data['employee_count']

                # Update lead.employee_count if not set
                if not lead.employee_count:
                    lead.employee_count = linkedin_data['employee_count']
                    changes_made = True

        # 2. Recent hires from job signals
        recent_hires = await _count_recent_hires(db, lead)
        if recent_hires > 0:
            enrichment_data['recent_hires_count'] = recent_hires
            enrichment_data['recent_hires_period'] = '90_days'
            changes_made = True

        # 3. Recent news/actualité from news signals
        recent_news = await _get_recent_news(db, lead)
        if recent_news:
            enrichment_data['recent_news'] = recent_news
            changes_made = True

        # 4. Fiscal sector from existing data
        if lead.sector:
            enrichment_data['fiscal_sector'] = _map_to_fiscal_sector(lead.sector)
            changes_made = True

        # 5. Extract registre de commerce from scraped data if available
        registre = _extract_registre_commerce(lead)
        if registre:
            enrichment_data['registre_commerce'] = registre
            changes_made = True

        # 6. Company age/founding year estimation
        founding_info = _estimate_company_age(lead)
        if founding_info:
            enrichment_data.update(founding_info)
            changes_made = True

        # 7. Growth indicators
        growth_signals = _detect_growth_signals(lead, recent_hires)
        if growth_signals:
            enrichment_data['growth_indicators'] = growth_signals
            changes_made = True

        # 8. Risk/compliance flags
        compliance_flags = _detect_compliance_flags(lead)
        if compliance_flags:
            enrichment_data['compliance_flags'] = compliance_flags
            changes_made = True

        # Update lead's scraped_data with enrichment
        if changes_made:
            if not lead.scraped_data:
                lead.scraped_data = {}

            lead.scraped_data['enrichment'] = {
                'data': enrichment_data,
                'enriched_at': datetime.utcnow().isoformat(),
                'version': '1.0'
            }

            await db.execute(
                sql_update(Lead)
                .where(Lead.id == lead.id)
                .values(
                    scraped_data=lead.scraped_data,
                    employee_count=lead.employee_count,
                    updated_at=datetime.utcnow()
                )
            )
            await db.commit()

            logger.info(
                f"✅ Enriched {lead.company_name}: {len(enrichment_data)} fields added"
            )

        return {
            'success': True,
            'lead_id': lead.id,
            'company_name': lead.company_name,
            'fields_added': len(enrichment_data),
            'changes_made': changes_made
        }

    except Exception as e:
        logger.error(f"Error enriching lead {lead.id}: {e}")
        await db.rollback()
        return {
            'success': False,
            'lead_id': lead.id,
            'error': str(e)
        }


async def _count_recent_hires(db: AsyncSession, lead: Lead) -> int:
    """Count hiring signals in last 90 days."""
    ninety_days_ago = datetime.utcnow() - timedelta(days=90)

    result = await db.execute(
        select(LeadSignal)
        .where(
            LeadSignal.lead_id == lead.id,
            LeadSignal.signal_type == 'new_hire',
            LeadSignal.detected_at >= ninety_days_ago
        )
    )
    signals = result.scalars().all()
    return len(signals)


async def _get_recent_news(db: AsyncSession, lead: Lead) -> Optional[list]:
    """Get recent news signals (last 6 months)."""
    six_months_ago = datetime.utcnow() - timedelta(days=180)

    result = await db.execute(
        select(LeadSignal)
        .where(
            LeadSignal.lead_id == lead.id,
            LeadSignal.signal_type == 'news',
            LeadSignal.detected_at >= six_months_ago
        )
        .order_by(LeadSignal.detected_at.desc())
        .limit(5)
    )
    signals = result.scalars().all()

    if not signals:
        return None

    return [
        {
            'title': signal.title,
            'date': signal.detected_at.isoformat(),
            'source_url': signal.source_url
        }
        for signal in signals
    ]


def _map_to_fiscal_sector(sector: str) -> str:
    """Map company sector to Tunisian fiscal sector classification."""
    sector_lower = sector.lower()

    # Tunisian fiscal sectors (simplified mapping)
    if any(kw in sector_lower for kw in ['industrie', 'manufacturing', 'production', 'usine']):
        return "Industrie manufacturière"
    elif any(kw in sector_lower for kw in ['construction', 'btp', 'génie civil', 'bâtiment']):
        return "Construction et BTP"
    elif any(kw in sector_lower for kw in ['service', 'conseil', 'consulting', 'bureau']):
        return "Services aux entreprises"
    elif any(kw in sector_lower for kw in ['commerce', 'distribution', 'vente']):
        return "Commerce"
    elif any(kw in sector_lower for kw in ['technologie', 'informatique', 'software', 'it']):
        return "Technologies de l'information"
    elif any(kw in sector_lower for kw in ['energie', 'energy', 'électrique']):
        return "Énergie et électricité"
    elif any(kw in sector_lower for kw in ['agriculture', 'agroalimentaire', 'food']):
        return "Agriculture et agroalimentaire"
    elif any(kw in sector_lower for kw in ['textile', 'habillement', 'clothing']):
        return "Textile et habillement"
    elif any(kw in sector_lower for kw in ['chimique', 'pharmaceutique', 'chemical']):
        return "Chimie et pharmacie"
    elif any(kw in sector_lower for kw in ['transport', 'logistique', 'logistics']):
        return "Transport et logistique"
    else:
        return sector  # Return original if no match


def _extract_registre_commerce(lead: Lead) -> Optional[str]:
    """Extract registre de commerce number from scraped data if available."""
    if not lead.scraped_data:
        return None

    # Check various sources in scraped_data
    for source_key in lead.scraped_data:
        if isinstance(lead.scraped_data[source_key], dict):
            source_data = lead.scraped_data[source_key]

            # Look for RC number in various fields
            for key in ['registre_commerce', 'rc', 'registry', 'commercial_registry']:
                if key in source_data:
                    return str(source_data[key])

            # Try to extract from description or other text fields
            for key in ['description', 'detail', 'about']:
                if key in source_data and isinstance(source_data[key], str):
                    # Pattern: RC followed by numbers
                    match = re.search(r'R\.?C\.?\s*:?\s*([A-Z]?\d+[/-]?\d*)', source_data[key], re.IGNORECASE)
                    if match:
                        return match.group(1)

    return None


def _estimate_company_age(lead: Lead) -> Optional[Dict[str, Any]]:
    """Estimate company age from various signals."""
    founding_year = None

    # Check LinkedIn data
    if lead.scraped_data and 'linkedin' in lead.scraped_data:
        linkedin = lead.scraped_data['linkedin']
        if 'founded' in linkedin:
            founding_year = linkedin['founded']

    if founding_year:
        current_year = datetime.now().year
        age = current_year - founding_year

        return {
            'founding_year': founding_year,
            'company_age_years': age,
            'maturity': 'established' if age > 10 else 'growing' if age > 3 else 'startup'
        }

    return None


def _detect_growth_signals(lead: Lead, recent_hires: int) -> Optional[Dict[str, bool]]:
    """Detect company growth indicators."""
    signals = {}

    # Hiring = growth
    if recent_hires > 0:
        signals['hiring'] = True
        signals['hiring_rate'] = 'high' if recent_hires >= 5 else 'moderate' if recent_hires >= 2 else 'low'

    # Funding = growth
    if lead.scraped_data:
        for source in lead.scraped_data.values():
            if isinstance(source, dict) and 'funding' in str(source).lower():
                signals['recently_funded'] = True
                break

    # Export/multinational = expansion
    if lead.is_exporter or lead.is_multinational:
        signals['expanding_internationally'] = True

    return signals if signals else None


def _detect_compliance_flags(lead: Lead) -> Optional[Dict[str, bool]]:
    """Detect compliance/risk indicators."""
    flags = {}

    # Under audit = high compliance need
    if lead.under_audit:
        flags['under_audit'] = True
        flags['compliance_priority'] = 'high'

    # Multinational = compliance standards
    if lead.is_multinational:
        flags['international_compliance_required'] = True

    # Exporter = export regulations
    if lead.is_exporter:
        flags['export_compliance_required'] = True

    return flags if flags else None


@celery_app.task(name="company_enrichment.enrich_all_leads")
def enrich_all_leads_task() -> Dict[str, Any]:
    """
    Celery task to enrich all leads with company data.

    Runs through all leads and adds:
    - Employee count
    - Recent hires
    - Recent news
    - Fiscal sector
    - Registre de commerce
    - Company age
    - Growth indicators
    - Compliance flags

    Returns:
        Dictionary with enrichment statistics
    """
    import asyncio

    async def _enrich():
        async with AsyncSessionLocal() as db:
            # Get all leads
            result = await db.execute(select(Lead))
            leads = result.scalars().all()

            logger.info(f"Starting enrichment for {len(leads)} leads")

            enriched_count = 0
            failed_count = 0
            skipped_count = 0

            for lead in leads:
                # Check if already enriched recently (last 7 days)
                if lead.scraped_data and 'enrichment' in lead.scraped_data:
                    enriched_at = lead.scraped_data['enrichment'].get('enriched_at')
                    if enriched_at:
                        enriched_date = datetime.fromisoformat(enriched_at)
                        days_old = (datetime.utcnow() - enriched_date).days
                        if days_old < 7:
                            logger.debug(f"Lead {lead.id} enriched {days_old} days ago - skipping")
                            skipped_count += 1
                            continue

                # Enrich the lead
                result = await enrich_single_lead(db, lead)

                if result['success']:
                    if result['changes_made']:
                        enriched_count += 1
                    else:
                        skipped_count += 1
                else:
                    failed_count += 1

            return {
                'total_leads': len(leads),
                'enriched': enriched_count,
                'failed': failed_count,
                'skipped': skipped_count,
                'timestamp': datetime.utcnow().isoformat()
            }

    loop = asyncio.get_event_loop()
    if loop.is_running():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(_enrich())


@celery_app.task(name="company_enrichment.enrich_lead")
def enrich_lead_task(lead_id: int) -> Dict[str, Any]:
    """
    Celery task to enrich a single lead.

    Args:
        lead_id: ID of lead to enrich

    Returns:
        Dictionary with enrichment result
    """
    import asyncio

    async def _enrich():
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Lead).where(Lead.id == lead_id))
            lead = result.scalar_one_or_none()

            if not lead:
                return {"success": False, "error": f"Lead {lead_id} not found"}

            return await enrich_single_lead(db, lead)

    loop = asyncio.get_event_loop()
    if loop.is_running():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(_enrich())

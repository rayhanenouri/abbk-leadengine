"""
Analytics routes for ABBK LeadEngine.
Provides aggregated statistics and metrics for sales intelligence dashboard.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_, cast, Float, case
from datetime import datetime, timedelta
from typing import Dict, List, Any

from app.db.session import get_db
from app.models.models import Lead, LeadScore, LeadSignal, Service
from app.api.routes.auth import get_current_user

router = APIRouter()


@router.get("/analytics/overview")
async def get_analytics_overview(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get comprehensive analytics overview for sales intelligence dashboard.

    Returns:
    - Total leads count
    - Leads by sector (top 20 sectors with counts)
    - Top 10 sectors by average score
    - Geographic distribution (Tunisia cities + countries)
    - Leads by status (sales funnel)
    - Score distribution (histogram buckets)
    - Recent signals (last 7 days)
    - New companies (last 7 days)
    - Conversion metrics
    """

    # Total leads count
    total_leads_result = await db.execute(select(func.count(Lead.id)))
    total_leads = total_leads_result.scalar() or 0

    # Leads by sector (top 20)
    sector_query = select(
        Lead.sector,
        func.count(Lead.id).label('count')
    ).where(
        Lead.sector.isnot(None)
    ).group_by(
        Lead.sector
    ).order_by(
        desc('count')
    ).limit(20)

    sector_result = await db.execute(sector_query)
    leads_by_sector = [
        {"sector": row.sector, "count": row.count}
        for row in sector_result.all()
    ]

    # Top 10 sectors by average score
    # Get best score per lead first, then average by sector
    subquery = select(
        Lead.id,
        Lead.sector,
        func.max(LeadScore.score).label('best_score')
    ).join(
        LeadScore, Lead.id == LeadScore.lead_id
    ).where(
        Lead.sector.isnot(None)
    ).group_by(
        Lead.id, Lead.sector
    ).subquery()

    avg_score_query = select(
        subquery.c.sector,
        func.avg(subquery.c.best_score).label('avg_score'),
        func.count(subquery.c.id).label('lead_count')
    ).group_by(
        subquery.c.sector
    ).order_by(
        desc('avg_score')
    ).limit(10)

    avg_score_result = await db.execute(avg_score_query)
    top_sectors_by_score = [
        {
            "sector": row.sector,
            "avg_score": round(float(row.avg_score), 1),
            "lead_count": row.lead_count
        }
        for row in avg_score_result.all()
    ]

    # Geographic distribution - Cities in Tunisia
    city_query = select(
        Lead.city,
        func.count(Lead.id).label('count')
    ).where(
        and_(
            Lead.city.isnot(None),
            Lead.country == 'Tunisia'
        )
    ).group_by(
        Lead.city
    ).order_by(
        desc('count')
    ).limit(15)

    city_result = await db.execute(city_query)
    leads_by_city = [
        {"city": row.city, "count": row.count}
        for row in city_result.all()
    ]

    # Geographic distribution - Countries
    country_query = select(
        Lead.country,
        func.count(Lead.id).label('count')
    ).where(
        Lead.country.isnot(None)
    ).group_by(
        Lead.country
    ).order_by(
        desc('count')
    )

    country_result = await db.execute(country_query)
    leads_by_country = [
        {"country": row.country, "count": row.count}
        for row in country_result.all()
    ]

    # Leads by status (sales funnel)
    status_query = select(
        Lead.status,
        func.count(Lead.id).label('count')
    ).group_by(
        Lead.status
    ).order_by(
        # Custom order for funnel visualization
        case(
            (Lead.status == 'new', 1),
            (Lead.status == 'qualified', 2),
            (Lead.status == 'contacted', 3),
            (Lead.status == 'converted', 4),
            (Lead.status == 'lost', 5),
            else_=6
        )
    )

    status_result = await db.execute(status_query)
    leads_by_status = [
        {"status": row.status or 'new', "count": row.count}
        for row in status_result.all()
    ]

    # Score distribution (histogram with 10-point buckets)
    # Get best score per lead
    best_scores_subquery = select(
        Lead.id,
        func.max(LeadScore.score).label('best_score')
    ).join(
        LeadScore, Lead.id == LeadScore.lead_id
    ).group_by(
        Lead.id
    ).subquery()

    score_buckets = [
        {"range": "0-10", "min": 0, "max": 10},
        {"range": "10-20", "min": 10, "max": 20},
        {"range": "20-30", "min": 20, "max": 30},
        {"range": "30-40", "min": 30, "max": 40},
        {"range": "40-50", "min": 40, "max": 50},
        {"range": "50-60", "min": 50, "max": 60},
        {"range": "60-70", "min": 60, "max": 70},
        {"range": "70-80", "min": 70, "max": 80},
        {"range": "80-90", "min": 80, "max": 90},
        {"range": "90-100", "min": 90, "max": 100},
    ]

    score_distribution = []
    for bucket in score_buckets:
        count_query = select(
            func.count(best_scores_subquery.c.id)
        ).where(
            and_(
                best_scores_subquery.c.best_score >= bucket["min"],
                best_scores_subquery.c.best_score < bucket["max"]
            )
        )
        count_result = await db.execute(count_query)
        count = count_result.scalar() or 0
        score_distribution.append({
            "range": bucket["range"],
            "count": count
        })

    # Handle 100 score edge case (include in 90-100 bucket)
    hundred_query = select(
        func.count(best_scores_subquery.c.id)
    ).where(
        best_scores_subquery.c.best_score == 100
    )
    hundred_result = await db.execute(hundred_query)
    hundred_count = hundred_result.scalar() or 0
    if hundred_count > 0:
        score_distribution[-1]["count"] += hundred_count

    # Recent signals (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)

    recent_signals_query = select(
        LeadSignal.signal_type,
        func.count(LeadSignal.id).label('count')
    ).where(
        LeadSignal.detected_at >= seven_days_ago
    ).group_by(
        LeadSignal.signal_type
    ).order_by(
        desc('count')
    )

    recent_signals_result = await db.execute(recent_signals_query)
    recent_signals = [
        {"signal_type": row.signal_type, "count": row.count}
        for row in recent_signals_result.all()
    ]

    # Total signals count (last 7 days)
    total_signals_query = select(
        func.count(LeadSignal.id)
    ).where(
        LeadSignal.detected_at >= seven_days_ago
    )
    total_signals_result = await db.execute(total_signals_query)
    total_recent_signals = total_signals_result.scalar() or 0

    # New companies (last 7 days)
    new_companies_query = select(
        func.count(Lead.id)
    ).where(
        Lead.created_at >= seven_days_ago
    )
    new_companies_result = await db.execute(new_companies_query)
    new_companies_count = new_companies_result.scalar() or 0

    # Conversion metrics
    converted_query = select(
        func.count(Lead.id)
    ).where(
        Lead.status == 'converted'
    )
    converted_result = await db.execute(converted_query)
    converted_count = converted_result.scalar() or 0

    contacted_query = select(
        func.count(Lead.id)
    ).where(
        Lead.status.in_(['contacted', 'converted', 'lost'])
    )
    contacted_result = await db.execute(contacted_query)
    contacted_count = contacted_result.scalar() or 0

    # Calculate conversion rate (converted / contacted)
    conversion_rate = 0.0
    if contacted_count > 0:
        conversion_rate = round((converted_count / contacted_count) * 100, 1)

    # High-value leads metrics
    multinational_query = select(
        func.count(Lead.id)
    ).where(
        Lead.is_multinational == True
    )
    multinational_result = await db.execute(multinational_query)
    multinational_count = multinational_result.scalar() or 0

    exporter_query = select(
        func.count(Lead.id)
    ).where(
        Lead.is_exporter == True
    )
    exporter_result = await db.execute(exporter_query)
    exporter_count = exporter_result.scalar() or 0

    audit_query = select(
        func.count(Lead.id)
    ).where(
        Lead.under_audit == True
    )
    audit_result = await db.execute(audit_query)
    audit_count = audit_result.scalar() or 0

    # High priority leads (score >= 70)
    high_priority_query = select(
        func.count(func.distinct(best_scores_subquery.c.id))
    ).where(
        best_scores_subquery.c.best_score >= 70
    )
    high_priority_result = await db.execute(high_priority_query)
    high_priority_count = high_priority_result.scalar() or 0

    return {
        "summary": {
            "total_leads": total_leads,
            "new_companies_this_week": new_companies_count,
            "total_signals_this_week": total_recent_signals,
            "high_priority_leads": high_priority_count,
            "conversion_rate": conversion_rate,
            "converted_count": converted_count,
            "contacted_count": contacted_count
        },
        "high_value_leads": {
            "multinational": multinational_count,
            "exporter": exporter_count,
            "under_audit": audit_count
        },
        "leads_by_sector": leads_by_sector,
        "top_sectors_by_score": top_sectors_by_score,
        "geographic": {
            "by_city": leads_by_city,
            "by_country": leads_by_country
        },
        "leads_by_status": leads_by_status,
        "score_distribution": score_distribution,
        "recent_signals": recent_signals
    }

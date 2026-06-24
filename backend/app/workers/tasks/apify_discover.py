"""
Apify LinkedIn Discovery - Find NEW Tunisian companies.

Uses Apify LinkedIn Company Search to discover companies:
- Location: Tunisia
- Industries: Engineering, Manufacturing, Construction, Industrial
- Keywords: CAD, SOLIDWORKS, bureau études, ingénierie, fabrication

Creates new Lead records for discovered companies.
"""

import os
import logging
from typing import Dict, Any, List
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.workers.celery_app import celery_app
from app.db.session import AsyncSessionLocal
from app.models.models import Lead, LeadSignal

logger = logging.getLogger(__name__)

APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN")


async def discover_companies_on_linkedin(
    db: AsyncSession,
    keywords: List[str],
    location: str = "Tunisia",
    max_results: int = 100
) -> int:
    """
    Discover companies on LinkedIn using Apify.

    Args:
        db: Database session
        keywords: Search keywords (e.g., ["engineering", "CAD", "manufacturing"])
        location: Geographic location filter
        max_results: Maximum number of companies to discover

    Returns:
        Number of new companies discovered
    """
    if not APIFY_API_TOKEN:
        logger.error("APIFY_API_TOKEN not set - cannot discover companies")
        return 0

    try:
        from apify_client import ApifyClient
    except ImportError:
        logger.error("apify-client not installed. Run: pip install apify-client")
        return 0

    client = ApifyClient(APIFY_API_TOKEN)

    # Use LinkedIn Company Search actor
    # Actor: apify/linkedin-company-search or similar
    # Note: We'll use the sales-navigator search which is more powerful

    discovered_count = 0

    for keyword in keywords:
        try:
            logger.info(f"Searching LinkedIn for: '{keyword}' in {location}")

            # Input for LinkedIn search
            run_input = {
                "searches": [
                    {
                        "keywords": keyword,
                        "location": location,
                    }
                ],
                "maxResults": max_results // len(keywords),  # Distribute quota across keywords
                "proxy": {
                    "useApifyProxy": True,
                    "apifyProxyGroups": ["RESIDENTIAL"]
                }
            }

            # Run the Actor
            # Using apify/linkedin-search-companies-urls
            run = client.actor("apify/linkedin-search-companies-urls").call(run_input=run_input)

            # Fetch results
            company_urls = []
            for item in client.dataset(run["defaultDatasetId"]).iterate_items():
                if item.get("url"):
                    company_urls.append(item["url"])

            logger.info(f"Found {len(company_urls)} company URLs for keyword '{keyword}'")

            # Now scrape each company profile
            if company_urls:
                scrape_input = {
                    "startUrls": [{"url": url} for url in company_urls[:50]],  # Limit to 50 per keyword
                }

                logger.info(f"Scraping {len(scrape_input['startUrls'])} company profiles...")

                scrape_run = client.actor("apify/linkedin-company-scraper").call(run_input=scrape_input)

                # Process scraped companies
                for company in client.dataset(scrape_run["defaultDatasetId"]).iterate_items():
                    success = await create_lead_from_linkedin(db, company)
                    if success:
                        discovered_count += 1

            # Rate limiting between keyword searches
            import asyncio
            await asyncio.sleep(5)

        except Exception as e:
            logger.error(f"Error searching for keyword '{keyword}': {str(e)}")
            continue

    await db.commit()
    logger.info(f"Discovery complete: {discovered_count} new companies added")
    return discovered_count


async def create_lead_from_linkedin(db: AsyncSession, company_data: Dict[str, Any]) -> bool:
    """
    Create a new Lead from LinkedIn company data.

    Args:
        db: Database session
        company_data: Company data from Apify LinkedIn scraper

    Returns:
        True if lead was created, False if skipped (duplicate)
    """
    try:
        company_name = company_data.get("name")
        linkedin_url = company_data.get("url") or company_data.get("linkedInUrl")
        website = company_data.get("website")

        if not company_name:
            logger.warning("Company has no name - skipping")
            return False

        # Check for duplicate by company name or LinkedIn URL
        existing = await db.execute(
            select(Lead).where(
                (Lead.company_name == company_name) |
                (Lead.linkedin_url == linkedin_url) |
                (Lead.website == website)
            )
        )

        if existing.scalar_one_or_none():
            logger.info(f"Company '{company_name}' already exists - skipping")
            return False

        # Extract location (city and country)
        location = company_data.get("headquarters", {})
        city = location.get("city") if isinstance(location, dict) else None
        country = location.get("country") if isinstance(location, dict) else "Tunisia"

        # Extract sector from industry
        industry = company_data.get("industry", "Unknown")

        # Create new lead
        new_lead = Lead(
            company_name=company_name,
            website=website,
            linkedin_url=linkedin_url,
            country=country or "Tunisia",
            city=city,
            sector=industry,
            employee_count=company_data.get("staffCount"),
            scraped_data={
                "linkedin": {
                    "scraped_at": datetime.utcnow().isoformat(),
                    "description": company_data.get("description"),
                    "specialties": company_data.get("specialties", []),
                    "industry": industry,
                    "headquarters": location,
                    "founded": company_data.get("founded"),
                    "company_type": company_data.get("companyType"),
                    "follower_count": company_data.get("followerCount"),
                }
            },
            status="new",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        db.add(new_lead)
        await db.flush()  # Get the lead ID

        # Create signal for LinkedIn discovery
        signal = LeadSignal(
            lead_id=new_lead.id,
            signal_type="linkedin_discovery",
            title=f"Discovered on LinkedIn: {company_name}",
            detail=f"Found via LinkedIn search. Industry: {industry}. Employees: {company_data.get('staffCount', 'unknown')}",
            source_url=linkedin_url,
            detected_at=datetime.utcnow()
        )
        db.add(signal)

        logger.info(f"Created new lead: {company_name} (ID: {new_lead.id})")
        return True

    except Exception as e:
        logger.error(f"Error creating lead from LinkedIn data: {str(e)}")
        return False


@celery_app.task(name="apify_discover.discover_tunisian_companies")
def discover_tunisian_companies_task() -> Dict[str, Any]:
    """
    Celery task to discover Tunisian companies on LinkedIn.
    Searches for engineering, manufacturing, and CAD-related companies.

    Returns:
        Dictionary with discovery results
    """
    import asyncio

    async def _discover():
        async with AsyncSessionLocal() as db:
            # Search keywords targeting ABBK's ideal customers
            keywords = [
                "engineering Tunisia",
                "bureau d'études Tunisie",
                "manufacturing Tunisia",
                "CAD Tunisia",
                "SOLIDWORKS Tunisia",
                "ingénierie mécanique Tunisie",
                "fabrication industrielle Tunisie",
                "construction Tunisia",
                "automotive Tunisia",
                "aerospace Tunisia",
            ]

            discovered = await discover_companies_on_linkedin(
                db=db,
                keywords=keywords,
                location="Tunisia",
                max_results=500  # Aim for 500 companies
            )

            return {
                "discovered_count": discovered,
                "keywords_searched": len(keywords),
                "timestamp": datetime.utcnow().isoformat(),
                "status": "completed"
            }

    loop = asyncio.get_event_loop()
    if loop.is_running():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    try:
        return loop.run_until_complete(_discover())
    except Exception as e:
        logger.error(f"Discovery task failed: {str(e)}")
        return {
            "discovered_count": 0,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
            "status": "failed"
        }


@celery_app.task(name="apify_discover.discover_by_keyword")
def discover_by_keyword_task(keyword: str, max_results: int = 50) -> Dict[str, Any]:
    """
    Discover companies by a specific keyword.
    Useful for targeted searches.

    Args:
        keyword: Search keyword
        max_results: Maximum results to fetch

    Returns:
        Discovery results
    """
    import asyncio

    async def _discover():
        async with AsyncSessionLocal() as db:
            discovered = await discover_companies_on_linkedin(
                db=db,
                keywords=[keyword],
                location="Tunisia",
                max_results=max_results
            )

            return {
                "keyword": keyword,
                "discovered_count": discovered,
                "timestamp": datetime.utcnow().isoformat(),
                "status": "completed"
            }

    loop = asyncio.get_event_loop()
    if loop.is_running():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    try:
        return loop.run_until_complete(_discover())
    except Exception as e:
        logger.error(f"Keyword discovery failed: {str(e)}")
        return {
            "keyword": keyword,
            "discovered_count": 0,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
            "status": "failed"
        }

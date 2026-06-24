"""
Apify LinkedIn Discovery API endpoints.
Allows manual triggering of company discovery and enrichment.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Dict, Any
from datetime import datetime

from app.db.session import get_db
from app.models.models import Lead, User, UserRole
from app.core.deps import get_current_user, require_role

router = APIRouter(prefix="/apify", tags=["apify"])


@router.post("/discover", response_model=Dict[str, Any])
async def trigger_linkedin_discovery(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_role(UserRole.admin, UserRole.manager))
):
    """
    Manually trigger LinkedIn company discovery.
    Searches for Tunisian engineering/manufacturing companies.

    - **Discovers 500+ companies**
    - **Creates new Lead records**
    - **Detects engineering roles**
    - **Runs in background**

    Requires: admin or manager role
    """
    from app.workers.tasks.apify_discover import discover_tunisian_companies_task

    # Trigger task asynchronously
    task = discover_tunisian_companies_task.delay()

    return {
        "status": "started",
        "task_id": task.id,
        "message": "LinkedIn discovery started. This may take 10-30 minutes.",
        "estimated_results": "500+ companies",
        "check_status_at": f"/api/apify/status/{task.id}"
    }


@router.post("/discover/keyword", response_model=Dict[str, Any])
async def discover_by_keyword(
    keyword: str,
    max_results: int = 50,
    current_user: User = Depends(require_role(UserRole.admin, UserRole.manager))
):
    """
    Discover companies by specific keyword.

    Args:
        keyword: Search term (e.g., "SOLIDWORKS Tunisia", "CAD engineering")
        max_results: Maximum companies to fetch (default 50)

    Requires: admin or manager role
    """
    from app.workers.tasks.apify_discover import discover_by_keyword_task

    task = discover_by_keyword_task.delay(keyword, max_results)

    return {
        "status": "started",
        "task_id": task.id,
        "keyword": keyword,
        "max_results": max_results,
        "message": f"Searching LinkedIn for '{keyword}'",
        "check_status_at": f"/api/apify/status/{task.id}"
    }


@router.post("/enrich", response_model=Dict[str, Any])
async def trigger_linkedin_enrichment(
    current_user: User = Depends(require_role(UserRole.admin, UserRole.manager))
):
    """
    Manually trigger LinkedIn enrichment for existing leads.
    Enriches all leads that have LinkedIn URLs.

    Adds:
    - Employee counts
    - Company descriptions
    - Engineering roles
    - Recent hires

    Requires: admin or manager role
    """
    from app.workers.tasks.apify_linkedin import enrich_all_leads_task

    task = enrich_all_leads_task.delay()

    return {
        "status": "started",
        "task_id": task.id,
        "message": "LinkedIn enrichment started",
        "check_status_at": f"/api/apify/status/{task.id}"
    }


@router.get("/status/{task_id}", response_model=Dict[str, Any])
async def get_task_status(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Check status of an Apify task.

    Args:
        task_id: Celery task ID returned from trigger endpoints

    Returns:
        Task status and results (if completed)
    """
    from celery.result import AsyncResult

    task = AsyncResult(task_id)

    if task.state == "PENDING":
        return {
            "task_id": task_id,
            "status": "pending",
            "message": "Task is waiting to start"
        }
    elif task.state == "STARTED":
        return {
            "task_id": task_id,
            "status": "running",
            "message": "Task is currently running"
        }
    elif task.state == "SUCCESS":
        return {
            "task_id": task_id,
            "status": "completed",
            "result": task.result,
            "message": "Task completed successfully"
        }
    elif task.state == "FAILURE":
        return {
            "task_id": task_id,
            "status": "failed",
            "error": str(task.info),
            "message": "Task failed"
        }
    else:
        return {
            "task_id": task_id,
            "status": task.state.lower(),
            "message": f"Task state: {task.state}"
        }


@router.get("/stats", response_model=Dict[str, Any])
async def get_apify_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get statistics about LinkedIn-discovered companies.

    Returns counts of:
    - Total leads with LinkedIn data
    - Leads discovered via LinkedIn
    - Leads with employee data
    - Leads with engineering roles detected
    """
    # Total leads with LinkedIn URLs
    linkedin_count = await db.execute(
        select(func.count(Lead.id)).where(Lead.linkedin_url.isnot(None))
    )
    total_linkedin = linkedin_count.scalar() or 0

    # Leads with LinkedIn scraped data
    enriched_count = await db.execute(
        select(func.count(Lead.id)).where(
            Lead.scraped_data.op('?')('linkedin')  # Check if JSON has 'linkedin' key
        )
    )
    total_enriched = enriched_count.scalar() or 0

    # Leads with employee data
    employee_data_count = await db.execute(
        select(func.count(Lead.id)).where(Lead.employee_count.isnot(None))
    )
    total_with_employees = employee_data_count.scalar() or 0

    return {
        "total_leads_with_linkedin_url": total_linkedin,
        "total_enriched_with_linkedin_data": total_enriched,
        "total_with_employee_counts": total_with_employees,
        "enrichment_coverage": f"{(total_enriched / total_linkedin * 100) if total_linkedin > 0 else 0:.1f}%",
        "timestamp": datetime.utcnow().isoformat()
    }

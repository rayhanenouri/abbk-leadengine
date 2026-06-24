from fastapi import APIRouter, Depends
from app.api.routes.auth import get_current_user
from app.workers.tasks.universal_scraping import (
    scrape_all_directories,
    scrape_all_jobs,
    scrape_all_news,
    scrape_all_training,
    scrape_all_sources,
)

router = APIRouter()

@router.post("/trigger/all")
async def trigger_all_scrapers(current_user = Depends(get_current_user)):
    """
    Trigger ALL 34 verified sources using AI-powered universal scraper.

    Uses Playwright + Claude API - no CSS selectors needed.
    Future-proof and works on any website.

    Returns task IDs for tracking.
    """
    task = scrape_all_sources.delay()

    return {
        "message": "All 34 verified sources triggered (AI-powered scraping)",
        "task_id": task.id,
        "sources": {
            "directories": 12,
            "jobs": 9,
            "news": 3,
            "training": 7,
            "total": 34
        }
    }

@router.post("/trigger/universal/all")
async def trigger_universal_all(current_user = Depends(get_current_user)):
    """
    Same as /trigger/all but explicit universal scraping.
    """
    return await trigger_all_scrapers(current_user)

@router.post("/trigger/{spider_name}")
async def trigger_spider(spider_name: str, current_user = Depends(get_current_user)):
    """
    Trigger a specific spider.
    spider_name: directories, jobs, news, training
    """
    spider_tasks = {
        "directories": scrape_directories,
        "jobs": scrape_jobs,
        "news": scrape_news,
        "training": scrape_training,
    }

    if spider_name not in spider_tasks:
        return {"error": f"Unknown spider: {spider_name}. Valid options: {list(spider_tasks.keys())}"}

    task = spider_tasks[spider_name].delay()

    return {
        "message": f"{spider_name} spider triggered",
        "task_id": task.id,
        "spider": spider_name
    }

@router.get("/status/{task_id}")
async def get_scraping_status(task_id: str, current_user = Depends(get_current_user)):
    """Get status of a scraping task."""
    from celery.result import AsyncResult

    task_result = AsyncResult(task_id)

    return {
        "task_id": task_id,
        "status": task_result.state,
        "result": task_result.result if task_result.ready() else None
    }

from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

celery_app = Celery(
    "abbk_workers",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.workers.tasks.scraping",
        "app.workers.tasks.scoring",
        "app.workers.tasks.enrichment",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Africa/Tunis",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,           # re-queue if worker crashes mid-task
    worker_prefetch_multiplier=1,  # fair distribution across workers
)

# ─── Scheduled jobs (Celery Beat) ─────────────────────────────────────────────
celery_app.conf.beat_schedule = {
    # LinkedIn scrape every 48 hours (Apify quota friendly)
    "scrape-linkedin-companies": {
        "task": "app.workers.tasks.scraping.scrape_linkedin_companies",
        "schedule": crontab(hour="*/48"),
    },
    # News + job boards every 6 hours
    "scrape-news-and-jobs": {
        "task": "app.workers.tasks.scraping.scrape_news_and_jobs",
        "schedule": crontab(hour="*/6"),
    },
    # Tunisian directories daily at 2am
    "scrape-directories": {
        "task": "app.workers.tasks.scraping.scrape_directories",
        "schedule": crontab(hour=2, minute=0),
    },
    # Recalculate all lead scores nightly at 3am
    "recalculate-all-scores": {
        "task": "app.workers.tasks.scoring.recalculate_all_scores",
        "schedule": crontab(hour=3, minute=0),
    },
}

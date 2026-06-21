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
        "app.workers.tasks.logo_detection",
        "app.workers.tasks.maintenance",
        "app.workers.tasks.apify_linkedin",
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
# All scrapers auto-scheduled to keep data fresh
celery_app.conf.beat_schedule = {
    # ═══ DATA COLLECTION (Scrapers) ═══

    # Tunisian business directories - Daily at 2am
    "scrape-directories-daily": {
        "task": "app.workers.tasks.scraping.scrape_directories",
        "schedule": crontab(hour=2, minute=0),
        "options": {"queue": "scrapers"},
    },

    # Business news - Every 6 hours
    "scrape-news-6h": {
        "task": "app.workers.tasks.scraping.scrape_news",
        "schedule": crontab(minute=0, hour="*/6"),  # 00:00, 06:00, 12:00, 18:00
        "options": {"queue": "scrapers"},
    },

    # Job boards hiring signals - Every 12 hours
    "scrape-jobs-12h": {
        "task": "app.workers.tasks.scraping.scrape_jobs",
        "schedule": crontab(minute=0, hour="*/12"),  # 00:00, 12:00
        "options": {"queue": "scrapers"},
    },

    # Apify LinkedIn enrichment - Every 48 hours (quota friendly)
    "apify-linkedin-enrichment-48h": {
        "task": "apify_linkedin.enrich_all_leads",
        "schedule": crontab(minute=0, hour=0, day_of_week="*/2"),  # Every 2 days
        "options": {"queue": "enrichment"},
    },

    # Training centers - Weekly on Monday at 1am
    "scrape-training-weekly": {
        "task": "app.workers.tasks.scraping.scrape_training",
        "schedule": crontab(hour=1, minute=0, day_of_week=1),  # Monday
        "options": {"queue": "scrapers"},
    },

    # International funders - Weekly on Tuesday at 2am
    "scrape-funders-weekly": {
        "task": "app.workers.tasks.scraping.scrape_funders",
        "schedule": crontab(hour=2, minute=0, day_of_week=2),  # Tuesday
        "options": {"queue": "scrapers"},
    },

    # Public tenders - Weekly on Wednesday at 2am
    "scrape-tenders-weekly": {
        "task": "app.workers.tasks.scraping.scrape_tenders",
        "schedule": crontab(hour=2, minute=0, day_of_week=3),  # Wednesday
        "options": {"queue": "scrapers"},
    },

    # ═══ ENRICHMENT (Detection & Analysis) ═══

    # Multinational/exporter/audit detection - Daily at 1am
    "enrichment-flags-daily": {
        "task": "enrichment.detect_all_flags",
        "schedule": crontab(hour=1, minute=0),
        "options": {"queue": "enrichment"},
    },

    # Logo detection on websites - Weekly on Sunday at 3am
    "logo-detection-weekly": {
        "task": "logo_detection.detect_all_websites",
        "schedule": crontab(hour=3, minute=0, day_of_week=0),  # Sunday
        "options": {"queue": "enrichment"},
    },

    # ═══ SCORING & RANKING ═══

    # Recalculate all lead scores - Daily at 4am (after enrichment)
    "recalculate-scores-daily": {
        "task": "app.workers.tasks.scoring.recalculate_all_scores",
        "schedule": crontab(hour=4, minute=0),
        "options": {"queue": "scoring"},
    },

    # ═══ MAINTENANCE ═══

    # Clean old signals - Weekly on Monday at 5am
    "cleanup-old-signals-weekly": {
        "task": "app.workers.tasks.maintenance.cleanup_old_signals",
        "schedule": crontab(hour=5, minute=0, day_of_week=1),  # Monday
        "options": {"queue": "maintenance"},
    },
}

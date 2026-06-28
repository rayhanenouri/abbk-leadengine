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
        "app.workers.tasks.apify_discover",
        "app.workers.tasks.company_enrichment",
        "app.workers.tasks.universal_scraping",
        "app.workers.tasks.full_automation",
        "app.workers.tasks.complete_automation",
        "app.workers.tasks.master_scraping",
        "app.workers.tasks.production_enrichment",  # PRODUCTION: Real signal extraction
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
# COMPLETE AUTOMATION - Everything runs automatically
celery_app.conf.beat_schedule = {
    # ═══ MASTER AUTOMATION PIPELINE ═══
    # This ONE task does EVERYTHING automatically every day
    # NEW: Complete automation with job boards + news search
    "run-complete-automation-daily": {
        "task": "complete_automation.run_complete_pipeline",
        "schedule": crontab(hour=2, minute=0),  # Daily at 2am
        "options": {"queue": "scrapers"},
    },

    # ═══ INDIVIDUAL TASKS (backup - runs if master fails) ═══

    # Discover companies - Daily at 2am
    "discover-companies-daily": {
        "task": "app.workers.tasks.full_automation.discover_companies",
        "schedule": crontab(hour=2, minute=30),
        "options": {"queue": "scrapers"},
    },

    # Find websites - Daily at 3am
    "find-websites-daily": {
        "task": "app.workers.tasks.full_automation.find_company_websites",
        "schedule": crontab(hour=3, minute=0),
        "options": {"queue": "scrapers"},
    },

    # Scrape all websites - Daily at 4am
    "scrape-websites-daily": {
        "task": "app.workers.tasks.full_automation.scrape_all_websites",
        "schedule": crontab(hour=4, minute=0),
        "options": {"queue": "scrapers"},
    },

    # Recalculate scores - Daily at 5am
    "recalculate-scores-daily": {
        "task": "app.workers.tasks.full_automation.recalculate_all_scores",
        "schedule": crontab(hour=5, minute=0),
        "options": {"queue": "scoring"},
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

    # Apify LinkedIn discovery - Weekly on Friday at 3am (discover NEW companies)
    "apify-linkedin-discovery-weekly": {
        "task": "apify_discover.discover_tunisian_companies",
        "schedule": crontab(hour=3, minute=0, day_of_week=5),  # Friday
        "options": {"queue": "enrichment"},
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

    # Engineering events - Monthly on 1st at 2am
    "scrape-events-monthly": {
        "task": "app.workers.tasks.scraping.scrape_events",
        "schedule": crontab(hour=2, minute=0, day_of_month=1),  # 1st of month
        "options": {"queue": "scrapers"},
    },

    # ═══ ENRICHMENT (Detection & Analysis) ═══

    # PRODUCTION ENRICHMENT - Extract real signals from ALL sources
    "production-enrichment-daily": {
        "task": "production_enrichment.enrich_all_companies",
        "schedule": crontab(hour=6, minute=0),  # Daily at 6am (after scraping)
        "options": {"queue": "enrichment"},
    },

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

    # Company enrichment - Weekly on Thursday at 3am
    "company-enrichment-weekly": {
        "task": "company_enrichment.enrich_all_leads",
        "schedule": crontab(hour=3, minute=0, day_of_week=4),  # Thursday
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

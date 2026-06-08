# Task modules for Celery workers
from app.workers.tasks import scraping, scoring, enrichment

__all__ = ["scraping", "scoring", "enrichment"]

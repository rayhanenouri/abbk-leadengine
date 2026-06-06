from app.workers.celery_app import celery_app


@celery_app.task(name="app.workers.tasks.scraping.scrape_linkedin_companies")
def scrape_linkedin_companies():
    """Scrape LinkedIn companies using Apify."""
    print("TODO: Implement LinkedIn scraping")
    return {"status": "not_implemented"}


@celery_app.task(name="app.workers.tasks.scraping.scrape_news_and_jobs")
def scrape_news_and_jobs():
    """Scrape news and job boards."""
    print("TODO: Implement news and jobs scraping")
    return {"status": "not_implemented"}


@celery_app.task(name="app.workers.tasks.scraping.scrape_directories")
def scrape_directories():
    """Scrape Tunisian business directories."""
    print("TODO: Implement directory scraping")
    return {"status": "not_implemented"}

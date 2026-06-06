from app.workers.celery_app import celery_app


@celery_app.task(name="app.workers.tasks.enrichment.enrich_lead")
def enrich_lead(lead_id: int):
    """Enrich a lead with additional data from external sources."""
    print(f"TODO: Enrich lead {lead_id}")
    return {"status": "not_implemented", "lead_id": lead_id}

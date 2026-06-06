from app.workers.celery_app import celery_app


@celery_app.task(name="app.workers.tasks.scoring.recalculate_all_scores")
def recalculate_all_scores():
    """Recalculate lead scores for all leads in the database."""
    print("TODO: Implement score recalculation")
    return {"status": "not_implemented"}


@celery_app.task(name="app.workers.tasks.scoring.calculate_lead_score")
def calculate_lead_score(lead_id: int):
    """Calculate score for a specific lead."""
    print(f"TODO: Calculate score for lead {lead_id}")
    return {"status": "not_implemented", "lead_id": lead_id}

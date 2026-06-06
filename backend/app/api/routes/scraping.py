from fastapi import APIRouter

router = APIRouter()

@router.post("/trigger")
async def trigger_scraping():
    return {"message": "Trigger scraping - TODO"}

@router.get("/status/{task_id}")
async def get_scraping_status(task_id: str):
    return {"task_id": task_id, "status": "pending"}

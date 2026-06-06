from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_leads():
    return {"leads": []}

@router.post("/")
async def create_lead():
    return {"message": "Create lead - TODO"}

@router.get("/{lead_id}")
async def get_lead(lead_id: int):
    return {"lead_id": lead_id}

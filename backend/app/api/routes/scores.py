from fastapi import APIRouter

router = APIRouter()

@router.get("/{lead_id}")
async def get_lead_score(lead_id: int):
    return {"lead_id": lead_id, "score": 0}

@router.post("/{lead_id}/recalculate")
async def recalculate_score(lead_id: int):
    return {"message": "Recalculate score - TODO"}

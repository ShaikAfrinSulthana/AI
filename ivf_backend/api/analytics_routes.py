# ivf_backend/api/analytics_routes.py
from fastapi import APIRouter
router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/ping")
async def ping():
    return {"status":"ok"}

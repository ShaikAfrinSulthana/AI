# ivf_backend/api/feedback_routes.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import logging

router = APIRouter(prefix="/feedback", tags=["feedback"])
logger = logging.getLogger(__name__)


class FeedbackRequest(BaseModel):
    session_id: str
    message_id: str
    rating: int = Field(..., ge=1, le=5)
    category: str = "general"
    comment: Optional[str] = ""
    metadata: Optional[Dict[str, Any]] = None


@router.post("/submit")
async def submit_feedback(payload: FeedbackRequest):
    """
    Unified feedback endpoint for frontend compatibility.
    Accepts rating, category, comments, and metadata.
    """

    logger.info(f"Feedback received: {payload.dict()}")

    # TODO: Save to DB or file. Currently placeholder.
    return {
        "status": "ok",
        "message": "Feedback received",
        "received": payload.dict()
    }

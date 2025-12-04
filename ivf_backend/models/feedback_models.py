from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class FeedbackCategory(str, Enum):
    ACCURACY = "accuracy"
    RELEVANCE = "relevance"
    CLARITY = "clarity"
    EMPATHY = "empathy"
    TIMELINESS = "timeliness"
    GENERAL = "general"

class FeedbackRequest(BaseModel):
    session_id: str = Field(..., description="Session ID for the conversation")
    message_id: str = Field(..., description="Specific message ID being rated")
    rating: int = Field(..., ge=1, le=5, description="Rating from 1-5")
    category: FeedbackCategory = Field(default=FeedbackCategory.GENERAL)
    comment: Optional[str] = Field(None, max_length=500)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @validator('comment')
    def comment_length(cls, v):
        if v and len(v) > 500:
            raise ValueError('Comment must be less than 500 characters')
        return v

class FeedbackResponse(BaseModel):
    feedback_id: str
    status: str
    message: str
    timestamp: datetime
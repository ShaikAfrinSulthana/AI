# ivf_backend/models/chat_models.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from enum import Enum

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class ChatMessage(BaseModel):
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    message_id: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    session_id: str = Field(..., description="Unique session identifier")
    user_id: Optional[str] = None
    language: str = "en"
    include_context: bool = True

class ChatResponse(BaseModel):
    response: str
    session_id: str
    message_id: str
    timestamp: datetime
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    confidence: float = 0.0
    warning: Optional[str] = None

class ConversationSession(BaseModel):
    session_id: str
    user_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    message_count: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
import logging
from ..models.chat_models import ChatRequest, ChatResponse
from ..services.doctor_chatbot import DoctorChatbot

# REMOVE /api prefix
router = APIRouter(prefix="", tags=["chat"])
logger = logging.getLogger(__name__)


def _serialize_chat_response(resp: ChatResponse) -> dict:
    if hasattr(resp, "model_dump"):
        data = resp.model_dump()
    else:
        data = resp.dict()

    ts = data.get("timestamp")
    if hasattr(ts, "isoformat"):
        data["timestamp"] = ts.isoformat()
    else:
        data["timestamp"] = str(ts)

    serial_srcs = []
    for s in data.get("sources", []):
        try:
            serial_srcs.append({
                "id": s.get("id"),
                "category": s.get("category"),
                "question": s.get("question"),
                "similarity_score": float(s.get("similarity_score", 0.0)),
                "warning": s.get("warning")
            })
        except:
            serial_srcs.append({k: str(v) for k, v in s.items()})
    data["sources"] = serial_srcs

    return data


# Now endpoint is: POST /chat
@router.post("/chat", response_model=ChatResponse)
async def handle_chat(req: ChatRequest, request: Request):
    rag = getattr(request.app.state, "rag_engine", None)
    chatbot = DoctorChatbot(rag=rag)

    try:
        resp = chatbot.process_message(req)
        payload = _serialize_chat_response(resp)
        return JSONResponse(status_code=200, content=payload)
    except Exception as e:
        logger.exception(f"/chat error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

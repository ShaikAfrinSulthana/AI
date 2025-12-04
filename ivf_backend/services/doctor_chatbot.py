# ivf_backend/services/doctor_chatbot.py
import logging
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from .rag_engine import RAGEngine
from .llm_engine import LLMEngine
from .memory_manager import MemoryManager
from .safety_handler import SafetyHandler
from ..models.chat_models import ChatRequest, ChatResponse, ChatMessage

logger = logging.getLogger(__name__)


class DoctorChatbot:
    def __init__(
        self,
        rag: Optional[RAGEngine] = None,
        llm: Optional[LLMEngine] = None,
        memory: Optional[MemoryManager] = None,
        safety: Optional[SafetyHandler] = None
    ):
        # allow injection (useful for tests / startup wiring)
        self.rag_engine = rag or RAGEngine()
        self.llm_engine = llm or LLMEngine()
        self.memory_manager = memory or MemoryManager()
        self.safety_handler = safety or SafetyHandler()
        logger.info("DoctorChatbot initialized")

    def process_message(self, chat_request: ChatRequest) -> ChatResponse:
        """
        High-level flow:
        - filter input
        - detect emergency
        - store user message
        - fetch short history
        - optionally RAG -> context
        - generate LLM response
        - filter LLM output
        - store assistant message
        - return ChatResponse (with UTC timestamp)
        """
        try:
            # 1) Input filtering
            filtered = self.safety_handler.filter_content(chat_request.message)
            if not filtered:
                return self._create_error(
                    chat_request.session_id,
                    "I couldn't process that message. Please ask IVF-related questions."
                )

            # 2) Emergency detection
            if self.safety_handler.detect_medical_emergency(filtered):
                return self._create_emergency(chat_request.session_id)

            # 3) Ensure session exists & store user message
            self.memory_manager.create_session(chat_request.session_id, chat_request.user_id)
            self.memory_manager.add_message(chat_request.session_id, "user", filtered)

            # 4) Fetch conversation history (as ChatMessage objects)
            history_msgs: List[ChatMessage] = self.memory_manager.get_conversation_history(
                chat_request.session_id, limit=6
            )

            # Convert history into list of dicts required by LLM
            conversation_history = []
            for m in history_msgs:
                # m.role may be an enum or string
                role = getattr(m, "role", None)
                if hasattr(role, "value"):
                    role_val = role.value
                else:
                    role_val = str(role)
                conversation_history.append({"role": role_val, "content": m.content})

            # 5) RAG retrieval (optional)
            similar_chunks: List[Dict[str, Any]] = []
            if getattr(chat_request, "include_context", True):
                try:
                    similar_chunks = self.rag_engine.search_similar_chunks(filtered, top_k=5) or []
                except Exception as e:
                    # do not fail entire request for RAG errors
                    logger.exception(f"RAG search error (continuing without context): {e}")
                    similar_chunks = []

            # 6) Build context for LLM
            context = self.rag_engine.format_context(similar_chunks) if similar_chunks else ""

            # 7) Generate LLM response
            try:
                llm_resp = self.llm_engine.generate_response(
                    user_message=filtered,
                    context=context,
                    conversation_history=conversation_history,
                    language=getattr(chat_request, "language", "en")
                )
            except Exception as e:
                logger.exception(f"LLM generation error: {e}")
                llm_resp = "I'm experiencing a temporary issue generating a response. Please try again shortly."

            # 8) Post-process LLM output (safety)
            try:
                llm_resp = self.safety_handler.filter_output(llm_resp)
            except Exception:
                # Ensure we never crash the pipeline here
                logger.exception("Safety handler failed while filtering LLM output; returning raw output.")

            # 9) Persist assistant message
            self.memory_manager.add_message(chat_request.session_id, "assistant", llm_resp)

            # 10) Build sources list for response
            sources = []
            for ch in similar_chunks[:3]:
                sources.append({
                    "id": ch.get("id") or ch.get("id", ch.get("chunk_id", None)),
                    "category": ch.get("category", "Unknown"),
                    "question": ch.get("question", "") or "",
                    "similarity_score": float(ch.get("similarity_score", 0.0)),
                    "warning": ch.get("warning") if "warning" in ch else None
                })

            # 11) Compute confidence (simple heuristic)
            max_sim = 0.0
            if sources:
                try:
                    max_sim = max(s.get("similarity_score", 0.0) for s in sources)
                except Exception:
                    max_sim = 0.0
            confidence = float(min(1.0, max(0.0, 0.5 + max_sim / 2.0)))

            # 12) Append a medical disclaimer if not present
            disclaimer_needed = True
            check_text = llm_resp.lower()
            for token in ["consult", "doctor", "medical", "seek medical advice", "healthcare provider"]:
                if token in check_text:
                    disclaimer_needed = False
                    break
            if disclaimer_needed:
                llm_resp = llm_resp.rstrip() + "\n\n⚠️ This information is educational. Consult a healthcare provider for medical advice."

            # 13) Build ChatResponse with UTC ISO timestamp
            resp = ChatResponse(
                response=llm_resp,
                session_id=chat_request.session_id,
                message_id=str(uuid.uuid4()),
                timestamp=datetime.now(timezone.utc),
                sources=sources,
                confidence=confidence,
                warning="MEDICAL WARNING" if any(s.get("warning") for s in sources) else None
            )

            return resp

        except Exception as e:
            logger.exception(f"Unhandled error in DoctorChatbot.process_message: {e}")
            return self._create_error(chat_request.session_id, "Technical error. Try again later.")

    # ---------- helper response factories ----------
    def _create_error(self, session_id: str, message: str) -> ChatResponse:
        return ChatResponse(
            response=message,
            session_id=session_id,
            message_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc),
            sources=[],
            confidence=0.0,
            warning="System error"
        )

    def _create_emergency(self, session_id: str) -> ChatResponse:
        msg = self.safety_handler.get_emergency_response()
        return ChatResponse(
            response=msg,
            session_id=session_id,
            message_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc),
            sources=[],
            confidence=0.0,
            warning="EMERGENCY"
        )

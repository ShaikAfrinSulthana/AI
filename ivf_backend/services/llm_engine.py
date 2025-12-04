# ivf_backend/services/llm_engine.py

import logging
import hashlib
import json
import re
from collections import OrderedDict
from typing import List, Dict, Any, Optional

from ..config import settings

logger = logging.getLogger(__name__)


class LLMEngine:
    """
    IVF-specialized LLM wrapper with:
    - IVF-only strict filtering
    - Document explanation mode (safe)
    - Response caching
    - Groq LLM integration
    """

    def __init__(self):
        self.client = None
        self._initialize_client()

        # Simple FIFO response cache
        self._response_cache: OrderedDict[str, str] = OrderedDict()
        self._cache_max = 256

    # -----------------------------------------------------------
    # Initialize Groq Client
    # -----------------------------------------------------------
    def _initialize_client(self):
        try:
            if not settings.GROQ_API_KEY:
                logger.warning("Groq API Key missing — LLM disabled.")
                return

            try:
                from groq import Groq
                self.client = Groq(api_key=settings.GROQ_API_KEY)
            except ImportError:
                import groq
                self.client = groq.Client(api_key=settings.GROQ_API_KEY)

            logger.info(f"Groq client initialized. Model = {settings.GROQ_MODEL}")

        except Exception as e:
            logger.error(f"Groq initialization error: {e}")
            self.client = None

    # -----------------------------------------------------------
    # Cache utilities
    # -----------------------------------------------------------
    def _make_key(self, sys_prompt, context, history, user_msg):
        payload = {
            "sys": sys_prompt,
            "ctx": context or "",
            "hist": history or "",
            "user": user_msg
        }
        raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def _cache_get(self, key: str) -> Optional[str]:
        if key in self._response_cache:
            val = self._response_cache.pop(key)
            self._response_cache[key] = val
            return val
        return None

    def _cache_set(self, key: str, val: str):
        self._response_cache[key] = val
        if len(self._response_cache) > self._cache_max:
            self._response_cache.popitem(last=False)

    # -----------------------------------------------------------
    # IVF-only Safety Filter
    # -----------------------------------------------------------
    def _is_ivf_related(self, text: str) -> bool:
        ivf_keywords = [
            r"ivf", r"iui", r"icsi", r"embryo", r"egg", r"oocyte",
            r"sperm", r"fertility", r"infertility", r"implantation",
            r"amh", r"beta hcg", r"follicle", r"antral",
            r"endometrium", r"transfer", r"stimulation",
            r"progesterone", r"estrogen", r"pcos", r"endometriosis",
            r"blastocyst", r"luteal", r"hormone", r"trigger shot"
        ]

        pattern = r"|".join(ivf_keywords)
        return bool(re.search(pattern, text.lower()))

    def _reject_non_ivf(self):
        return (
            "I can only help with **IVF, fertility, embryos, sperm, eggs, hormones**, "
            "and reproductive treatment-related questions.\n\n"
            "Your question does **not seem to be IVF-related**, so I cannot answer it."
        )

    # -----------------------------------------------------------
    # System Prompt
    # -----------------------------------------------------------
    def _system_prompt(self, lang: str):
        return (
            "You are an **IVF-only assistant AI**.\n\n"
            "RULES:\n"
            "1. Only answer IVF, fertility, embryo, sperm, egg, and hormone related questions.\n"
            "2. If the question is NOT IVF-related, refuse to answer.\n"
            "3. You are NOT a doctor.\n"
            "4. NEVER give medical advice, diagnosis, treatment, or medication suggestions.\n"
            "5. If anything appears serious, tell the user to **visit their doctor**.\n"
            "6. Keep language simple and supportive.\n"
        )

    # -----------------------------------------------------------
    # CHAT MODE
    # -----------------------------------------------------------
    def generate_response(
        self,
        user_message: str,
        context: str = "",
        conversation_history: List[Dict[str, str]] = None,
        language: str = "en"
    ) -> str:

        # IVF relevance check (CHAT MODE ONLY)
        if not self._is_ivf_related(user_message):
            return self._reject_non_ivf()

        if not self.client:
            return self._fallback(user_message)

        try:
            system_prompt = self._system_prompt(language)
            messages = [{"role": "system", "content": system_prompt}]

            if context:
                messages.append({"role": "system", "content": f"Relevant IVF context:\n{context}"})

            if conversation_history:
                for m in conversation_history[-6:]:
                    messages.append({
                        "role": m.get("role", "user"),
                        "content": m.get("content", "")
                    })

            messages.append({"role": "user", "content": user_message})

            # Cache
            key = self._make_key(system_prompt, context, conversation_history, user_message)
            cached = self._cache_get(key)
            if cached:
                return cached

            response = self.client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=messages,
                temperature=0.25,
                top_p=0.9,
                max_tokens=700,
            )

            output = response.choices[0].message.content.strip()
            self._cache_set(key, output)
            return output

        except Exception as e:
            logger.error(f"Groq LLM error: {e}")
            return self._fallback(user_message)

    # -----------------------------------------------------------
    # DOCUMENT EXPLANATION MODE
    # -----------------------------------------------------------
    def explain_document(self, extracted_text: str) -> str:
        """
        Explains PDFs/DOCX/Images *safely*.
        Does NOT check IVF relevance (documents may contain lab values).
        """

        if not self.client:
            return self._fallback(extracted_text)

        prompt = (
            "A user uploaded a medical document.\n\n"
            f"Extracted Text:\n{extracted_text}\n\n"
            "Your job:\n"
            "- Explain what the document contains in simple language.\n"
            "- Only describe what is present — do NOT diagnose or treat.\n"
            "- If anything appears abnormal, concerning, or urgent, say:\n"
            '  **\"Please visit your doctor for proper medical evaluation.\"**\n'
            "- No medical advice, no treatment recommendations.\n"
            "- Keep it friendly and easy to understand.\n"
        )

        try:
            response = self.client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": "You are a safe IVF document explainer AI."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.25,
                max_tokens=700
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error("Document explanation failed: %s", e)
            return self._fallback(extracted_text)

    # -----------------------------------------------------------
    # Fallback if Groq is unavailable
    # -----------------------------------------------------------
    def _fallback(self, msg: str):
        from ..basic_ivf import get_basic_response
        logger.warning("Fallback IVF response triggered.")
        return get_basic_response(msg)

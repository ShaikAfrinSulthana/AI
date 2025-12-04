# ivf_backend/services/safety_handler.py
import logging, re
from typing import Optional

logger = logging.getLogger(__name__)

class SafetyHandler:
    def __init__(self):
        self.inappropriate_patterns = [r"(?i)\b(illegal|scam|fraud)\b", r"(?i)\b(hack|cheat)\b", r"(?i)\b(porn|explicit|nude)\b"]
        self.self_harm_patterns = [r"(?i)\b(suicide|kill myself|end my life|self[- ]?harm)\b"]
        self.medical_emergency_keywords = ["chest pain", "can't breathe", "cannot breathe", "shortness of breath", "heavy bleeding", "bleeding heavily", "severe pain", "uncontrolled pain", "emergency", "911", "ambulance", "ohss", "severe bloating", "severe abdominal pain", "ectopic", "ectopic pregnancy", "fever after retrieval", "infection after transfer", "vomiting violently", "fainting", "dizziness"]
        self.ivf_keywords = ["ivf", "fertility", "embryo", "egg retrieval", "sperm", "semen analysis", "transfer", "blastocyst", "pregnancy test", "trigger shot", "follicle", "stimulation", "beta", "implantation", "progesterone", "estrogen", "luteal phase", "hcg", "pcos", "amh", "fsh", "endometrium", "iui", "icsi"]

    def filter_content(self, text: str) -> Optional[str]:
        if not text or not text.strip():
            return None
        t = text.lower()
        for pattern in self.self_harm_patterns:
            if re.search(pattern, t):
                return ("I'm really sorry you're feeling like this. Please reach out to emergency services or a trusted person right away.")
        for pattern in self.inappropriate_patterns:
            if re.search(pattern, t):
                logger.warning(f"Inappropriate blocked: {text}")
                return None
        for word in self.medical_emergency_keywords:
            if word in t:
                return text
        for word in self.ivf_keywords:
            if word in t:
                return text
        # not IVF — return text but the chatbot will guide
        return text.strip()

    def filter_output(self, text: str) -> str:
        unsafe_patterns = [r"(?i)\b(stop taking\b)", r"(?i)\b(increase (your )?dose\b)", r"(?i)\b(replace your doctor\b)", r"(?i)\b(you don't need a doctor)\b"]
        for pat in unsafe_patterns:
            if re.search(pat, text):
                logger.warning("Unsafe medical instruction removed from LLM output.")
                return ("I cannot provide instructions about changing medications or treatment. Please consult your fertility specialist or doctor before making medical decisions.")
        return text

    def detect_medical_emergency(self, text: str) -> bool:
        t = text.lower()
        return any(k in t for k in self.medical_emergency_keywords)

    def get_emergency_response(self) -> str:
        return ("🚨 **POSSIBLE MEDICAL EMERGENCY DETECTED** 🚨\nPlease seek immediate medical help. Call emergency services or go to the nearest ER.")

# ivf_frontend/utils/multilingual.py
from typing import Dict, List

# Minimal i18n mapping for the UI. Extend as needed.
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "en": {
        "welcome": "Welcome to IVF Assistant",
        "subtitle": "Evidence-based answers about fertility & treatment",
        "input_placeholder": "Type your question here...",
        "send": "Send",
        "voice_input": "Record voice",
        "upload_document": "Upload document",
        "choose_file": "Choose a file",
        "feedback": "Feedback",
        "rate_response": "Rate the response",
        "upload_success": "Uploaded to server",
    },
    "hi": {
        "welcome": "IVF सहायक में आपका स्वागत है",
        "subtitle": "प्रसव और उपचार के बारे में जानकारी",
        "input_placeholder": "यहाँ अपना प्रश्न टाइप करें...",
        "send": "भेजें",
    },
    "es": {
        "welcome": "Bienvenido al asistente de FIV",
        "subtitle": "Respuestas basadas en evidencia sobre fertilidad",
        "input_placeholder": "Escribe tu pregunta aquí...",
        "send": "Enviar",
    }
}

def get_languages() -> List[str]:
    return list(TRANSLATIONS.keys())

def get_translation(key: str, default: str = None, lang: str = "en") -> str:
    if lang not in TRANSLATIONS:
        lang = "en"
    return TRANSLATIONS[lang].get(key, default or key)

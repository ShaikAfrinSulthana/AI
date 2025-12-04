# ivf_frontend/utils/helpers.py
import os
import typing as t
from pathlib import Path

import requests

# Default backend (change with env var)
DEFAULT_BACKEND = "http://localhost:8000"

def get_backend_url() -> str:
    return os.getenv("BACKEND_URL", DEFAULT_BACKEND).rstrip("/")

# -------------------------------------------------------
# CLEAN ROUTE MAP (no more /api/*)
# -------------------------------------------------------
route_map = {
    "/chat": "/chat",                        # chat endpoint
    "/feedback": "/feedback",                # feedback
    "/ready": "/ready",                      # health check
    "/documents/analyze": "/documents/analyze",# document analyzer
    
    "/audio/transcribe": "/audio/transcribe",    # STT
    "/tts/speak": "/tts/speak",              # TTS
}

def get_api_url(logical_path: str) -> str:
    """
    Convert logical frontend paths → real backend endpoints.
    No /api prefix anywhere.
    """
    base = get_backend_url()
    mapped = route_map.get(logical_path, logical_path)

    if not mapped.startswith("/"):
        mapped = "/" + mapped

    return base + mapped


# -------------------------------------------------------
# Session state helper
# -------------------------------------------------------
def initialize_session_state(defaults: t.Optional[dict] = None) -> None:
    import streamlit as st
    if defaults is None:
        defaults = {}
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# -------------------------------------------------------
# Backend readiness check
# -------------------------------------------------------
def check_backend_ready(timeout: int = 3) -> dict:
    url = get_api_url("/ready")
    try:
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
        try:
            return resp.json()
        except ValueError:
            return {"status": "ok", "raw": resp.text}
    except Exception as exc:
        raise RuntimeError(f"Failed to contact backend at {url}: {exc}") from exc


# -------------------------------------------------------
# Simple translations
# -------------------------------------------------------
_default_translations = {
    "welcome": "Welcome to IVF Assistant",
    "subtitle": "Evidence-based answers about fertility & treatment",
    "input_placeholder": "Type your message here...",
    "send": "Send",
    "voice_input": "Voice input",
    "upload_document": "Upload document",
    "choose_file": "Choose a file",
    "feedback": "Feedback",
}

def get_translation(key: str, default: str = None) -> str:
    if default is None:
        default = _default_translations.get(key, key)
    return _default_translations.get(key, default)

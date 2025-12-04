# ivf_frontend/app.py

import os
import uuid
from pathlib import Path
from datetime import datetime

import streamlit as st

# Components
from ivf_frontend.components.sidebar import render_sidebar
from ivf_frontend.components.chat_interface import render_chat_interface
from ivf_frontend.components.voice_recorder import render_voice_recorder
from ivf_frontend.components.file_uploader import render_file_uploader
from ivf_frontend.components.theme_toggle import render_theme_toggle, apply_theme_css
from ivf_frontend.components.feedback_system import render_feedback_system

# Utilities
from ivf_frontend.utils.helpers import (
    initialize_session_state,
    get_api_url,
    get_backend_url,
)
from ivf_frontend.utils.animations import render_welcome_animation
from ivf_frontend.utils.multilingual import get_translation


# Optional Validator
try:
    from ivf_frontend.utils.validators import InputValidator
    def validate_message_content(x: str) -> bool:
        return InputValidator.validate_message_content(x)
except Exception:
    def validate_message_content(x: str) -> bool:
        return bool(x and x.strip() and len(x.strip()) <= 5000)


# -------------------------
# Page setup
# -------------------------
st.set_page_config(
    page_title="IVF Medical Assistant",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)


def load_css():
    css_file = Path(__file__).parent / "assets" / "frontend.css"
    if css_file.exists():
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# -------------------------
# Main App
# -------------------------
def main():
    # Initialize session state
    initialize_session_state({
        "messages": [],
        "chat_input": "",
        "clear_input": False,
        "show_feedback": False,
        "language": "en",
        "session_id": str(uuid.uuid4()),
        "theme": "light",
    })

    apply_theme_css()
    load_css()

    # ---------------------------------
    # NEW: Capture selected page
    # ---------------------------------
    page = render_sidebar()

    # -----------------------------
    # PAGE: CHAT
    # -----------------------------
    if page == "Chat":
        col_left, col_main, col_right = st.columns([1, 6, 1])

        with col_main:

            render_welcome_animation()

            # Chat interface
            render_chat_interface()

            # Spacing
            st.markdown(" ")

            # Bottom interaction toolbar
            st.markdown(
                """
                <div style='
                    padding: 15px;
                    border-radius: 12px;
                    background: rgba(150,150,150,0.08);
                    margin-top: 20px;
                    margin-bottom: 10px;
                '>
                """,
                unsafe_allow_html=True
            )

            toolbar_cols = st.columns([1, 1, 1])

            # Voice recorder
            with toolbar_cols[0]:
                try:
                    render_voice_recorder()
                except Exception as e:
                    st.info("🎤 Voice unavailable")
                    st.caption(str(e))

            # Document upload shortcut (works but minimized)
            with toolbar_cols[1]:
                st.write("📄 Upload in left menu")

            # Feedback
            with toolbar_cols[2]:
                render_feedback_system()

            st.markdown("</div>", unsafe_allow_html=True)

    # -----------------------------
    # PAGE: DOCUMENT UPLOAD
    # -----------------------------
    elif page == "Upload Documents":

        st.markdown("## 📄 Upload & Analyze Medical Documents")

        col_left, col_main, col_right = st.columns([1, 6, 1])
        with col_main:
            try:
                render_file_uploader()
            except Exception as e:
                st.error(f"Document upload failed: {e}")

        st.markdown("---")
        st.info("Your documents will be processed safely using IVF-focused rules.")

    else:
        st.error(f"Invalid page selected: {page}")
        return

    # -----------------------------
    # Footer
    # -----------------------------
    backend = get_backend_url()
    st.caption(f"Backend URL: {backend}")

    if st.button("Reconnect / Refresh"):
        try:
            get_api_url("/ready")
        finally:
            st.rerun()


if __name__ == "__main__":
    main()

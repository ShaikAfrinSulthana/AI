# ivf_frontend/components/sidebar.py
import streamlit as st
from pathlib import Path

from ivf_frontend.utils.helpers import check_backend_ready
from ivf_frontend.utils.multilingual import get_translation, get_languages

ASSETS_DIR = Path(__file__).parent.parent / "assets"


def render_sidebar() -> str:
    """Render the sidebar UI and return the selected page name."""

    # Header
    st.sidebar.markdown(
        """
        <div style="padding:8px 0; display:flex; align-items:center;">
            <div style="font-size:1.2rem; margin-right:8px;">👶</div>
            <div style="line-height:1;">
                <div style="font-size:1.05rem; font-weight:700;">IVF Assistant</div>
                <div style="font-size:0.85rem; opacity:0.7;">Your fertility companion</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ------------------------------------------
    # NEW: Navigation menu for multipage layout
    # ------------------------------------------
    pages = ["Chat", "Upload Documents"]

    if "page" not in st.session_state:
        st.session_state.page = "Chat"

    page = st.sidebar.radio(
        "Navigate",
        pages,
        index=pages.index(st.session_state.page)
    )

    st.session_state.page = page

    st.sidebar.markdown("---")

    # Language selector
    languages = get_languages()
    current_lang = st.session_state.get("language", "en")
    selection = st.sidebar.selectbox(
        "Language",
        options=languages,
        index=languages.index(current_lang) if current_lang in languages else 0
    )
    st.session_state.language = selection

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Controls")
    if st.sidebar.button("Clear messages"):
        st.session_state.messages = []
        st.session_state.chat_input = ""
        st.experimental_rerun()

    # Backend health
    try:
        check_backend_ready()
        st.sidebar.success("Backend: ready")
    except Exception:
        st.sidebar.warning("Backend: unavailable")

    # IMPORTANT: return selected page
    return page

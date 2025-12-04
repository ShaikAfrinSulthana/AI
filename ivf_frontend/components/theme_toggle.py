# ivf_frontend/components/theme_toggle.py
import streamlit as st
from pathlib import Path

def apply_theme_css():
    """
    Very small theme toggler: inject CSS variables for light/dark.
    This is intentionally simple; you can expand CSS in assets/frontend.css
    """
    theme = st.session_state.get("theme", "light")
    if theme == "dark":
        css = """
        <style>
        :root {
            --background: #0f1724;
            --text-color: #e6eef8;
            --secondary-bg: #0b1220;
            --border-color: #203040;
        }
        body { background: var(--background); color: var(--text-color); }
        </style>
        """
    else:
        css = """
        <style>
        :root {
            --background: #ffffff;
            --text-color: #222222;
            --secondary-bg: #f7fafc;
            --border-color: #e6e6e6;
        }
        body { background: var(--background); color: var(--text-color); }
        </style>
        """
    st.markdown(css, unsafe_allow_html=True)

def render_theme_toggle():
    if "theme" not in st.session_state:
        st.session_state.theme = "light"

    with st.sidebar:
        st.markdown("---")
        st.markdown("### Appearance")
        sel = st.radio("Mode", options=["light", "dark"], index=0 if st.session_state.theme == "light" else 1, key="theme_selector", horizontal=True)
        if sel != st.session_state.theme:
            st.session_state.theme = sel
            apply_theme_css()
            st.experimental_rerun()

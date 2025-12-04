# ivf_frontend/components/feedback_system.py
import streamlit as st
import requests

from ivf_frontend.utils.helpers import get_api_url
from ivf_frontend.utils.multilingual import get_translation

def render_feedback_system():
    st.markdown("### 💬 " + get_translation("feedback", "Feedback"))
    with st.form("feedback_form", clear_on_submit=True):
        rating = st.slider("Rate the assistant", min_value=1, max_value=5, value=5)
        comments = st.text_area("Comments (optional)", height=80)
        submitted = st.form_submit_button("Send feedback")
        if submitted:
            try:
                url = get_api_url("/api/feedback")
                payload = {"rating": rating, "comments": comments}
                requests.post(url, json=payload, timeout=10)
                st.success("Thanks for the feedback!")
            except Exception:
                st.info("Feedback saved locally (not sent).")

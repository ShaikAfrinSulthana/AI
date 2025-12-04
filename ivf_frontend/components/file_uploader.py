# ivf_frontend/components/file_uploader.py

import streamlit as st
import requests
from ivf_frontend.utils.helpers import get_api_url


def render_file_uploader():
    """
    Document upload UI for IVF chatbot.
    Handles IVF relevance checks and prevents showing raw JSON errors.
    """

    st.subheader("📄 Upload Medical Documents")

    uploaded = st.file_uploader(
        "Upload PDF / DOCX / TXT",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=False
    )

    if not uploaded:
        return

    st.info(f"Processing: **{uploaded.name}**")

    try:
        files = {
            "file": (uploaded.name, uploaded.getvalue(), uploaded.type)
        }

        api_url = get_api_url("/documents/analyze")
        response = requests.post(api_url, files=files)

        # ---------------------------
        # ❌ HANDLE NON-IVF DOCUMENT
        # ---------------------------
        if response.status_code == 400:
            data = response.json()
            if "relevant" in data and data["relevant"] is False:
                st.error("🚫 This document is **not related to IVF or reproductive health**.\n\n"
                         "Please upload a valid fertility or reproductive health report.")
                return

            # Other 400 errors
            st.error("⚠️ The document could not be processed. Please check the file.")
            return

        # ---------------------------
        # ❌ HANDLE SERVER ERRORS
        # ---------------------------
        if response.status_code != 200:
            st.error("⚠️ Something went wrong while processing the document.")
            return

        # ---------------------------
        # ✔ IVF RELEVANT DOCUMENT
        # ---------------------------
        data = response.json()

        st.success("✅ IVF-related document processed successfully!")

        st.write("### 📝 Extracted Text")
        st.write(data.get("extracted_text", ""))

        st.write("### 🤖 Summary (Safe Explanation)")
        st.write(data.get("explanation", ""))

    except Exception as e:
        st.error(f"❌ Document processing failed: {str(e)}")

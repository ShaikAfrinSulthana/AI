# ivf_frontend/components/chat_interface.py

import streamlit as st
from datetime import datetime
import html
import requests
import uuid
import base64
import math

# Correct Streamlit component import
import streamlit.components.v1 as components

from ivf_frontend.utils.multilingual import get_translation
from ivf_frontend.utils.helpers import get_api_url


# ---------------------------------------------------
#  Play Bot Voice Output (TTS)
# ---------------------------------------------------
def play_voice_output(text: str):
    try:
        tts_url = get_api_url("/tts/speak")
        resp = requests.post(tts_url, json={"text": text}, timeout=30)
        if resp.status_code != 200:
            return
        audio_base64 = resp.json().get("audio")
        if not audio_base64:
            return
        audio_bytes = base64.b64decode(audio_base64)
        st.audio(audio_bytes, format="audio/mp3")
    except:
        pass


# ---------------------------------------------------
#   Helper: estimate iframe height for a text block
# ---------------------------------------------------
def _estimate_height_for_text(text: str) -> int:
    chars_per_line = 60
    line_height_px = 22
    base = 80
    lines = max(1, math.ceil(len(text) / chars_per_line))
    height = base + (lines * line_height_px)
    return min(max(120, height), 800)


# ---------------------------------------------------
#   Render chat bubble using components.html
# ---------------------------------------------------
def render_bubble(role: str, text: str, ts: str):
    safe_text = html.escape(text).replace("\n", "<br/>")

    is_user = role == "user"
    icon = "🧑🏻" if is_user else "🤖"

    if is_user:
        bg_color = "#EDE4FF"
        align = "flex-end"
        direction = "row-reverse"
        ts_color = "rgba(0,0,0,0.45)"
        text_color = "#000"
    else:
        bg_color = "#E8F4FF"
        align = "flex-start"
        direction = "row"
        ts_color = "rgba(0,0,0,0.45)"
        text_color = "#000"

    html_block = f"""
    <div style="display:flex; justify-content:{align}; margin:12px 0;
         font-family: Inter, system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial;">
      
      <div style="display:flex; flex-direction:{direction}; gap:12px;
           max-width:75%; align-items:flex-start;">

        <!-- Icon -->
        <div style="font-size:26px; margin-top:5px;">{icon}</div>

        <!-- Bubble -->
        <div style="
            background:{bg_color};
            color:{text_color};
            padding:14px 16px;
            border-radius:16px;
            max-width:100%;
            font-size:15px;
            line-height:1.5;
            box-shadow:0 2px 6px rgba(0,0,0,0.18);
            word-wrap:break-word;
            white-space:pre-wrap;
        ">
            {safe_text}
            <div style="font-size:10px; color:{ts_color}; margin-top:8px;">
                {ts}
            </div>
        </div>
      </div>
    </div>
    """

    height = _estimate_height_for_text(text)
    components.html(html_block, height=height, scrolling=False)


# ---------------------------------------------------
#   Main Chat Interface
# ---------------------------------------------------
def render_chat_interface():

    st.markdown("## 💬 Chat")

    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Render message history
    for m in st.session_state.messages:
        render_bubble(m.get("role", "user"), m.get("text", ""), m.get("ts", ""))

    # User input box
    user_text = st.text_area(
        "Message",
        key="chat_input",
        placeholder=get_translation("input_placeholder"),
        label_visibility="collapsed",
        height=120,
    )

    if st.button(get_translation("send")):
        query = user_text.strip()
        if not query:
            st.warning("Please enter a message.")
            return

        # Store user message
        st.session_state.messages.append({
            "role": "user",
            "text": query,
            "ts": datetime.utcnow().isoformat()
        })

        payload = {
            "message": query,
            "session_id": st.session_state.session_id,
            "language": "en",
            "include_context": True
        }

        # Backend call
        try:
            url = get_api_url("/chat")
            resp = requests.post(url, json=payload, timeout=25)
            if resp.status_code == 200:
                answer = resp.json().get("response", "")
            else:
                answer = "⚠ Backend error: " + resp.text
        except Exception as e:
            answer = f"❌ Cannot connect to backend: {e}"

        # Store assistant message
        st.session_state.messages.append({
            "role": "assistant",
            "text": answer,
            "ts": datetime.utcnow().isoformat()
        })

        # Optional: voice
        play_voice_output(answer)

        # Refresh UI
        st.rerun()

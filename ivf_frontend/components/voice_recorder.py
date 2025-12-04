import streamlit as st
import requests
from ivf_frontend.utils.helpers import get_api_url
from ivf_frontend.utils.multilingual import get_translation


def render_voice_recorder():
    st.markdown("### 🎙️ " + get_translation("speak_question", "Speak Your Question"))
    st.caption(get_translation("speak_prompt", "Tap the microphone above and speak your question."))

    # --- THIS SHOWS MICROPHONE ---
    audio = st.audio_input("Voice Input", label_visibility="collapsed")

    if not audio:
        return

    try:
        with st.spinner("Processing audio... Please wait."):

            # -----------------------------------------------------
            # FIX: Convert UploadedFile → raw bytes
            # -----------------------------------------------------
            audio_bytes = audio.read()

            # MIME fix (Streamlit sometimes sends octet-stream)
            mime = audio.type or "audio/wav"
            if mime == "application/octet-stream":
                mime = "audio/wav"

            # Fix filename (Groq requires proper extension)
            filename = audio.name or "audio.wav"
            if not filename.endswith(".wav"):
                filename = "audio.wav"

            files = {
                "file": (filename, audio_bytes, mime)
            }

            stt_url = get_api_url("/audio/transcribe")
            resp = requests.post(stt_url, files=files, timeout=40)

            if resp.status_code != 200:
                st.error("Sorry, I couldn't understand the audio. Please try again.")
                return

            text = resp.json().get("text", "").strip()

        if not text:
            st.warning("I couldn’t clearly understand what you said. Please try again.")
            return

        st.markdown("#### 🗣️ You said")
        st.success(text)

        # -----------------------------------------------------
        # CHAT ENGINE
        # -----------------------------------------------------
        with st.spinner("Preparing an answer…"):
            chat_url = get_api_url("/chat")
            payload = {
                "message": text,
                "session_id": st.session_state.get("session_id", "default-session"),
                "language": "en",
                "include_context": True
            }
            chat_resp = requests.post(chat_url, json=payload, timeout=60)

            if chat_resp.status_code != 200:
                st.error("The assistant couldn't generate a response.")
                return

            answer = chat_resp.json().get("response", "")

        st.markdown("#### 🤖 AI Response")
        st.write(answer)

        # -----------------------------------------------------
        # TTS ENGINE
        # -----------------------------------------------------
        with st.spinner("Generating voice reply…"):
            tts_url = get_api_url("/tts/speak")
            tts_resp = requests.post(tts_url, json={"text": answer}, timeout=40)

            try:
                tts_data = tts_resp.json()
            except:
                tts_data = {}

        audio_content = tts_data.get("audio")

        if audio_content:
            st.audio(audio_content)
        else:
            st.caption("🔇 Voice playback unavailable.")

    except Exception as e:
        st.error(f"Something went wrong while processing your voice: {str(e)}")

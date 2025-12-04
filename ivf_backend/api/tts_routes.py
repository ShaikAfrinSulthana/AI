from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os
import requests
from pydub import AudioSegment
import io

router = APIRouter(prefix="/audio", tags=["audio"])

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/audio/transcriptions"


@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """Accept Streamlit audio, convert to WAV, then send to Groq."""

    try:
        if not GROQ_API_KEY:
            raise HTTPException(status_code=500, detail="GROQ_API_KEY missing")

        # Read raw bytes
        raw_bytes = await file.read()

        # Detect/force MIME
        mime = file.content_type or "audio/webm"
        if mime == "application/octet-stream":
            mime = "audio/webm"

        # -----------------------------
        # 🔥 Convert ANY audio → WAV
        # -----------------------------
        audio_segment = AudioSegment.from_file(io.BytesIO(raw_bytes))
        wav_buffer = io.BytesIO()
        audio_segment.export(wav_buffer, format="wav")
        wav_buffer.seek(0)

        # Prepare Groq request
        files = {
            "file": ("audio.wav", wav_buffer.read(), "audio/wav")
        }

        data = {
            "model": "whisper-large-v3-turbo",
            "response_format": "json"
        }

        # Send to Groq
        resp = requests.post(
            GROQ_URL,
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            files=files,
            data=data,
            timeout=40,
        )

        if resp.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"GROQ Whisper error: {resp.text}"
            )

        text = resp.json().get("text", "").strip()

        return JSONResponse(status_code=200, content={"text": text})

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"STT conversion error: {str(e)}"
        )

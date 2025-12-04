from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os
import requests

router = APIRouter(prefix="/audio", tags=["audio"])

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/audio/transcriptions"


@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Accept audio from Streamlit and send directly to Groq Whisper.
    Handles bad MIME types and forces valid filename extension.
    """

    try:
        if not GROQ_API_KEY:
            raise HTTPException(status_code=500, detail="GROQ_API_KEY missing")

        # --- FIX MIME TYPE ---
        mime = file.content_type or "audio/wav"

        # Streamlit often gives "application/octet-stream"
        if mime == "application/octet-stream":
            mime = "audio/wav"

        # --- FIX FILENAME ---
        # Streamlit gives weird filenames; Groq accepts .wav
        filename = file.filename or "audio.wav"
        if not filename.endswith(".wav"):
            filename = "audio.wav"

        # Read audio bytes
        audio_bytes = await file.read()

        files = {
            "file": (filename, audio_bytes, mime)
        }

        data = {
            "model": "whisper-large-v3-turbo",
            "response_format": "json"
        }

        resp = requests.post(
            GROQ_URL,
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            files=files,
            data=data,
            timeout=40,
        )

        # --- DEBUG ---
        print("\n=== GROQ RESPONSE START ===")
        print(resp.status_code)
        print(resp.text[:500])
        print("=== GROQ RESPONSE END ===\n")

        if resp.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"GROQ Whisper Error ({resp.status_code}): {resp.text}"
            )

        result = resp.json()
        text = result.get("text", "").strip()

        return JSONResponse(status_code=200, content={"text": text})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"STT error: {str(e)}")

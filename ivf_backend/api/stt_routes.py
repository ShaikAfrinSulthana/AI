# ivf_backend/api/stt_routes.py
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
import traceback
import os

from ivf_backend.services.audio_service import AudioService
from ivf_backend.services.speech_to_text import SpeechToText

router = APIRouter(prefix="/audio", tags=["audio"])

# Initialize engines once (fail early on startup if model missing)
stt_engine = SpeechToText()
audio_svc = AudioService()


@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Robust STT endpoint that always returns JSON.
    Frontend should POST multipart/form-data with field "file".
    Response: {"text": "..."} on success or {"error": "..."} on failure.
    """
    try:
        # save uploaded raw bytes to temp file
        saved_path = audio_svc.save_uploaded_file(file)
        # convert to wav 16k mono
        wav_path = audio_svc.convert_to_wav(saved_path)

        # transcribe
        text = stt_engine.transcribe(wav_path)

        # cleanup temporary files (best-effort)
        try:
            if os.path.exists(saved_path):
                os.remove(saved_path)
            if os.path.exists(wav_path) and wav_path != saved_path:
                os.remove(wav_path)
        except Exception:
            pass

        return JSONResponse(status_code=200, content={"text": text})

    except Exception as e:
        # Return JSON error (no HTML), include traceback in logs only
        tb = traceback.format_exc()
        # Log server-side
        print("STT ERROR:", str(e))
        print(tb)
        return JSONResponse(status_code=500, content={"error": str(e)})

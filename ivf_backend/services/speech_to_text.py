# ivf_backend/services/speech_to_text.py

import os
import json
import wave
import vosk

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_PATH = os.path.join(BASE_DIR, "models", "vosk-model-small-en-us-0.15")


class SpeechToText:

    def __init__(self):
        if not os.path.exists(MODEL_PATH):
            raise RuntimeError(
                f"❌ Vosk model missing at: {MODEL_PATH}\n"
                f"Download from: https://alphacephei.com/vosk/models\n"
                f"Extract into: ivf_backend/models/"
            )

        print(f"✔ Loading Vosk model from: {MODEL_PATH}")
        self.model = vosk.Model(MODEL_PATH)

    def transcribe(self, wav_path: str) -> str:
        if not os.path.exists(wav_path):
            raise FileNotFoundError("WAV file not found")

        wf = wave.open(wav_path, "rb")

        if (
            wf.getnchannels() != 1 
            or wf.getsampwidth() != 2 
            or wf.getframerate() not in [8000, 16000]
        ):
            raise RuntimeError(
                "Audio must be mono PCM WAV (16-bit), 8k or 16k sample rate"
            )

        rec = vosk.KaldiRecognizer(self.model, wf.getframerate())

        text = ""
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                partial = json.loads(rec.Result()).get("text", "")
                text += partial + " "

        final = json.loads(rec.FinalResult()).get("text", "")
        result = (text + " " + final).strip()
        return result

# ivf_backend/services/audio_service.py

import io
import os
import tempfile
from pydub import AudioSegment


class AudioService:

    @staticmethod
    def save_uploaded_file(upload_file):
        """
        Save uploaded audio to a temporary file.
        Works for WebM, OGG, MP4, M4A, WAV, etc.
        """

        suffix = os.path.splitext(upload_file.filename)[1] or ".webm"

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(upload_file.file.read())
            return tmp.name

    @staticmethod
    def convert_to_wav(input_path):
        """
        Convert the uploaded audio file to 16kHz mono WAV
        using ONLY Python (no FFmpeg).
        """

        try:
            # Load using pydub (can decode webm/ogg/mp4 etc.)
            sound = AudioSegment.from_file(input_path)

            # Convert to required format
            sound = sound.set_frame_rate(16000).set_channels(1)

            # Output file
            output_path = input_path.rsplit(".", 1)[0] + ".wav"

            # Export as WAV
            sound.export(output_path, format="wav")

            return output_path

        except Exception as e:
            raise Exception(f"Python audio decode/convert failed: {e}")

# ivf_backend/config.py

from pydantic_settings import BaseSettings
from typing import List
from pathlib import Path
import json
import os


class Settings(BaseSettings):
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    # ---------------------------------------------------------
    # Supabase
    # ---------------------------------------------------------
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""

    # ---------------------------------------------------------
    # LLM / Embeddings
    # ---------------------------------------------------------
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"

    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
  

    # ---------------------------------------------------------
    # RAG Settings
    # ---------------------------------------------------------
    SIMILARITY_TOP_K: int = 5
    SIMILARITY_THRESHOLD: float = 0.40

    # ---------------------------------------------------------
    # App Settings
    # ---------------------------------------------------------
    DEBUG: bool = False
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # ---------------------------------------------------------
    # CORS allowed origins
    # ---------------------------------------------------------
    CORS_ORIGINS: List[str] = [
        "http://localhost:8501",
        "http://127.0.0.1:8501",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"
    ]

    # ---------------------------------------------------------
    # File Uploads
    # ---------------------------------------------------------
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".txt", ".doc", ".docx", ".csv"]

    # ---------------------------------------------------------
    # Data directory
    # ---------------------------------------------------------
    DATA_DIR: str = str(Path(__file__).parent / "data")

    # ---------------------------------------------------------
    # Normalize extensions if in .env
    # ---------------------------------------------------------
    def __init__(self, **values):
        super().__init__(**values)

        raw = os.getenv("ALLOWED_EXTENSIONS")
        if raw:
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, list):
                    object.__setattr__(
                        self,
                        "ALLOWED_EXTENSIONS",
                        [("." + ext if not ext.startswith(".") else ext).lower()
                         for ext in parsed]
                    )
            except Exception:
                parts = [p.strip() for p in raw.split(",")]
                object.__setattr__(
                    self,
                    "ALLOWED_EXTENSIONS",
                    [("." + p if not p.startswith(".") else p).lower()
                     for p in parts if p]
                )


settings = Settings()

if settings.DEBUG:
    print("==== DEBUG: Settings Loaded ====")
    print("SUPABASE_URL:", settings.SUPABASE_URL)
    print("GROQ_MODEL:", settings.GROQ_MODEL)
    print("EMBEDDING_MODEL:", settings.EMBEDDING_MODEL)
    print("DATA_DIR:", settings.DATA_DIR)

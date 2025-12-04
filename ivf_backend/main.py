# ivf_backend/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi import status
import logging, uvicorn, traceback
from pathlib import Path
from .config import settings
from .api.chat_routes import router as chat_router
from .api.feedback_routes import router as feedback_router
from .api.document_routes import router as document_router
from .api.analytics_routes import router as analytics_router
from .api.audio_routes import router as audio_router
from .services.rag_engine import RAGEngine
from .api.tts_routes import router as tts_router
from .api.stt_routes import router as stt_router
from dotenv import load_dotenv
import os
print(" Loaded GROQ key:", os.getenv("GROQ_API_KEY"))


load_dotenv()


logging.basicConfig(level=logging.INFO if not settings.DEBUG else logging.DEBUG,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="IVF Medical Chatbot API", version="1.0.0", docs_url="/api/docs", redoc_url="/api/redoc")
app.add_middleware(CORSMiddleware,
                   allow_origins=settings.CORS_ORIGINS,
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"],)

app.include_router(chat_router)
app.include_router(feedback_router)
app.include_router(document_router)
app.include_router(stt_router)
app.include_router(analytics_router)
app.include_router(tts_router)
app.include_router(audio_router)


# mount assets (try both names)
base = Path(__file__).resolve().parents[1]
candidates = [base / "ivf-frontend" / "assets", base / "ivf_frontend" / "assets"]
for p in candidates:
    if p.exists():
        app.mount("/assets", StaticFiles(directory=str(p)), name="assets")
        logger.info(f"Mounted assets: {p}")
        break

@app.get("/")
async def root():
    return {"message": "IVF Medical Chatbot API", "version": "1.0.0", "status": "running", "docs": "/api/docs"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ivf-chatbot-api", "timestamp": "2024-01-01T00:00:00Z"}

@app.get("/ready")
async def readiness_probe():
    rag_engine = getattr(app.state, "rag_engine", None)
    resp = {"faiss_index_loaded": False, "faiss_ntotal": 0, "id_map_size": 0, "db_connected": False}
    try:
        if rag_engine:
            resp["faiss_index_loaded"] = rag_engine.faiss_index is not None
            resp["faiss_ntotal"] = int(getattr(rag_engine.faiss_index, "ntotal", 0)) if rag_engine.faiss_index else 0
            resp["id_map_size"] = len(getattr(rag_engine, "id_map", {}) or {})
            resp["db_connected"] = rag_engine.supabase_client is not None
        else:
            resp["error"] = "rag_engine not initialized"
    except Exception as e:
        resp["error"] = str(e)
    status_code = status.HTTP_200_OK if resp.get("faiss_index_loaded") else status.HTTP_503_SERVICE_UNAVAILABLE
    return JSONResponse(status_code=status_code, content=resp)

@app.on_event("startup")
async def on_startup():
    logger.info("Starting app — initializing RAG engine...")
    try:
        rag = RAGEngine()
        app.state.rag_engine = rag
        logger.info("RAG engine attached to app.state.rag_engine")
    except Exception as e:
        logger.error(f"RAG initialization failed: {e}\n{traceback.format_exc()}")
        app.state.rag_engine = None

@app.on_event("shutdown")
async def on_shutdown():
    logger.info("Shutting down application.")

if __name__ == "__main__":
    uvicorn.run("ivf_backend.main:app", host=settings.API_HOST, port=settings.API_PORT, reload=settings.DEBUG,
                log_level="debug" if settings.DEBUG else "info")

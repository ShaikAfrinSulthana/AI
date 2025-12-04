from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import pytesseract
from PIL import Image
import io
from ivf_backend.services.llm_engine import run_llm_ivf_safe


router = APIRouter(prefix="/files", tags=["files"])

@router.post("/analyze")
async def analyze_file(file: UploadFile = File(...)):
    """Extract text → LLM summarizes → returns SAFE IVF explanation."""
    try:
        content = await file.read()

        # --- Step 1: Extract text (OCR for images / direct for txt/pdf) ---
        text = ""

        if file.filename.endswith((".png", ".jpg", ".jpeg")):
            img = Image.open(io.BytesIO(content))
            text = pytesseract.image_to_string(img)

        elif file.filename.endswith(".txt"):
            text = content.decode("utf-8", errors="ignore")

        else:
            text = "Unable to extract text — unsupported file type."

        if not text.strip():
            raise Exception("No readable text found in the uploaded file.")

        # --- Step 2: Analyze with IVF-Safe LLM ---
        result = run_llm_ivf_safe(
            f"Extracted text from patient document:\n\n{text}\n\n"
            "Explain this document simply. If anything appears serious, tell them to visit their doctor."
        )

        return JSONResponse({"summary": result})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

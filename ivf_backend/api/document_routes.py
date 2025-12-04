import os
import shutil
import tempfile
import logging
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from ..services.document_processor import DocumentProcessor
from ..services.llm_engine import LLMEngine

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/documents", tags=["documents"])

processor = DocumentProcessor()
llm = LLMEngine()


@router.post("/analyze")
async def analyze_document(file: UploadFile = File(...)):
    """
    Upload → extract → IVF relevance check → safe summary.
    If the document is NOT related to IVF → reject it.
    """

    try:
        file_ext = Path(file.filename).suffix.lower()

        # Validate file type
        if file_ext not in processor.supported_formats:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_ext}")

        # Save temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
            shutil.copyfileobj(file.file, tmp)
            temp_path = tmp.name

        # Extract text
        result = processor.process_document(temp_path, file_ext)

        # Cleanup
        try:
            os.remove(temp_path)
        except:
            pass

        if result is None or "error" in result:
            raise HTTPException(status_code=500, detail=result.get("error", "Processing failed"))

        extracted = result.get("extracted_text", "").strip()

        # If extraction failed or empty
        if not extracted:
            return JSONResponse(
                status_code=400,
                content={"error": "Could not extract readable text from this file."}
            )

        # ------------------------------------------------------------
        # IVF RELEVANCE CHECK  (LLM classifier)
        # ------------------------------------------------------------
        relevance_prompt = (
            "You are an IVF content classifier.\n"
            "Read the text below and answer ONLY 'YES' or 'NO'.\n\n"
            "YES = The document is about IVF, fertility, pregnancy, reproductive health, "
            "menstrual cycles, hormones, infertility, ovulation, sperm, embryos, gynaecology, "
            "laparoscopy, ovarian reserve, AMH, semen analysis, reproductive tests.\n\n"
            "NO = Everything else. Financial docs, legal docs, academic papers, software, "
            "general reports, school assignments, novels, textbooks, random content, etc.\n\n"
            f"Document text:\n{extracted}\n\n"
            "Is this document related to IVF?"
        )

        relevance = llm.generate_response(relevance_prompt).strip().lower()

        if not relevance.startswith("yes"):
            # Reject file completely
            return JSONResponse(
                status_code=400,
                content={
                    "error": "This document is not related to IVF or reproductive health.",
                    "relevant": False
                }
            )

        # ------------------------------------------------------------
        # IVF-SAFE EXPLANATION
        # ------------------------------------------------------------
        summary_prompt = (
            "Below is the extracted text from a medical document.\n\n"
            "You MUST follow these rules:\n"
            "- Summarize it as simply as possible.\n"
            "- DO NOT provide any medical advice.\n"
            "- DO NOT diagnose or suggest treatment.\n"
            "- If anything sounds serious, ALWAYS say: 'Please visit your doctor.'\n"
            "- Keep it factual and IVF-safe.\n\n"
            f"Document text:\n{extracted}\n\n"
            "Now provide a short, safe explanation:"
        )

        explanation = llm.generate_response(summary_prompt)

        return JSONResponse(
            status_code=200,
            content={
                "filename": file.filename,
                "extracted_text": extracted,
                "explanation": explanation
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Document analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    return JSONResponse(
        {"message": "Deprecated endpoint. Use /documents/analyze instead."}
    )

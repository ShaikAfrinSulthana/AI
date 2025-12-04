# ivf_backend/services/document_processor.py
import logging
import pandas as pd
from typing import Dict, Any
from pathlib import Path
import PyPDF2

logger = logging.getLogger(__name__)

try:
    import docx  # for Word file reading
except ImportError:
    docx = None


class DocumentProcessor:
    """Process medical documents for IVF chatbot"""

    def __init__(self):
        self.supported_formats = ['.pdf', '.txt', '.doc', '.docx', '.csv']

    def process_document(self, file_path: str, file_ext: str) -> Dict[str, Any]:
        """Route to correct processor"""
        try:
            if file_ext == ".pdf":
                return self._process_pdf(file_path)

            elif file_ext in [".doc", ".docx"]:
                return self._process_word(file_path)

            elif file_ext == ".csv":
                return self._process_csv(file_path)

            elif file_ext == ".txt":
                return self._process_text(file_path)

            else:
                return {"error": f"Unsupported file type: {file_ext}"}

        except Exception as e:
            logger.error(f"Processing error: {e}")
            return {"error": f"Processing failed: {str(e)}"}

    # -------------------- PDF -------------------------
    def _process_pdf(self, file_path: str) -> Dict[str, Any]:
        """Extract text from PDF"""
        try:
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)

                text = ""
                for page in reader.pages:
                    extracted = page.extract_text() or ""
                    text += extracted + "\n"

            return {
                "type": "pdf",
                "page_count": len(reader.pages),
                "extracted_text": text[:3000],
                "summary": f"PDF with {len(reader.pages)} pages processed.",
                "word_count": len(text.split())
            }

        except Exception as e:
            logger.error(f"PDF error: {e}")
            return {"error": "Failed to extract PDF text"}

    # -------------------- WORD -------------------------
    def _process_word(self, file_path: str) -> Dict[str, Any]:
        """Extract text from Word documents"""
        try:
            if docx is None:
                return {"error": "python-docx not installed"}

            d = docx.Document(file_path)
            text = "\n".join([p.text for p in d.paragraphs])

            return {
                "type": "word",
                "word_count": len(text.split()),
                "extracted_text": text[:3000],
                "summary": "Word document processed successfully"
            }

        except Exception as e:
            logger.error(f"Word error: {e}")
            return {"error": "Failed to process Word document"}

    # -------------------- CSV -------------------------
    def _process_csv(self, file_path: str) -> Dict[str, Any]:
        """Extract table structure from CSV"""
        try:
            df = pd.read_csv(file_path)

            return {
                "type": "csv",
                "rows": len(df),
                "columns": list(df.columns),
                "sample_data": df.head(5).to_dict("records"),
                "summary": f"CSV with {len(df)} rows processed"
            }

        except Exception as e:
            logger.error(f"CSV error: {e}")
            return {"error": "Failed to process CSV"}

    # -------------------- TEXT -------------------------
    def _process_text(self, file_path: str) -> Dict[str, Any]:
        """Extract plain text from .txt files"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()

            return {
                "type": "text",
                "word_count": len(text.split()),
                "extracted_text": text[:3000],
                "summary": "Text file processed successfully"
            }

        except Exception as e:
            logger.error(f"Text error: {e}")
            return {"error": "Failed to process text file"}

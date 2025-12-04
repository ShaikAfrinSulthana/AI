from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class DocumentUploadResponse(BaseModel):
    filename: str
    file_type: str
    file_size: int
    processing_result: Dict[str, Any]
    status: str

class DocumentProcessingResult(BaseModel):
    type: str
    word_count: Optional[int] = None
    page_count: Optional[int] = None
    row_count: Optional[int] = None
    column_count: Optional[int] = None
    processing_summary: str
    extracted_text_preview: Optional[str] = None
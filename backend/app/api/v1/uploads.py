"""
Upload endpoint: accepts a dragged/browsed complaint document (PDF, DOCX,
TXT, or EML), extracts its text, and runs it through the AI extraction
node -- this powers the "Drag & drop complaint document here" panel in
the reference UI.
"""
import os
import uuid

from fastapi import APIRouter, Depends, UploadFile

from app.ai.graph import run_ai_task
from app.api.deps import get_current_user
from app.core.config import settings
from app.models.user import User
from app.schemas.ai import ExtractResponse
from app.services.file_parser import extract_text
from app.utils.exceptions import FileProcessingError

router = APIRouter()

MAX_UPLOAD_BYTES = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024


@router.post("/extract", response_model=ExtractResponse)
async def upload_and_extract(
    file: UploadFile,
    current_user: User = Depends(get_current_user),
) -> ExtractResponse:
    file_bytes = await file.read()

    if len(file_bytes) > MAX_UPLOAD_BYTES:
        raise FileProcessingError(
            f"File exceeds the {settings.MAX_UPLOAD_SIZE_MB}MB upload limit."
        )
    if not file_bytes:
        raise FileProcessingError("Uploaded file is empty.")

    raw_text = extract_text(file.filename or "upload", file_bytes)

    # Persist the original file for audit/traceability (referenced later as
    # Complaint.source_document_path when the user saves the complaint).
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    stored_name = f"{uuid.uuid4().hex}_{file.filename}"
    stored_path = os.path.join(settings.UPLOAD_DIR, stored_name)
    with open(stored_path, "wb") as f:
        f.write(file_bytes)

    result = run_ai_task("extract", raw_text=raw_text)

    return ExtractResponse(
        fields=result.get("extracted_fields", {}),
        confidence=result.get("extraction_confidence", {}),
        raw_text_preview=raw_text[:500],
        source_document_path=stored_path,
    )

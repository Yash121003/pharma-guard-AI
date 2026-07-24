"""
Pydantic schemas for the /ai/* endpoints.
"""
from typing import Any

from pydantic import BaseModel, Field


class ExtractTextRequest(BaseModel):
    """For the 'paste complaint text' path (as opposed to file upload)."""

    text: str = Field(min_length=1)


class ExtractResponse(BaseModel):
    fields: dict[str, Any]
    confidence: dict[str, float] = Field(default_factory=dict)
    raw_text_preview: str
    source_document_path: str | None = None


class ChatRequest(BaseModel):
    complaint_id: int
    question: str = Field(min_length=1)


class ChatResponse(BaseModel):
    answer: str


class SummaryResponse(BaseModel):
    summary: str


class RootCauseResponse(BaseModel):
    root_cause: str


class CapaResponse(BaseModel):
    capa_recommendation: str


class RiskResponse(BaseModel):
    risk_level: str
    reasoning: str


class DuplicateCheckResponse(BaseModel):
    is_duplicate: bool
    duplicate_of_id: int | None
    reasoning: str


class CompletenessResponse(BaseModel):
    completeness_score: float
    completeness_notes: str
    missing_fields: list[str]

"""
AI endpoints:
  - /extract-text  : paste-complaint-text alternative to file upload
  - /chat           : the AI Complaint Intake Assistant Q&A panel
  - /summarize/root-cause/capa/risk/duplicate-check/completeness/{id} :
    each runs the corresponding LangGraph task against a saved complaint
    and persists the result onto that Complaint row.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.ai.graph import run_ai_task
from app.api.deps import get_current_user, get_db
from app.models.ai_conversation import AIConversation, MessageRole
from app.models.complaint import Complaint
from app.models.user import User
from app.schemas.ai import (
    CapaResponse,
    ChatRequest,
    ChatResponse,
    CompletenessResponse,
    DuplicateCheckResponse,
    ExtractResponse,
    ExtractTextRequest,
    RiskResponse,
    RootCauseResponse,
    SummaryResponse,
)
from app.services.complaint_service import complaint_to_ai_dict, get_complaint_or_404

router = APIRouter()


@router.post("/extract-text", response_model=ExtractResponse)
def extract_from_text(
    payload: ExtractTextRequest,
    current_user: User = Depends(get_current_user),
) -> ExtractResponse:
    result = run_ai_task("extract", raw_text=payload.text)
    return ExtractResponse(
        fields=result.get("extracted_fields", {}),
        confidence=result.get("extraction_confidence", {}),
        raw_text_preview=payload.text[:500],
    )


@router.post("/chat", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChatResponse:
    complaint = get_complaint_or_404(db, payload.complaint_id)

    history = [
        {"role": c.role.value, "message": c.message}
        for c in sorted(complaint.conversations, key=lambda c: c.created_at)
    ]

    result = run_ai_task(
        "qa",
        question=payload.question,
        complaint_data=complaint_to_ai_dict(complaint),
        conversation_history=history,
    )
    answer = result.get("answer", "")

    db.add(AIConversation(complaint_id=complaint.id, role=MessageRole.USER, message=payload.question))
    db.add(
        AIConversation(
            complaint_id=complaint.id, role=MessageRole.ASSISTANT, message=answer, tool_used="qa"
        )
    )
    db.commit()

    return ChatResponse(answer=answer)


def _get_complaint(db: Session, complaint_id: int) -> Complaint:
    return get_complaint_or_404(db, complaint_id)


@router.post("/summarize/{complaint_id}", response_model=SummaryResponse)
def summarize(complaint_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> SummaryResponse:
    complaint = _get_complaint(db, complaint_id)
    result = run_ai_task("summarize", complaint_data=complaint_to_ai_dict(complaint))
    complaint.ai_summary = result["summary"]
    db.commit()
    return SummaryResponse(summary=result["summary"])


@router.post("/root-cause/{complaint_id}", response_model=RootCauseResponse)
def root_cause(complaint_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> RootCauseResponse:
    complaint = _get_complaint(db, complaint_id)
    result = run_ai_task("root_cause", complaint_data=complaint_to_ai_dict(complaint))
    complaint.ai_root_cause = result["root_cause"]
    db.commit()
    return RootCauseResponse(root_cause=result["root_cause"])


@router.post("/capa/{complaint_id}", response_model=CapaResponse)
def capa(complaint_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> CapaResponse:
    complaint = _get_complaint(db, complaint_id)
    # Chain off the existing root cause if we already have one -- gives a more grounded CAPA.
    result = run_ai_task(
        "capa", complaint_data=complaint_to_ai_dict(complaint), root_cause=complaint.ai_root_cause or ""
    )
    complaint.ai_capa_recommendation = result["capa_recommendation"]
    db.commit()
    return CapaResponse(capa_recommendation=result["capa_recommendation"])


@router.post("/risk/{complaint_id}", response_model=RiskResponse)
def risk(complaint_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> RiskResponse:
    complaint = _get_complaint(db, complaint_id)
    result = run_ai_task("risk", complaint_data=complaint_to_ai_dict(complaint))
    complaint.ai_risk_level = result["risk_level"]
    db.commit()
    return RiskResponse(risk_level=result["risk_level"], reasoning=result["risk_reasoning"])


@router.post("/duplicate-check/{complaint_id}", response_model=DuplicateCheckResponse)
def duplicate_check(complaint_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> DuplicateCheckResponse:
    complaint = _get_complaint(db, complaint_id)

    candidates = (
        db.query(Complaint)
        .filter(Complaint.id != complaint.id, Complaint.product_id == complaint.product_id)
        .filter(Complaint.product_id.isnot(None))
        .limit(20)
        .all()
    )
    other_complaints = [
        {
            "id": c.id,
            "product_name": c.product.name if c.product else c.product_name_raw,
            "batch_number": c.batch.batch_number if c.batch else c.batch_number_raw,
            "description": c.description,
        }
        for c in candidates
    ]

    result = run_ai_task(
        "duplicate", complaint_data=complaint_to_ai_dict(complaint), other_complaints=other_complaints
    )
    complaint.is_duplicate_of_id = result.get("duplicate_of_id")
    db.commit()

    return DuplicateCheckResponse(
        is_duplicate=result["is_duplicate"],
        duplicate_of_id=result.get("duplicate_of_id"),
        reasoning=result["duplicate_reasoning"],
    )


@router.post("/completeness/{complaint_id}", response_model=CompletenessResponse)
def completeness(complaint_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> CompletenessResponse:
    complaint = _get_complaint(db, complaint_id)
    result = run_ai_task("completeness", complaint_data=complaint_to_ai_dict(complaint))
    complaint.ai_completeness_score = result["completeness_score"]
    complaint.ai_completeness_notes = result["completeness_notes"]
    db.commit()
    return CompletenessResponse(
        completeness_score=result["completeness_score"],
        completeness_notes=result["completeness_notes"],
        missing_fields=result["missing_fields"],
    )

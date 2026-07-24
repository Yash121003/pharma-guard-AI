"""
Shared state passed between LangGraph nodes for the complaint AI workflow.

`task` selects which node the router sends the state to; each node reads
only the inputs it needs and writes only the outputs it owns, so the same
state object can flow through any of the AI features.
"""
from typing import Any, Literal, TypedDict

TaskName = Literal[
    "extract",
    "qa",
    "summarize",
    "root_cause",
    "capa",
    "risk",
    "duplicate",
    "completeness",
]


class ComplaintGraphState(TypedDict, total=False):
    # --- routing ---
    task: TaskName

    # --- inputs (populated by the caller before invoking the graph) ---
    raw_text: str  # document text or pasted complaint text (for extract)
    question: str  # user's question (for qa)
    complaint_data: dict[str, Any]  # current form/complaint field values
    other_complaints: list[dict[str, Any]]  # candidate complaints for duplicate check
    conversation_history: list[dict[str, str]]  # prior chat turns [{role, message}, ...]

    # --- outputs (populated by nodes) ---
    extracted_fields: dict[str, Any]
    extraction_confidence: dict[str, float]
    answer: str
    summary: str
    root_cause: str
    capa_recommendation: str
    risk_level: str
    risk_reasoning: str
    is_duplicate: bool
    duplicate_of_id: int | None
    duplicate_reasoning: str
    completeness_score: float
    completeness_notes: str
    missing_fields: list[str]

    error: str

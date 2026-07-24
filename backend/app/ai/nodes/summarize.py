"""
Summarize node: produces a concise, QA-reviewer-friendly summary of a
complaint.
"""
from app.ai.llm_client import call_llm
from app.ai.state import ComplaintGraphState

SYSTEM_PROMPT = """You are a pharmaceutical QMS assistant. Summarize the complaint below \
in 3-4 sentences for a QA reviewer: what happened, which product/batch is involved, \
and why it matters. Be factual and neutral -- do not speculate about cause or fault."""


def summarize_node(state: ComplaintGraphState) -> ComplaintGraphState:
    complaint_data = state.get("complaint_data", {})
    summary = call_llm(SYSTEM_PROMPT, f"Complaint data:\n{complaint_data}", temperature=0.2)
    return {**state, "summary": summary}

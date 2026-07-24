"""
CAPA node: drafts a preliminary Corrective and Preventive Action
recommendation for QA review.
"""
from app.ai.llm_client import call_llm
from app.ai.state import ComplaintGraphState

SYSTEM_PROMPT = """You are a pharmaceutical QMS assistant. Draft a preliminary CAPA \
(Corrective and Preventive Action) recommendation for the complaint below. Structure \
your answer as:
Corrective Action: <immediate action to address this specific instance>
Preventive Action: <systemic change to prevent recurrence>
This is a draft for QA review, not an approved CAPA -- keep each section to 1-2 sentences."""


def capa_node(state: ComplaintGraphState) -> ComplaintGraphState:
    complaint_data = state.get("complaint_data", {})
    root_cause = state.get("root_cause", "")
    context = f"Complaint data:\n{complaint_data}"
    if root_cause:
        context += f"\n\nSuggested root cause:\n{root_cause}"

    capa = call_llm(SYSTEM_PROMPT, context, temperature=0.3)
    return {**state, "capa_recommendation": capa}

"""
Risk node: predicts an overall risk level for the complaint (distinct from
the human-entered "initial severity" -- this is the AI's independent
assessment, useful as a cross-check).
"""
from app.ai.llm_client import call_llm_json
from app.ai.state import ComplaintGraphState

SYSTEM_PROMPT = """You are a pharmaceutical QMS risk assessor. Evaluate the complaint \
below and predict an overall risk level considering patient safety impact, product \
quality impact, and regulatory exposure. Return JSON:
{"risk_level": "low"|"medium"|"high"|"critical", "reasoning": "<2-3 sentence explanation>"}"""


def risk_node(state: ComplaintGraphState) -> ComplaintGraphState:
    complaint_data = state.get("complaint_data", {})
    result = call_llm_json(SYSTEM_PROMPT, f"Complaint data:\n{complaint_data}")
    return {
        **state,
        "risk_level": result.get("risk_level", "medium"),
        "risk_reasoning": result.get("reasoning", ""),
    }

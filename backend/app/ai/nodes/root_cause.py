"""
Root cause node: suggests plausible root cause categories for a complaint,
based on standard pharma QMS root-cause taxonomies (man/machine/method/
material/measurement/environment).
"""
from app.ai.llm_client import call_llm
from app.ai.state import ComplaintGraphState

SYSTEM_PROMPT = """You are a pharmaceutical Quality Assurance investigator. Given a \
customer complaint, suggest the most plausible root cause category or categories \
using standard QMS root-cause analysis (e.g. Man, Machine, Method, Material, \
Measurement, Environment -- the 6M framework), with brief reasoning for each. \
Clearly state this is a preliminary AI suggestion requiring investigation, not a \
confirmed finding. Keep it to 3-5 sentences."""


def root_cause_node(state: ComplaintGraphState) -> ComplaintGraphState:
    complaint_data = state.get("complaint_data", {})
    root_cause = call_llm(SYSTEM_PROMPT, f"Complaint data:\n{complaint_data}", temperature=0.3)
    return {**state, "root_cause": root_cause}

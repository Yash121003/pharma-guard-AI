"""
Completeness node: checks whether a complaint has all fields required to
proceed past triage. Deliberately deterministic (no LLM call) -- for a
compliance checklist like this, a rule-based check is more reliable and
auditable than an LLM judgment, and it's instant/free to run.
"""
from app.ai.state import ComplaintGraphState

REQUIRED_FIELDS = [
    "complaint_source",
    "customer_name",
    "product_name",
    "batch_number",
    "complaint_type",
    "complaint_date",
    "description",
    "initial_severity",
    "priority",
]

RECOMMENDED_FIELDS = [
    "strength",
    "manufacturing_date",
    "expiry_date",
    "quantity_affected",
]


def completeness_node(state: ComplaintGraphState) -> ComplaintGraphState:
    complaint_data = state.get("complaint_data", {})

    missing_required = [f for f in REQUIRED_FIELDS if not complaint_data.get(f)]
    missing_recommended = [f for f in RECOMMENDED_FIELDS if not complaint_data.get(f)]

    total_checked = len(REQUIRED_FIELDS) + len(RECOMMENDED_FIELDS)
    present = total_checked - len(missing_required) - len(missing_recommended)
    score = round((present / total_checked) * 100, 2) if total_checked else 0.0

    notes_parts = []
    if missing_required:
        notes_parts.append(f"Missing required fields: {', '.join(missing_required)}.")
    if missing_recommended:
        notes_parts.append(f"Missing recommended fields: {', '.join(missing_recommended)}.")
    if not notes_parts:
        notes_parts.append("All required and recommended fields are present.")

    description = (complaint_data.get("description") or "").strip()
    if description and len(description) < 20:
        notes_parts.append("Description is very short -- consider requesting more detail from the customer.")

    return {
        **state,
        "completeness_score": score,
        "completeness_notes": " ".join(notes_parts),
        "missing_fields": missing_required + missing_recommended,
    }

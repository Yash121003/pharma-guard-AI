"""
Extraction node: reads raw document/pasted text and populates the
structured complaint fields shown in the intake form.
"""
from app.ai.llm_client import call_llm_json
from app.ai.state import ComplaintGraphState

SYSTEM_PROMPT = """You are a pharmaceutical Quality Management System (QMS) assistant. \
Your job is to read a customer complaint document (email, letter, or form) and extract \
structured data for the complaint intake form.

Extract these fields (use null if a field is genuinely not present in the text -- \
never invent data):
- complaint_source: one of "phone", "email", "portal", "letter", "sales_rep", "other"
- customer_name: string
- product_name: string
- strength: string (e.g. "500mg")
- batch_number: string
- manufacturing_date: string in YYYY-MM-DD format, or null
- expiry_date: string in YYYY-MM-DD format, or null
- quantity_affected: number, or null
- quantity_unit: string (e.g. "kg", "units", "strips"), or null
- complaint_type: one of "efficacy", "packaging_defect", "contamination", \
"adverse_event", "labeling_error", "physical_defect", "other"
- complaint_date: string in YYYY-MM-DD format
- description: string, a clear rewritten summary of what the customer reported
- initial_severity: one of "low", "medium", "high", "critical"
- priority: one of "low", "medium", "high", "urgent"

Return a JSON object with exactly two top-level keys:
{
  "fields": { ...the fields above... },
  "confidence": { "<field_name>": <0.0-1.0 confidence score>, ... }
}
"""


def extract_node(state: ComplaintGraphState) -> ComplaintGraphState:
    raw_text = state.get("raw_text", "").strip()
    if not raw_text:
        return {**state, "extracted_fields": {}, "extraction_confidence": {}, "error": "No text provided."}

    result = call_llm_json(SYSTEM_PROMPT, f"Complaint document:\n\n{raw_text}")

    fields = result.get("fields", {})
    confidence = result.get("confidence", {})

    return {**state, "extracted_fields": fields, "extraction_confidence": confidence}

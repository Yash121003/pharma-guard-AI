"""
Deterministic mock responses used when AI_MOCK_MODE=true. Lets the whole
AI workflow (and the frontend built against it) be exercised end-to-end
without a Groq API key or network access -- useful for local dev, demos,
and CI.

Responses are picked by looking for a few keywords in the system prompt,
which is reliable here since each node in app/ai/nodes/ has a distinct,
fixed system prompt.
"""
import random
from datetime import date, timedelta


def mock_call_llm(system_prompt: str, user_prompt: str) -> str:
    prompt_lower = system_prompt.lower()

    if "answer the user's question" in prompt_lower:
        return (
            "[MOCK RESPONSE] Based on the complaint data provided, I can see this involves a "
            "packaging/quality issue that's currently pending triage. For a definitive answer "
            "I'd recommend reviewing the full complaint record. (This is a mock AI response -- "
            "set AI_MOCK_MODE=false with a real GROQ_API_KEY for live answers.)"
        )
    if "summarize the complaint" in prompt_lower:
        return (
            "[MOCK RESPONSE] This complaint reports a quality issue with the named product and "
            "batch, raised by the customer and currently under initial review. The issue appears "
            "isolated to a portion of the affected quantity and has been logged for QA "
            "investigation. No adverse patient impact has been confirmed at this stage."
        )
    if "root cause" in prompt_lower or "6m framework" in prompt_lower:
        return (
            "[MOCK RESPONSE] Preliminary root cause suggestion (Method/Machine category): the "
            "described defect pattern is consistent with a packaging-line sealing or handling "
            "issue rather than a formulation problem. Investigation should verify line "
            "calibration logs and in-process quality checks for the affected batch. This is a "
            "preliminary AI suggestion requiring investigation, not a confirmed finding."
        )
    if "capa" in prompt_lower or "corrective and preventive" in prompt_lower:
        return (
            "[MOCK RESPONSE]\nCorrective Action: Quarantine and inspect remaining stock from the "
            "affected batch; issue a replacement to the customer.\n"
            "Preventive Action: Review and, if needed, recalibrate the relevant packaging line "
            "step, and add an in-process spot-check for this defect type."
        )

    return "[MOCK RESPONSE] This is a placeholder AI response generated because AI_MOCK_MODE is enabled."


def mock_call_llm_json(system_prompt: str, user_prompt: str) -> dict:
    prompt_lower = system_prompt.lower()

    if "fields" in prompt_lower and "confidence" in prompt_lower:
        today = date.today()
        return {
            "fields": {
                "complaint_source": "email",
                "customer_name": "Mock Customer Pharmacy",
                "product_name": "Mock Product 500mg",
                "strength": "500mg",
                "batch_number": f"MOCK-{today.year}-0001",
                "manufacturing_date": str(today - timedelta(days=180)),
                "expiry_date": str(today + timedelta(days=545)),
                "quantity_affected": 5.0,
                "quantity_unit": "kg",
                "complaint_type": "packaging_defect",
                "complaint_date": str(today),
                "description": (
                    "[MOCK EXTRACTION] Sample extracted description -- enable a real GROQ_API_KEY "
                    "and set AI_MOCK_MODE=false to extract actual fields from the uploaded document."
                ),
                "initial_severity": "medium",
                "priority": "medium",
            },
            "confidence": {
                "customer_name": 0.5,
                "product_name": 0.5,
                "batch_number": 0.5,
                "description": 0.3,
            },
        }

    if "risk_level" in prompt_lower:
        risk_level = random.choice(["low", "medium", "high"])
        return {
            "risk_level": risk_level,
            "reasoning": f"[MOCK RESPONSE] Assessed as {risk_level} risk based on complaint type and severity.",
        }

    if "is_duplicate" in prompt_lower:
        return {
            "is_duplicate": False,
            "duplicate_of_id": None,
            "reasoning": "[MOCK RESPONSE] No strong match found among shortlisted candidates.",
        }

    return {"mock": True, "note": "Unrecognized prompt type for mock JSON response."}

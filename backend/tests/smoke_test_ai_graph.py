"""
Phase 5 smoke test for the AI graph.

IMPORTANT: api.groq.com is not reachable from this sandbox's network
egress (only pypi/npm/github/etc are allowlisted), so this test monkey-
patches app.ai.llm_client.call_llm / call_llm_json to verify:
  1. every task routes to the correct node,
  2. each node reads/writes the state fields it's supposed to,
  3. JSON-returning nodes parse the (mocked) LLM output correctly.

It does NOT verify real Groq connectivity or real model output quality --
that requires a live GROQ_API_KEY and network access (e.g. run this same
graph from Claude Code, or in the real deployment environment).

Run with:  python -m tests.smoke_test_ai_graph
"""
import json
from unittest.mock import patch

from app.ai.graph import run_ai_task

SAMPLE_COMPLAINT = {
    "complaint_source": "email",
    "customer_name": "MedPlus Pharmacy",
    "product_name": "Paracetamol",
    "batch_number": "PCM-2026-0417",
    "complaint_type": "packaging_defect",
    "complaint_date": "2026-07-20",
    "description": "Blister packaging seal was broken on 3 strips within the received carton.",
    "initial_severity": "medium",
    "priority": "high",
}

SAMPLE_DOCUMENT_TEXT = """
From: complaints@medplus.example
Subject: Damaged packaging - Paracetamol 500mg

We received a shipment of Paracetamol 500mg (Batch PCM-2026-0417, mfg 2026-01-10,
exp 2028-01-10) on 2026-07-20. Three blister strips out of the carton had broken
seals, affecting approximately 0.5 kg of stock. Please advise on replacement.

Customer: MedPlus Pharmacy
"""


def fake_call_llm(system_prompt, user_prompt, model=None, temperature=0.2):
    return "This is a mocked free-text LLM response used for offline testing."


def fake_call_llm_json(system_prompt, user_prompt, model=None, temperature=0.0):
    # Return a shape appropriate to whichever node is calling, inferred from prompt content.
    if "extract" in system_prompt.lower() and "fields" in system_prompt.lower():
        return {
            "fields": {
                "complaint_source": "email",
                "customer_name": "MedPlus Pharmacy",
                "product_name": "Paracetamol",
                "strength": "500mg",
                "batch_number": "PCM-2026-0417",
                "manufacturing_date": "2026-01-10",
                "expiry_date": "2028-01-10",
                "quantity_affected": 0.5,
                "quantity_unit": "kg",
                "complaint_type": "packaging_defect",
                "complaint_date": "2026-07-20",
                "description": "Three blister strips had broken seals.",
                "initial_severity": "medium",
                "priority": "high",
            },
            "confidence": {"customer_name": 0.95, "batch_number": 0.9},
        }
    if "risk" in system_prompt.lower():
        return {"risk_level": "high", "reasoning": "Packaging integrity failure poses contamination risk."}
    if "duplicate" in system_prompt.lower():
        return {"is_duplicate": True, "duplicate_of_id": 7, "reasoning": "Same customer, batch, and defect type."}
    raise AssertionError(f"Unexpected JSON call for prompt: {system_prompt[:80]}")


def run() -> None:
    with (
        patch("app.ai.nodes.extract.call_llm_json", side_effect=fake_call_llm_json),
        patch("app.ai.nodes.risk.call_llm_json", side_effect=fake_call_llm_json),
        patch("app.ai.nodes.duplicate.call_llm_json", side_effect=fake_call_llm_json),
        patch("app.ai.nodes.qa.call_llm", side_effect=fake_call_llm),
        patch("app.ai.nodes.summarize.call_llm", side_effect=fake_call_llm),
        patch("app.ai.nodes.root_cause.call_llm", side_effect=fake_call_llm),
        patch("app.ai.nodes.capa.call_llm", side_effect=fake_call_llm),
    ):
        # 1. extract
        r = run_ai_task("extract", raw_text=SAMPLE_DOCUMENT_TEXT)
        assert r["extracted_fields"]["batch_number"] == "PCM-2026-0417"
        assert r["extraction_confidence"]["customer_name"] == 0.95
        print("[OK] extract:", json.dumps(r["extracted_fields"], indent=None)[:100], "...")

        # 2. qa
        r = run_ai_task(
            "qa",
            question="What batch is affected?",
            complaint_data=SAMPLE_COMPLAINT,
            conversation_history=[{"role": "user", "message": "hi"}],
        )
        assert r["answer"]
        print("[OK] qa:", r["answer"][:60])

        # 3. summarize
        r = run_ai_task("summarize", complaint_data=SAMPLE_COMPLAINT)
        assert r["summary"]
        print("[OK] summarize:", r["summary"][:60])

        # 4. root_cause
        r = run_ai_task("root_cause", complaint_data=SAMPLE_COMPLAINT)
        assert r["root_cause"]
        print("[OK] root_cause:", r["root_cause"][:60])

        # 5. capa (chained after root_cause, as the API layer will do)
        r = run_ai_task("capa", complaint_data=SAMPLE_COMPLAINT, root_cause=r["root_cause"])
        assert r["capa_recommendation"]
        print("[OK] capa:", r["capa_recommendation"][:60])

        # 6. risk
        r = run_ai_task("risk", complaint_data=SAMPLE_COMPLAINT)
        assert r["risk_level"] == "high"
        print("[OK] risk:", r["risk_level"], "-", r["risk_reasoning"][:60])

        # 7. duplicate (with a shortlisted candidate so the LLM path actually runs)
        r = run_ai_task(
            "duplicate",
            complaint_data={"product_name": "Paracetamol", "batch_number": "PCM-2026-0417"},
            other_complaints=[
                {"id": 7, "product_name": "Paracetamol", "batch_number": "PCM-2026-0417", "description": "same"}
            ],
        )
        assert r["is_duplicate"] is True
        assert r["duplicate_of_id"] == 7
        print("[OK] duplicate:", r["is_duplicate"], r["duplicate_of_id"])

        # 8. completeness (real, deterministic, no mocking needed)
        r = run_ai_task("completeness", complaint_data=SAMPLE_COMPLAINT)
        print("[OK] completeness:", r["completeness_score"], "-", r["completeness_notes"][:60])

    print("\nAll 8 AI graph tasks routed and executed correctly (LLM calls mocked).")


if __name__ == "__main__":
    run()

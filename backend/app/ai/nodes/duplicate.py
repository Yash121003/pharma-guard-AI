"""
Duplicate detection node: flags whether a complaint appears to be a
duplicate of an existing one.

Uses a cheap heuristic pre-filter (same product/batch) before spending an
LLM call, and skips the LLM entirely if there are no plausible candidates
-- keeps this fast and avoids unnecessary API usage.
"""
from app.ai.llm_client import call_llm_json
from app.ai.state import ComplaintGraphState

SYSTEM_PROMPT = """You are a pharmaceutical QMS assistant checking for duplicate \
complaints. You will be given a new complaint and a shortlist of existing complaints \
for the same product/batch. Decide if the new complaint is very likely describing the \
same underlying issue as one of the existing ones (same customer, same defect \
description, same timeframe), not just the same product.

Return JSON:
{"is_duplicate": true|false, "duplicate_of_id": <id or null>, "reasoning": "<1-2 sentences>"}"""


def _shortlist_candidates(complaint_data: dict, other_complaints: list[dict]) -> list[dict]:
    product = (complaint_data.get("product_name") or "").strip().lower()
    batch = (complaint_data.get("batch_number") or "").strip().lower()

    candidates = []
    for c in other_complaints:
        c_product = (c.get("product_name") or "").strip().lower()
        c_batch = (c.get("batch_number") or "").strip().lower()
        if product and product == c_product and batch and batch == c_batch:
            candidates.append(c)
    return candidates


def duplicate_node(state: ComplaintGraphState) -> ComplaintGraphState:
    complaint_data = state.get("complaint_data", {})
    other_complaints = state.get("other_complaints", [])

    candidates = _shortlist_candidates(complaint_data, other_complaints)
    if not candidates:
        return {
            **state,
            "is_duplicate": False,
            "duplicate_of_id": None,
            "duplicate_reasoning": "No existing complaints share the same product and batch.",
        }

    user_prompt = f"New complaint:\n{complaint_data}\n\nExisting complaints for same product/batch:\n{candidates}"
    result = call_llm_json(SYSTEM_PROMPT, user_prompt)

    return {
        **state,
        "is_duplicate": bool(result.get("is_duplicate", False)),
        "duplicate_of_id": result.get("duplicate_of_id"),
        "duplicate_reasoning": result.get("reasoning", ""),
    }

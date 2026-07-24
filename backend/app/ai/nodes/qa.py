"""
QA node: answers free-form questions about a complaint, using the current
complaint data and prior conversation turns as context (the right-hand
chat panel in the reference UI).
"""
from app.ai.llm_client import call_llm
from app.ai.state import ComplaintGraphState

SYSTEM_PROMPT = """You are the AI Complaint Intake Assistant for a pharmaceutical QMS. \
Answer the user's question about the complaint using only the complaint data provided. \
If the answer isn't in the data, say so plainly rather than guessing. \
Keep answers concise (2-4 sentences unless the question needs more detail). \
Remind the user to verify AI-generated information when it matters for a regulatory decision."""


def qa_node(state: ComplaintGraphState) -> ComplaintGraphState:
    question = state.get("question", "").strip()
    complaint_data = state.get("complaint_data", {})
    history = state.get("conversation_history", [])

    if not question:
        return {**state, "answer": "", "error": "No question provided."}

    history_text = "\n".join(f"{turn['role']}: {turn['message']}" for turn in history[-6:])
    user_prompt = (
        f"Complaint data:\n{complaint_data}\n\n"
        f"Recent conversation:\n{history_text}\n\n"
        f"User question: {question}"
    )

    answer = call_llm(SYSTEM_PROMPT, user_prompt, temperature=0.3)
    return {**state, "answer": answer}

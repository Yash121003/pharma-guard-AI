"""
Thin wrapper around langchain-groq's ChatGroq, giving the rest of the
codebase two simple entry points: call_llm() for free text and
call_llm_json() for structured JSON output. Centralizing this here means
swapping models/providers later only touches one file.

Also handles AI_MOCK_MODE: when enabled, both functions return
deterministic mock output (see app/ai/mock_responses.py) instead of
calling Groq at all -- no network call is made and no API key is
required in this mode.
"""
import json
import logging
import re

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from app.ai.mock_responses import mock_call_llm, mock_call_llm_json
from app.core.config import settings
from app.utils.exceptions import AIProcessingError

logger = logging.getLogger(__name__)

_client_cache: dict[str, ChatGroq] = {}


def get_llm(model: str | None = None, temperature: float = 0.2) -> ChatGroq:
    """Returns a cached ChatGroq client for the given model.
    Raises AIProcessingError with a clear message if no API key is
    configured -- callers should not call this while AI_MOCK_MODE is on."""
    model_name = model or settings.GROQ_MODEL_DEFAULT
    cache_key = f"{model_name}:{temperature}"
    if cache_key not in _client_cache:
        if not settings.GROQ_API_KEY:
            raise AIProcessingError(
                "GROQ_API_KEY is not configured. Set it in your .env file, or set "
                "AI_MOCK_MODE=true to use mock AI responses without a key."
            )
        _client_cache[cache_key] = ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model=model_name,
            temperature=temperature,
        )
    return _client_cache[cache_key]


def call_llm(system_prompt: str, user_prompt: str, model: str | None = None, temperature: float = 0.2) -> str:
    """Sends a system+user prompt to Groq and returns the raw text response.
    Returns a mock response instead if AI_MOCK_MODE is enabled."""
    if settings.AI_MOCK_MODE:
        logger.debug("AI_MOCK_MODE enabled -- returning mock text response instead of calling Groq.")
        return mock_call_llm(system_prompt, user_prompt)

    llm = get_llm(model=model, temperature=temperature)
    try:
        response = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)])
    except Exception as exc:  # network/auth/rate-limit errors from the Groq SDK
        logger.exception("Groq call failed")
        raise AIProcessingError(f"AI request failed: {exc}") from exc
    return response.content


def _strip_json_fences(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def call_llm_json(
    system_prompt: str, user_prompt: str, model: str | None = None, temperature: float = 0.0
) -> dict:
    """
    Calls the LLM with an instruction to return ONLY JSON, then parses it.
    Returns a mock response instead if AI_MOCK_MODE is enabled.
    Raises AIProcessingError if the model doesn't return valid JSON.
    """
    if settings.AI_MOCK_MODE:
        logger.debug("AI_MOCK_MODE enabled -- returning mock JSON response instead of calling Groq.")
        return mock_call_llm_json(system_prompt, user_prompt)

    strict_system = (
        system_prompt
        + "\n\nCRITICAL: Respond with ONLY a valid JSON object. No markdown fences, "
        "no preamble, no explanation, no trailing text -- just the JSON object."
    )
    raw = call_llm(strict_system, user_prompt, model=model, temperature=temperature)
    cleaned = _strip_json_fences(raw)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as exc:
        logger.error("Failed to parse LLM JSON output: %s", raw[:500])
        raise AIProcessingError(f"AI returned malformed JSON: {exc}") from exc

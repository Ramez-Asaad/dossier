"""LLM call dispatcher: routes to whichever provider is configured.

Agents call `llm.call_json(...)` through the module (not a direct imported
name) so tests can monkeypatch `app.llm.call_json` without needing a live
API key or provider. See backend/tests/test_graph.py.

Provider selection: `LLM_PROVIDER` env var ("anthropic" or "groq") if set,
otherwise inferred from whichever API key is present (GROQ_API_KEY wins if
both are set). Groq is served through its OpenAI-compatible endpoint, so
this needs no separate Groq SDK, just the `openai` package pointed at a
different base_url.

This is a minimal single-model-per-provider version: one default model per
provider, not yet the per-agent routing (cheap model for extraction, strong
model for the Project Architect) from the accepted multi-provider plan.
That per-agent table is still future work.
"""

import json
import os
import time

from anthropic import Anthropic
from anthropic import RateLimitError as AnthropicRateLimitError
from openai import BadRequestError as GroqBadRequestError
from openai import OpenAI
from openai import RateLimitError as GroqRateLimitError

JSON_ONLY_INSTRUCTION = (
    "Respond with a single JSON object and nothing else. "
    "No prose, no markdown code fences, no explanation."
)

MAX_RATE_LIMIT_RETRIES = 5
RATE_LIMIT_BASE_DELAY_SECONDS = 2.0

GROQ_BASE_URL = "https://api.groq.com/openai/v1"

# gpt-oss models on Groq spend hidden reasoning tokens before emitting the
# actual JSON response, counted against the same max_tokens budget, and the
# amount of hidden reasoning varies call to call, so no fixed floor is ever
# fully safe. A tight budget sized for Claude's output-only token count
# (e.g. Validator's 256) gets the response truncated to nothing and Groq's
# json_validate_failed error. Handled two ways: a generous starting floor to
# make it rare, and an escalate-and-retry path below to make it recoverable
# when it happens anyway. Both are a provider quirk, not an agent one, so
# they live here rather than in every agent's max_tokens.
GROQ_MIN_MAX_TOKENS = 1024
GROQ_MAX_MAX_TOKENS = 4096

_PROVIDER_DEFAULT_MODEL = {
    "anthropic": "claude-sonnet-5",
    "groq": "openai/gpt-oss-120b",
}

_anthropic_client: Anthropic | None = None
_groq_client: OpenAI | None = None


def _resolve_provider() -> str:
    provider = os.environ.get("LLM_PROVIDER")
    if provider:
        return provider
    if os.environ.get("GROQ_API_KEY"):
        return "groq"
    return "anthropic"


def _default_model_for(provider: str) -> str:
    return os.environ.get("EVIDENCE_ENGINE_MODEL") or _PROVIDER_DEFAULT_MODEL.get(provider, "claude-sonnet-5")


def _get_anthropic_client() -> Anthropic:
    global _anthropic_client
    if _anthropic_client is None:
        _anthropic_client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _anthropic_client


def _get_groq_client() -> OpenAI:
    global _groq_client
    if _groq_client is None:
        _groq_client = OpenAI(api_key=os.environ["GROQ_API_KEY"], base_url=GROQ_BASE_URL)
    return _groq_client


def call_json(system: str, user: str, model: str | None = None, max_tokens: int = 2048) -> dict:
    provider = _resolve_provider()
    resolved_model = model or _default_model_for(provider)

    if provider == "groq":
        return _call_groq(system, user, resolved_model, max_tokens)
    if provider == "anthropic":
        return _call_anthropic(system, user, resolved_model, max_tokens)
    raise RuntimeError(f"Unknown LLM_PROVIDER: {provider!r}. Expected 'anthropic' or 'groq'.")


def _retry_on_rate_limit(make_request, rate_limit_exception):
    delay = RATE_LIMIT_BASE_DELAY_SECONDS
    for attempt in range(MAX_RATE_LIMIT_RETRIES):
        try:
            return make_request()
        except rate_limit_exception:
            if attempt == MAX_RATE_LIMIT_RETRIES - 1:
                raise
            time.sleep(delay)
            delay *= 2


def _call_anthropic(system: str, user: str, model: str, max_tokens: int) -> dict:
    client = _get_anthropic_client()

    def make_request():
        return client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=f"{system}\n\n{JSON_ONLY_INSTRUCTION}",
            messages=[{"role": "user", "content": user}],
        )

    response = _retry_on_rate_limit(make_request, AnthropicRateLimitError)
    text = "".join(block.text for block in response.content if block.type == "text")
    return json.loads(text)


def _call_groq(system: str, user: str, model: str, max_tokens: int) -> dict:
    client = _get_groq_client()
    current_max_tokens = max(max_tokens, GROQ_MIN_MAX_TOKENS)
    delay = RATE_LIMIT_BASE_DELAY_SECONDS

    for attempt in range(MAX_RATE_LIMIT_RETRIES):
        try:
            response = client.chat.completions.create(
                model=model,
                max_tokens=current_max_tokens,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": f"{system}\n\n{JSON_ONLY_INSTRUCTION}"},
                    {"role": "user", "content": user},
                ],
            )
            return json.loads(response.choices[0].message.content)
        except GroqRateLimitError:
            if attempt == MAX_RATE_LIMIT_RETRIES - 1:
                raise
            time.sleep(delay)
            delay *= 2
        except GroqBadRequestError as exc:
            ran_out_of_reasoning_room = exc.code == "json_validate_failed" and current_max_tokens < GROQ_MAX_MAX_TOKENS
            if not ran_out_of_reasoning_room or attempt == MAX_RATE_LIMIT_RETRIES - 1:
                raise
            current_max_tokens = min(current_max_tokens * 2, GROQ_MAX_MAX_TOKENS)

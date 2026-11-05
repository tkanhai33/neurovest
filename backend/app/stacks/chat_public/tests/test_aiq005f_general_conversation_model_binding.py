from __future__ import annotations

from pathlib import Path

from backend.app.stacks.chat_public.chat_intent_regex import (
    detect_chat_intent,
)
from backend.app.stacks.chat_public.cognitive_model_router import (
    NEURO_FAST_MODEL,
    route_cognitive_request,
)


QUALIFIED_GENERAL_MODEL = 'neuro-fast-no-think:latest'
OLD_GENERAL_MODEL = 'neuro-fast:latest'

CLIENT_FILE = Path(
    "backend/app/stacks/chat_public/ollama_chat_client.py"
)


def route(message: str):
    intent = detect_chat_intent(
        message
    )

    decision = route_cognitive_request(
        message,
        intent=intent,
    )

    return intent, decision


def test_router_constant_uses_qualified_general_model() -> None:
    assert NEURO_FAST_MODEL == QUALIFIED_GENERAL_MODEL


def test_ollama_client_registers_qualified_model() -> None:
    text = CLIENT_FILE.read_text(
        encoding="utf-8",
    )

    assert QUALIFIED_GENERAL_MODEL in text
    assert OLD_GENERAL_MODEL not in text


def test_greeting_uses_qualified_general_model() -> None:
    intent, decision = route(
        "Hello Neuro, how is your day going?"
    )

    assert intent.intent == "general_conversation"
    assert decision.model == QUALIFIED_GENERAL_MODEL


def test_small_talk_uses_qualified_general_model() -> None:
    intent, decision = route(
        "Tell me something interesting about wolves."
    )

    assert intent.intent == "general_conversation"
    assert decision.model == QUALIFIED_GENERAL_MODEL


def test_simple_explanation_uses_qualified_general_model() -> None:
    intent, decision = route(
        "Explain what an emergency fund is."
    )

    assert intent.intent == "general_conversation"
    assert decision.model == QUALIFIED_GENERAL_MODEL


def test_software_debugging_remains_on_coder() -> None:
    intent, decision = route(
        "Help me debug a FastAPI endpoint returning HTTP 500."
    )

    assert intent.family == "DEVELOPER"
    assert decision.model == "neuro-reason:latest"


def test_live_execution_remains_blocked() -> None:
    intent = detect_chat_intent(
        "Execute a real live trade and submit the order."
    )

    assert intent.blocked is True
    assert intent.intent == "blocked_live_execution"
    assert intent.family == "SAFETY"

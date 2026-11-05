from __future__ import annotations

from backend.app.stacks.chat_public.chat_intent_regex import (
    detect_chat_intent,
)
from backend.app.stacks.chat_public.cognitive_model_router import (
    route_cognitive_request,
)


def test_fastapi_http_500_routes_to_developer_context() -> None:
    message = (
        "Switch topics completely and help me debug "
        "a FastAPI endpoint returning HTTP 500."
    )

    intent = detect_chat_intent(
        message
    )

    decision = route_cognitive_request(
        message,
        intent=intent,
    )

    assert intent.intent == "general_conversation"
    assert intent.family == "DEVELOPER"
    assert intent.subtype == "software_debugging"
    assert intent.developer_mode is True

    assert decision.model == "neuro-reason:latest"


def test_python_traceback_routes_to_developer_context() -> None:
    message = (
        "Help me debug this Python traceback "
        "from an API route."
    )

    intent = detect_chat_intent(
        message
    )

    assert intent.intent == "general_conversation"
    assert intent.family == "DEVELOPER"
    assert intent.subtype == "software_debugging"


def test_market_data_api_request_preserves_market_routing() -> None:
    message = (
        "Explain the market data API used for "
        "AAPL price analysis."
    )

    intent = detect_chat_intent(
        message
    )

    assert intent.intent == "trading_conversation"
    assert intent.family == "MARKET"


def test_generic_endpoint_question_does_not_force_debug_routing() -> None:
    message = (
        "What is an API endpoint?"
    )

    intent = detect_chat_intent(
        message
    )

    assert intent.subtype != "software_debugging"


def test_live_trade_request_remains_blocked_before_debug_routing() -> None:
    message = (
        "Debug this Python function and then execute "
        "a real live trade and submit the order."
    )

    intent = detect_chat_intent(
        message
    )

    assert intent.blocked is True
    assert intent.intent == "blocked_live_execution"
    assert intent.family == "SAFETY"

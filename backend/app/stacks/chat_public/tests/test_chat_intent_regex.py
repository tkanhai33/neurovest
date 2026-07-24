from __future__ import annotations

import pytest

from backend.app.stacks.chat_public.chat_intent_regex import (
    ChatIntent,
    detect_chat_intent,
)


@pytest.mark.parametrize(
    ("message", "legacy_intent", "family", "subtype"),
    [
        (
            "hello",
            "general_conversation",
            "GENERAL",
            "greeting",
        ),
        (
            "Are you a happy wolf?",
            "general_conversation",
            "GENERAL",
            "personality",
        ),
        (
            "As your developer, how can I improve you?",
            "general_conversation",
            "DEVELOPER",
            "self_evaluation",
        ),
        (
            "Review the architecture.",
            "general_conversation",
            "DEVELOPER",
            "architecture_review",
        ),
        (
            "What capabilities are missing?",
            "general_conversation",
            "DEVELOPER",
            "self_evaluation",
        ),
        (
            "What should we build next?",
            "general_conversation",
            "DEVELOPER",
            "developer_review",
        ),
        (
            "What is the price of AAPL?",
            "trading_conversation",
            "MARKET",
            "market_analysis",
        ),
        (
            "Review my portfolio holdings.",
            "trading_conversation",
            "PORTFOLIO",
            "portfolio_review",
        ),
        (
            "graph reset",
            "graph_reset",
            "SYSTEM",
            "graph_reset",
        ),
        (
            "graph validate",
            "graph_validate",
            "SYSTEM",
            "graph_validate",
        ),
        (
            "simulate trade AAPL",
            "simulate_trade",
            "MARKET",
            "simulate_trade",
        ),
        (
            "Enable live trading and execute a real trade.",
            "blocked_live_execution",
            "SAFETY",
            "blocked_live_execution",
        ),
        (
            "Explain diversification.",
            "general_conversation",
            "GENERAL",
            "discussion",
        ),
    ],
)
def test_detect_chat_intent_v2_metadata_and_legacy_compatibility(
    message: str,
    legacy_intent: str,
    family: str,
    subtype: str,
) -> None:
    result = detect_chat_intent(message)

    assert result.intent == legacy_intent
    assert result.family == family
    assert result.subtype == subtype


def test_developer_pronoun_i_is_not_detected_as_ticker() -> None:
    result = detect_chat_intent(
        "As your developer, how can I improve you?"
    )

    assert result.symbol is None
    assert result.intent == "general_conversation"
    assert result.developer_mode is True
    assert result.self_evaluation is True


def test_market_symbol_is_preserved() -> None:
    result = detect_chat_intent(
        "What is the price of AAPL?"
    )

    assert result.symbol == "AAPL"
    assert result.intent == "trading_conversation"


def test_blocked_live_execution_remains_fail_closed() -> None:
    result = detect_chat_intent(
        "Enable live trading and execute a real trade."
    )

    assert result.blocked is True
    assert result.intent == "blocked_live_execution"


def test_chat_intent_legacy_constructor_remains_valid() -> None:
    result = ChatIntent(
        intent="general_conversation",
    )

    assert result.intent == "general_conversation"
    assert result.symbol is None
    assert result.blocked is False

"""V74: avoid rolling historical turn excerpts into summaries."""

from backend.app.stacks.chat_public.context import (
    context_assembler as ca,
)

INITIAL = (
    "I'm developing a strategy called Northern Wolf "
    "using RSI and Bollinger Bands."
)
CORRECTION = (
    "Actually, change Northern Wolf. It is now a momentum "
    "strategy using MACD and EMA crossovers instead of "
    "RSI and Bollinger Bands."
)


def extract(message):
    return ca.extract_strategy_context(
        user_message=message,
        assistant_message="Okay",
        strategy_capture=None,
        remembered_terms={},
    )


def summarize(previous, active, user, assistant):
    return ca.build_summary(
        previous_summary=previous,
        remembered_terms={},
        active_strategy=active,
        portfolio_context={},
        latest_user_message=user,
        latest_assistant_message=assistant,
    )


def test_three_turn_summary_does_not_accumulate_turn_logs():
    active = extract(INITIAL)
    first = summarize(
        "",
        active,
        INITIAL,
        "Northern Wolf uses RSI and Bollinger Bands.",
    )

    active = extract(CORRECTION)
    second = summarize(
        first,
        active,
        CORRECTION,
        "Northern Wolf is now momentum using MACD and EMA.",
    )

    third = summarize(
        second,
        active,
        "What's my strategy now?",
        "Northern Wolf is momentum using MACD and EMA.",
    )

    assert third.count("Latest turn: user asked") == 1
    assert "What's my strategy now?" in third
    assert "Northern Wolf is currently a momentum strategy" in third
    assert "MACD, EMA crossovers" in third
    assert "Neuro replied ''" not in third
    assert (
        "Northern Wolf is currently a user-described strategy"
        not in third
    )


def test_unrelated_durable_summary_is_preserved():
    active = extract(CORRECTION)

    previous = (
        "The user prefers daily risk reports. "
        "Northern Wolf is currently a mean-reversion strategy "
        "using RSI and Bollinger Bands. "
        "Latest turn: user asked 'Old question' "
        "and Neuro replied 'Old answer'."
    )

    result = summarize(
        previous,
        active,
        "What's my current strategy?",
        "Momentum using MACD and EMA.",
    )

    assert "daily risk reports" in result
    assert "mean-reversion strategy using RSI" not in result
    assert result.count("Latest turn: user asked") == 1


def test_no_previous_turn_marker_preserves_summary():
    result = summarize(
        "The user prefers concise explanations.",
        None,
        "Hello",
        "Hello!",
    )

    assert "The user prefers concise explanations." in result
    assert result.count("Latest turn: user asked") == 1


def test_historical_content_not_truncated_in_new_turn():
    active = extract(CORRECTION)

    result = summarize(
        "The user likes risk reports.",
        active,
        CORRECTION,
        "Northern Wolf is now momentum using MACD.",
    )

    assert "Neuro replied ''" not in result
    assert "Northern Wolf is now momentum using MACD" in result

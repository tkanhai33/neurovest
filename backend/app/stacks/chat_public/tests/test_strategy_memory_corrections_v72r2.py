"""V72R2 isolated strategy correction regressions."""

from backend.app.stacks.chat_public.context import (
    context_assembler as ca,
)

OLD = (
    "Northern Wolf is currently a mean-reversion strategy "
    "using RSI and Bollinger Bands."
)

CORRECTION = (
    "Actually, change Northern Wolf. It is now a momentum "
    "strategy using MACD and EMA crossovers instead of "
    "RSI and Bollinger Bands."
)


def extract(text, assistant="Okay"):
    return ca.extract_strategy_context(
        user_message=text,
        assistant_message=assistant,
        strategy_capture=None,
        remembered_terms={},
    )


def test_correction_extracts_current_strategy():
    result = extract(CORRECTION)
    assert result is not None
    assert result["name"] == "Northern Wolf"
    assert result["strategy_type"] == "momentum"
    assert result["indicators"] == ["MACD", "EMA crossovers"]
    assert result["is_correction"] is True


def test_initial_strategy_description():
    result = extract(
        "I'm developing a strategy called Northern Wolf "
        "using RSI and Bollinger Bands."
    )
    assert result is not None
    assert result["name"] == "Northern Wolf"
    assert result["indicators"] == ["RSI", "Bollinger Bands"]
    assert result["is_correction"] is False


def test_current_definition_without_correction():
    result = extract(
        "Northern Wolf is a momentum strategy using "
        "MACD and EMA crossovers."
    )
    assert result is not None
    assert result["strategy_type"] == "momentum"


def test_assistant_cannot_invent_user_strategy():
    result = extract(
        "Hello",
        assistant="Northern Wolf now uses MACD.",
    )
    assert result is None


def test_correction_supersedes_stale_summary():
    active = extract(CORRECTION)

    summary = ca.build_summary(
        previous_summary=(
            OLD + " The user prefers daily risk reports."
        ),
        remembered_terms={},
        active_strategy=active,
        portfolio_context={},
        latest_user_message=CORRECTION,
        latest_assistant_message="Correction acknowledged.",
    )

    assert OLD not in summary
    assert "daily risk reports" in summary
    assert "Northern Wolf is currently a momentum strategy" in summary
    assert "MACD, EMA crossovers" in summary


def test_other_strategy_remains_intact():
    active = extract(CORRECTION)

    summary = ca.build_summary(
        previous_summary=(
            "Southern Bear is currently a trend strategy. " + OLD
        ),
        remembered_terms={},
        active_strategy=active,
        portfolio_context={},
        latest_user_message=CORRECTION,
        latest_assistant_message="Correction acknowledged.",
    )

    assert "Southern Bear is currently a trend strategy." in summary
    assert OLD not in summary


def test_captured_strategy_still_takes_precedence():
    result = ca.extract_strategy_context(
        user_message=CORRECTION,
        assistant_message="Okay",
        strategy_capture={
            "name": "Captured Strategy",
            "status": "proposed_not_validated",
        },
        remembered_terms={},
    )

    assert result["name"] == "Captured Strategy"
    assert result["source"] == "strategy_proposal_capture"


def test_uncertain_intent_does_not_become_memory():
    assert extract(
        "Could we maybe make something with MACD?"
    ) is None

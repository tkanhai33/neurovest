from __future__ import annotations

from backend.app.stacks.chat_public.chat_runtime import (
    _build_strategy_snapshot_explanation_v1,
)


def snapshot_message() -> str:
    return "\n".join(
        [
            "Please explain this read-only dashboard strategy snapshot.",
            "Treat these values as user-provided on-screen context, not as a",
            "trade instruction or independently fetched evidence.",
            "Symbol: MSFT",
            "Decision: BUY",
            "Confidence: 7.4%",
            "Provider: owner_enabled_reference_strategy_aggregation",
            "Reason: Buy vote majority",
            "Owner strategy applied: Yes",
            "Buy votes: 33",
            "Sell votes: 8",
            "Hold votes: 87",
            "Explain the result, uncertainty, and paper-only boundary.",
        ],
    )


def test_dashboard_snapshot_gets_deterministic_explanation():
    response = _build_strategy_snapshot_explanation_v1(
        snapshot_message(),
    )

    assert response is not None
    assert "MSFT" in response
    assert "**BUY**" in response
    assert "7.4%" in response
    assert "33 qualified evaluators" in response
    assert "8 reported SELL" in response
    assert "87 reported HOLD" in response
    assert "No paper order, broker order, or live execution" in response


def test_unmarked_general_chat_does_not_activate_snapshot_repair():
    assert (
        _build_strategy_snapshot_explanation_v1(
            "Explain why MSFT moved today."
        )
        is None
    )


def test_malformed_snapshot_fails_closed_to_normal_chat():
    assert (
        _build_strategy_snapshot_explanation_v1(
            "Please explain this read-only dashboard strategy snapshot.\n"
            "Symbol: MSFT"
        )
        is None
    )

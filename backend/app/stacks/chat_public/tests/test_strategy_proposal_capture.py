from pathlib import Path
import json

import pytest

from backend.app.stacks.chat_public import (
    strategy_proposal_capture as capture,
)


@pytest.mark.parametrize(
    ("message", "expected"),
    (
        (
            "Create a strategy proposal named alpha_cross_01.",
            "alpha_cross_01",
        ),
        (
            'Create a strategy called "mean_revert_v2".',
            "mean_revert_v2",
        ),
        (
            "Create a strategy named alpha.v2.",
            "alpha.v2",
        ),
        (
            "The strategy name is breakout_5m.",
            "breakout_5m",
        ),
        (
            "Use a system called momentum-v3!",
            "momentum-v3",
        ),
    ),
)
def test_extract_strategy_name_positive(
    message,
    expected,
):
    assert (
        capture.extract_strategy_name(
            message
        )
        == expected
    )


@pytest.mark.parametrize(
    "message",
    (
        "",
        "Create a strategy for AAPL using moving averages.",
        "Build a strategy using RSI.",
        "Strategy for MSFT.",
        "Create a trading strategy.",
        "Research a strategy for NVDA.",
    ),
)
def test_extract_strategy_name_does_not_invent_name(
    message,
):
    assert (
        capture.extract_strategy_name(
            message
        )
        is None
    )


def test_capture_persists_strategy_name(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setattr(
        capture,
        "OUT_DIR",
        tmp_path,
    )

    result = capture.capture_strategy_proposal(
        (
            "Create a strategy proposal named "
            "qualification_strategy_alpha for AAPL "
            "using a moving average crossover."
        ),
        (
            "I will create the strategy proposal "
            "qualification_strategy_alpha."
        ),
        intent="trading_conversation",
        symbol="AAPL",
        owner_user_id="qualification-owner",
    )

    assert result is not None
    assert result["captured"] is True

    path = Path(
        result["path"]
    )

    payload = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    assert (
        payload["strategy_name"]
        == "qualification_strategy_alpha"
    )

    assert payload["symbol"] == "AAPL"

    assert (
        payload["owner_user_id"]
        == "qualification-owner"
    )

    assert (
        payload["status"]
        == "captured_pending_review"
    )

    assert (
        payload["safety"]["live_execution_allowed"]
        is False
    )

    assert (
        payload["safety"]["broker_execution_allowed"]
        is False
    )

    assert (
        payload["safety"]["simulation_only"]
        is True
    )


def test_capture_does_not_invent_strategy_name(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setattr(
        capture,
        "OUT_DIR",
        tmp_path,
    )

    result = capture.capture_strategy_proposal(
        (
            "Create a strategy for AAPL "
            "using moving averages."
        ),
        "Here is the requested strategy proposal.",
        intent="trading_conversation",
        symbol="AAPL",
        owner_user_id="qualification-owner",
    )

    assert result is not None

    payload = json.loads(
        Path(
            result["path"]
        ).read_text(
            encoding="utf-8"
        )
    )

    assert (
        payload["strategy_name"]
        is None
    )


def test_library_routes_still_do_not_capture(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setattr(
        capture,
        "OUT_DIR",
        tmp_path,
    )

    for route in (
        "strategy_library_identity",
        "strategy_library_list",
        "strategy_library_count",
    ):

        result = capture.capture_strategy_proposal(
            (
                "Create a strategy proposal named "
                "should_not_capture."
            ),
            "Strategy proposal.",
            intent="trading_conversation",
            symbol="AAPL",
            request_route=route,
            owner_user_id="qualification-owner",
        )

        assert result is None


def test_research_conversation_still_does_not_capture(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setattr(
        capture,
        "OUT_DIR",
        tmp_path,
    )

    result = capture.capture_strategy_proposal(
        (
            "Create a strategy proposal named "
            "should_not_capture."
        ),
        "Strategy proposal.",
        intent="research_conversation",
        symbol="AAPL",
        owner_user_id="qualification-owner",
    )

    assert result is None

from unittest.mock import (
    AsyncMock,
    MagicMock,
    call,
)

import pytest

from backend.app.stacks.strategy import (
    strategy_service,
)
from backend.app.stacks.strategy.evaluators.registry import (
    ALLOWLISTED_EVALUATORS,
)


NAMES = tuple(
    ALLOWLISTED_EVALUATORS
)[:24]


def bars():
    return [
        {
            "symbol": "AAPL",
            "timestamp":
                f"2025-01-{index + 1:03d}T00:00:00+00:00",
            "interval": "1d",
            "open": 100.0,
            "high": 102.0,
            "low": 98.0,
            "close": 100.0,
            "volume": 1000.0 + index,
            "provider": "fixture",
        }
        for index in range(
            253
        )
    ]


def result(
    name,
    decision,
    confidence=0.6,
):
    abstain = (
        decision == "ABSTAIN"
    )

    return {
        "status":
            "abstain"
            if abstain
            else "ok",
        "strategy_name":
            name,
        "evaluator_id":
            (
                name
                .lower()
                .replace(
                    " ",
                    "_",
                )
                + "_v1"
            ),
        "decision":
            decision,
        "signal":
            decision,
        "confidence":
            0.0
            if abstain
            else confidence,
        "reason":
            "fixture",
    }


def install(
    monkeypatch,
    *,
    enabled_names,
    evaluator_results,
):
    enabled_lookup = AsyncMock(
        return_value=enabled_names
    )

    supplied_bars = bars()

    bars_mock = MagicMock(
        return_value=supplied_bars
    )

    evaluator = MagicMock(
        side_effect=lambda name, values:
            evaluator_results[
                name
            ]
    )

    fallback = MagicMock(
        return_value={
            "status": "ok",
            "symbol": "AAPL",
            "decision": "HOLD",
            "signal": "hold",
            "confidence": 0.0,
            "provider": "strategy_engine",
        }
    )

    trace = AsyncMock()

    monkeypatch.setattr(
        strategy_service,
        "list_enabled_strategy_names",
        enabled_lookup,
    )

    monkeypatch.setattr(
        strategy_service,
        "get_bars",
        bars_mock,
    )

    monkeypatch.setattr(
        strategy_service,
        "evaluate_allowlisted_strategy",
        evaluator,
    )

    monkeypatch.setattr(
        strategy_service,
        "generate_strategy_decision",
        fallback,
    )

    monkeypatch.setattr(
        strategy_service,
        "emit_runtime_step",
        trace,
    )

    return (
        enabled_lookup,
        supplied_bars,
        bars_mock,
        evaluator,
        fallback,
    )


def test_registry_fixture_is_exact_twenty_four():
    assert len(
        NAMES
    ) == 24


@pytest.mark.asyncio
async def test_owner_all_twenty_four_use_one_253_bar_fetch(
    monkeypatch,
):
    decisions = (
        *("BUY",) * 12,
        *("SELL",) * 6,
        *("HOLD",) * 4,
        *("ABSTAIN",) * 2,
    )

    evaluator_results = {
        name:
            result(
                name,
                decision,
                0.75,
            )
        for name, decision in zip(
            NAMES,
            decisions,
            strict=True,
        )
    }

    shuffled_enabled = [
        *reversed(
            NAMES
        ),
        NAMES[
            0
        ],
        NAMES[
            9
        ],
        "Unknown Metadata Strategy",
        "ATR Position Sizing",
    ]

    (
        enabled_lookup,
        supplied_bars,
        bars_mock,
        evaluator,
        fallback,
    ) = install(
        monkeypatch,
        enabled_names=shuffled_enabled,
        evaluator_results=evaluator_results,
    )

    output = await (
        strategy_service
        .get_strategy_decision_for_api(
            " aapl ",
            owner_subject="owner-24",
        )
    )

    enabled_lookup.assert_awaited_once_with(
        owner_subject="owner-24"
    )

    bars_mock.assert_called_once_with(
        "AAPL",
        limit=253,
    )

    assert evaluator.call_args_list == [
        call(
            name,
            supplied_bars,
        )
        for name in NAMES
    ]

    fallback.assert_not_called()

    assert output[
        "symbol"
    ] == "AAPL"

    assert output[
        "decision"
    ] == "BUY"

    assert output[
        "reason"
    ] == "buy_vote_majority"

    assert output[
        "provider"
    ] == (
        "owner_enabled_reference_strategy_aggregation"
    )

    assert output[
        "owner_strategy_applied"
    ] is True

    assert output[
        "enabled_strategy_names"
    ] == list(
        NAMES
    )

    assert output[
        "enabled_strategy_count"
    ] == 24

    assert output[
        "buy_votes"
    ] == 12

    assert output[
        "sell_votes"
    ] == 6

    assert output[
        "hold_votes"
    ] == 4

    assert output[
        "abstaining_results"
    ] == 2

    assert output[
        "received_results"
    ] == 24

    assert output[
        "eligible_results"
    ] == 22

    assert len(
        output[
            "strategy_results"
        ]
    ) == 24

    assert output.get(
        "portfolio_output"
    ) is None

    assert output[
        "execution_enabled"
    ] is False


@pytest.mark.asyncio
async def test_owner_long_history_bulk_subset_uses_253(
    monkeypatch,
):
    selected = (
        "Time-Series Momentum",
        "Golden Cross",
        "Price Above Moving Average",
    )

    evaluator_results = {
        name:
            result(
                name,
                "HOLD",
                0.0,
            )
        for name in selected
    }

    (
        _,
        supplied_bars,
        bars_mock,
        evaluator,
        fallback,
    ) = install(
        monkeypatch,
        enabled_names=list(
            reversed(
                selected
            )
        ),
        evaluator_results=evaluator_results,
    )

    output = await (
        strategy_service
        .get_strategy_decision_for_api(
            "MSFT",
            owner_subject="owner-long-history",
        )
    )

    bars_mock.assert_called_once_with(
        "MSFT",
        limit=253,
    )

    assert evaluator.call_args_list == [
        call(
            name,
            supplied_bars,
        )
        for name in selected
    ]

    fallback.assert_not_called()

    assert output[
        "enabled_strategy_names"
    ] == list(
        selected
    )

    assert output[
        "enabled_strategy_count"
    ] == 3

    assert output[
        "received_results"
    ] == 3

    assert output[
        "hold_votes"
    ] == 3


@pytest.mark.asyncio
async def test_duplicate_owner_metadata_evaluates_once(
    monkeypatch,
):
    selected = (
        "MACD Crossover",
        "Golden Cross",
    )

    evaluator_results = {
        name:
            result(
                name,
                "HOLD",
                0.0,
            )
        for name in selected
    }

    (
        _,
        supplied_bars,
        bars_mock,
        evaluator,
        fallback,
    ) = install(
        monkeypatch,
        enabled_names=[
            selected[
                1
            ],
            selected[
                0
            ],
            selected[
                0
            ],
            selected[
                1
            ],
        ],
        evaluator_results=evaluator_results,
    )

    output = await (
        strategy_service
        .get_strategy_decision_for_api(
            "NVDA",
            owner_subject="owner-duplicates",
        )
    )

    bars_mock.assert_called_once_with(
        "NVDA",
        limit=253,
    )

    assert evaluator.call_args_list == [
        call(
            name,
            supplied_bars,
        )
        for name in selected
    ]

    fallback.assert_not_called()

    assert output[
        "enabled_strategy_names"
    ] == list(
        selected
    )

    assert output[
        "enabled_strategy_count"
    ] == 2


@pytest.mark.asyncio
async def test_unknown_metadata_preserves_fallback(
    monkeypatch,
):
    enabled_lookup = AsyncMock(
        return_value=[
            "Unknown Metadata Strategy",
            "ATR Position Sizing",
        ]
    )

    bars_mock = MagicMock()
    evaluator = MagicMock()

    fallback = MagicMock(
        return_value={
            "status": "ok",
            "symbol": "TD",
            "decision": "HOLD",
            "signal": "hold",
            "confidence": 0.0,
            "provider": "strategy_engine",
        }
    )

    monkeypatch.setattr(
        strategy_service,
        "list_enabled_strategy_names",
        enabled_lookup,
    )

    monkeypatch.setattr(
        strategy_service,
        "get_bars",
        bars_mock,
    )

    monkeypatch.setattr(
        strategy_service,
        "evaluate_allowlisted_strategy",
        evaluator,
    )

    monkeypatch.setattr(
        strategy_service,
        "generate_strategy_decision",
        fallback,
    )

    monkeypatch.setattr(
        strategy_service,
        "emit_runtime_step",
        AsyncMock(),
    )

    output = await (
        strategy_service
        .get_strategy_decision_for_api(
            "TD",
            owner_subject="owner-unknown",
        )
    )

    bars_mock.assert_not_called()
    evaluator.assert_not_called()

    fallback.assert_called_once_with(
        "TD"
    )

    assert output[
        "owner_strategy_applied"
    ] is False

    assert output[
        "provider"
    ] == "strategy_engine"

    assert output.get(
        "portfolio_output"
    ) is None


@pytest.mark.asyncio
async def test_single_bulk_strategy_preserves_single_provider(
    monkeypatch,
):
    selected = "MACD Crossover"

    evaluator_results = {
        selected:
            {
                **result(
                    selected,
                    "BUY",
                    0.4,
                ),
                "current_macd":
                    1.5,
                "current_signal":
                    1.0,
            }
    }

    (
        _,
        _,
        bars_mock,
        evaluator,
        fallback,
    ) = install(
        monkeypatch,
        enabled_names=[
            selected
        ],
        evaluator_results=evaluator_results,
    )

    output = await (
        strategy_service
        .get_strategy_decision_for_api(
            "TSLA",
            owner_subject="owner-single-bulk",
        )
    )

    bars_mock.assert_called_once_with(
        "TSLA",
        limit=253,
    )

    evaluator.assert_called_once()
    fallback.assert_not_called()

    assert output[
        "decision"
    ] == "BUY"

    assert output[
        "provider"
    ] == (
        "owner_enabled_reference_strategy"
    )

    assert output[
        "enabled_strategy_name"
    ] == selected

    assert output[
        "enabled_strategy_count"
    ] == 1

    assert output[
        "current_macd"
    ] == 1.5

    assert output[
        "current_signal"
    ] == 1.0

    assert output[
        "execution_enabled"
    ] is False

from unittest.mock import (
    AsyncMock,
    MagicMock,
    call,
)

import pytest

from backend.app.stacks.strategy import (
    strategy_service,
)


NAMES = (
    "Simple Moving Average Crossover",
    "Bollinger Band Breakout",
    "Bollinger Band Mean Reversion",
    "RSI Overbought Mean Reversion",
    "RSI Oversold Mean Reversion",
    "Donchian Channel Breakout",
    "ATR Volatility Breakout",
    "Keltner Channel Breakout",
    "Volatility Breakout from Previous Close",
)


def bars():
    return [
        {
            "symbol": "AAPL",
            "timestamp":
                f"2026-01-{index + 1:02d}T00:00:00+00:00",

            "interval": "1d",
            "open": 100.0,
            "high": 101.0,
            "low": 99.0,
            "close": 100.0,
            "volume": 1000.0 + index,
            "provider": "fixture",
        }
        for index in range(
            50
        )
    ]


def result(
    name,
    decision,
    confidence=0.5,
):
    abstain = (
        decision == "ABSTAIN"
    )

    return {
        "status":
            "abstained"
            if (
                abstain
                and
                name == NAMES[
                    0
                ]
            )
            else (
                "abstain"
                if abstain
                else "ok"
            ),

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
                +
                "_v1"
            ),

        "decision":
            decision,

        "signal":
            (
                "hold"
                if abstain
                else decision.lower()
            ),

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

    engine = MagicMock(
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
        engine,
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
        engine,
    )


@pytest.mark.asyncio
async def test_owner_all_nine_are_evaluated_in_registry_order(
    monkeypatch,
):
    decisions = (
        "BUY",
        "SELL",
        "HOLD",
        "BUY",
        "ABSTAIN",
        "BUY",
        "SELL",
        "HOLD",
        "BUY",
    )

    evaluator_results = {
        name:
            result(
                name,
                decision,
                0.8,
            )
        for name, decision in zip(
            NAMES,
            decisions,
            strict=True,
        )
    }

    shuffled_enabled = [
        NAMES[
            8
        ],
        "Unknown Metadata Strategy",
        NAMES[
            5
        ],
        NAMES[
            2
        ],
        NAMES[
            0
        ],
        NAMES[
            7
        ],
        NAMES[
            4
        ],
        NAMES[
            1
        ],
        NAMES[
            6
        ],
        NAMES[
            3
        ],
    ]

    (
        enabled_lookup,
        supplied_bars,
        bars_mock,
        evaluator,
        engine,
    ) = install(
        monkeypatch,
        enabled_names=shuffled_enabled,
        evaluator_results=evaluator_results,
    )

    output = await (
        strategy_service
        .get_strategy_decision_for_api(
            " aapl ",
            owner_subject="owner-nine",
        )
    )

    enabled_lookup.assert_awaited_once_with(
        owner_subject="owner-nine"
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

    engine.assert_not_called()

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
    ] == 9

    assert output[
        "buy_votes"
    ] == 4

    assert output[
        "sell_votes"
    ] == 2

    assert output[
        "hold_votes"
    ] == 2

    assert output[
        "abstaining_results"
    ] == 1

    assert output[
        "received_results"
    ] == 9

    assert output[
        "eligible_results"
    ] == 8

    assert len(
        output[
            "strategy_results"
        ]
    ) == 9

    assert output[
        "portfolio_output"
    ] is None

    assert output[
        "execution_enabled"
    ] is False


@pytest.mark.asyncio
async def test_owner_second_family_only_uses_four_results(
    monkeypatch,
):
    second_names = NAMES[
        5:
    ]

    evaluator_results = {
        name:
            result(
                name,
                "HOLD",
                0.0,
            )
        for name in second_names
    }

    (
        _,
        supplied_bars,
        bars_mock,
        evaluator,
        engine,
    ) = install(
        monkeypatch,
        enabled_names=list(
            reversed(
                second_names
            )
        ),
        evaluator_results=evaluator_results,
    )

    output = await (
        strategy_service
        .get_strategy_decision_for_api(
            "MSFT",
            owner_subject="owner-second-family",
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
        for name in second_names
    ]

    engine.assert_not_called()

    assert output[
        "decision"
    ] == "HOLD"

    assert output[
        "reason"
    ] == "no_directional_vote"

    assert output[
        "enabled_strategy_names"
    ] == list(
        second_names
    )

    assert output[
        "received_results"
    ] == 4

    assert output[
        "hold_votes"
    ] == 4


@pytest.mark.asyncio
async def test_duplicate_enabled_metadata_is_evaluated_once(
    monkeypatch,
):
    selected = (
        NAMES[
            5
        ],
        NAMES[
            8
        ],
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
        _,
        evaluator,
        engine,
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

    assert evaluator.call_args_list == [
        call(
            name,
            supplied_bars,
        )
        for name in selected
    ]

    engine.assert_not_called()

    assert output[
        "enabled_strategy_names"
    ] == list(
        selected
    )

    assert output[
        "enabled_strategy_count"
    ] == 2


@pytest.mark.asyncio
async def test_unknown_metadata_still_preserves_fallback(
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

    engine = MagicMock(
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
        engine,
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
    engine.assert_called_once_with(
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
async def test_one_second_family_strategy_preserves_single_provider(
    monkeypatch,
):
    selected = NAMES[
        5
    ]

    evaluator_results = {
        selected:
            {
                **result(
                    selected,
                    "BUY",
                    0.25,
                ),
                "current_upper_channel":
                    110.0,
                "current_close":
                    111.0,
            }
    }

    (
        _,
        _,
        _,
        evaluator,
        engine,
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
            owner_subject="owner-single-second",
        )
    )

    evaluator.assert_called_once()
    engine.assert_not_called()

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
        "current_upper_channel"
    ] == 110.0

    assert output[
        "current_close"
    ] == 111.0

    assert output[
        "execution_enabled"
    ] is False

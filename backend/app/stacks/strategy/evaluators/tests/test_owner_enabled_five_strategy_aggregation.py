from unittest.mock import (
    AsyncMock,
    MagicMock,
    call,
)

import pytest

from backend.app.stacks.strategy import (
    strategy_service,
)


SMA = "Simple Moving Average Crossover"
BREAKOUT = "Bollinger Band Breakout"
MEAN_REVERSION = "Bollinger Band Mean Reversion"
RSI_OVERBOUGHT = "RSI Overbought Mean Reversion"
RSI_OVERSOLD = "RSI Oversold Mean Reversion"


def bars():
    return [
        {
            "symbol": "AAPL",
            "close": 100.0,
            "provider": "fixture",
        }
        for _ in range(
            50
        )
    ]


def evaluator_result(
    name,
    decision,
    confidence=0.5,
):
    return {
        "status": (
            "abstained"
            if (
                name == SMA
                and
                decision == "ABSTAIN"
            )
            else (
                "abstain"
                if decision == "ABSTAIN"
                else "ok"
            )
        ),
        "strategy_name": name,
        "evaluator_id": (
            name
            .lower()
            .replace(
                " ",
                "_",
            )
            +
            "_v1"
        ),
        "decision": decision,
        "signal": (
            decision.lower()
            if decision != "ABSTAIN"
            else "hold"
        ),
        "confidence": (
            0.0
            if decision == "ABSTAIN"
            else confidence
        ),
        "reason": "fixture",
    }


def install_common(
    monkeypatch,
    *,
    enabled_names,
    evaluator,
):
    enabled_lookup = AsyncMock(
        return_value=enabled_names
    )

    bars_mock = MagicMock(
        return_value=bars()
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
        bars_mock,
        engine,
    )


@pytest.mark.asyncio
async def test_owner_enabled_names_are_intersected_in_registry_order(
    monkeypatch,
):
    results = {
        SMA:
            evaluator_result(
                SMA,
                "BUY",
                0.8,
            ),

        BREAKOUT:
            evaluator_result(
                BREAKOUT,
                "BUY",
                0.6,
            ),

        RSI_OVERBOUGHT:
            evaluator_result(
                RSI_OVERBOUGHT,
                "SELL",
                0.9,
            ),
    }

    evaluator = MagicMock(
        side_effect=lambda name, supplied_bars:
            results[
                name
            ]
    )

    (
        enabled_lookup,
        bars_mock,
        engine,
    ) = install_common(
        monkeypatch,
        enabled_names=[
            RSI_OVERBOUGHT,
            "Unknown Metadata Strategy",
            BREAKOUT,
            SMA,
        ],
        evaluator=evaluator,
    )

    result = await (
        strategy_service
        .get_strategy_decision_for_api(
            " aapl ",
            owner_subject="owner-five",
        )
    )

    enabled_lookup.assert_awaited_once_with(
        owner_subject="owner-five"
    )

    bars_mock.assert_called_once_with(
        "AAPL",
        limit=253,
    )

    evaluated_bars = bars_mock.return_value

    assert evaluator.call_args_list == [
        call(
            SMA,
            evaluated_bars,
        ),
        call(
            BREAKOUT,
            evaluated_bars,
        ),
        call(
            RSI_OVERBOUGHT,
            evaluated_bars,
        ),
    ]

    engine.assert_not_called()

    assert result[
        "symbol"
    ] == "AAPL"

    assert result[
        "decision"
    ] == "BUY"

    assert result[
        "provider"
    ] == (
        "owner_enabled_reference_strategy_aggregation"
    )

    assert result[
        "owner_strategy_applied"
    ] is True

    assert result[
        "enabled_strategy_names"
    ] == [
        SMA,
        BREAKOUT,
        RSI_OVERBOUGHT,
    ]

    assert result[
        "enabled_strategy_count"
    ] == 3

    assert result[
        "enabled_strategy_name"
    ] == (
        "Aggregated qualified owner strategies"
    )

    assert result[
        "buy_votes"
    ] == 2

    assert result[
        "sell_votes"
    ] == 1

    assert result[
        "portfolio_output"
    ] is None

    assert result[
        "execution_enabled"
    ] is False


@pytest.mark.asyncio
async def test_single_sma_owner_preserves_visible_sma_evidence(
    monkeypatch,
):
    sma = {
        **evaluator_result(
            SMA,
            "SELL",
            0.25,
        ),
        "short_window": 5,
        "long_window": 20,
        "minimum_bars": 21,
        "received_bars": 50,
        "previous_fast_sma": 102.0,
        "previous_slow_sma": 101.0,
        "current_fast_sma": 99.0,
        "current_slow_sma": 100.0,
    }

    evaluator = MagicMock(
        return_value=sma
    )

    _, bars_mock, engine = install_common(
        monkeypatch,
        enabled_names=[
            SMA
        ],
        evaluator=evaluator,
    )

    result = await (
        strategy_service
        .get_strategy_decision_for_api(
            "MSFT",
            owner_subject="owner-sma",
        )
    )

    evaluator.assert_called_once_with(
        SMA,
        bars_mock.return_value,
    )

    engine.assert_not_called()

    assert result[
        "decision"
    ] == "SELL"

    assert result[
        "enabled_strategy_name"
    ] == SMA

    assert result[
        "enabled_strategy_names"
    ] == [
        SMA
    ]

    assert result[
        "enabled_strategy_count"
    ] == 1

    assert result[
        "previous_fast_sma"
    ] == 102.0

    assert result[
        "previous_slow_sma"
    ] == 101.0

    assert result[
        "current_fast_sma"
    ] == 99.0

    assert result[
        "current_slow_sma"
    ] == 100.0


@pytest.mark.asyncio
async def test_unknown_enabled_metadata_preserves_system_fallback(
    monkeypatch,
):
    evaluator = MagicMock()

    _, bars_mock, engine = install_common(
        monkeypatch,
        enabled_names=[
            "Unknown Metadata Strategy"
        ],
        evaluator=evaluator,
    )

    result = await (
        strategy_service
        .get_strategy_decision_for_api(
            "NVDA",
            owner_subject="owner-metadata",
        )
    )

    bars_mock.assert_not_called()
    evaluator.assert_not_called()
    engine.assert_called_once_with(
        "NVDA"
    )

    assert result[
        "owner_strategy_applied"
    ] is False

    assert result[
        "provider"
    ] == "strategy_engine"

    assert result[
        "owner_strategy_reason"
    ] == "qualified_sma_not_enabled"


@pytest.mark.asyncio
async def test_all_owner_evaluators_abstaining_returns_abstention(
    monkeypatch,
):
    evaluator = MagicMock(
        side_effect=[
            evaluator_result(
                SMA,
                "ABSTAIN",
            ),
            evaluator_result(
                BREAKOUT,
                "ABSTAIN",
            ),
        ]
    )

    _, _, engine = install_common(
        monkeypatch,
        enabled_names=[
            SMA,
            BREAKOUT,
        ],
        evaluator=evaluator,
    )

    result = await (
        strategy_service
        .get_strategy_decision_for_api(
            "TSLA",
            owner_subject="owner-abstain",
        )
    )

    engine.assert_not_called()

    assert result[
        "status"
    ] == "abstain"

    assert result[
        "decision"
    ] == "ABSTAIN"

    assert result[
        "reason"
    ] == "all_evaluators_abstained"

    assert result[
        "owner_strategy_applied"
    ] is True

    assert result[
        "abstaining_results"
    ] == 2

    assert result[
        "portfolio_output"
    ] is None


@pytest.mark.asyncio
async def test_evaluator_failure_fails_closed_without_engine_fallback(
    monkeypatch,
):
    evaluator = MagicMock(
        side_effect=RuntimeError(
            "fixture evaluator failure"
        )
    )

    _, bars_mock, engine = install_common(
        monkeypatch,
        enabled_names=[
            BREAKOUT
        ],
        evaluator=evaluator,
    )

    result = await (
        strategy_service
        .get_strategy_decision_for_api(
            "AAPL",
            owner_subject="owner-failure",
        )
    )

    bars_mock.assert_called_once_with(
        "AAPL",
        limit=253,
    )

    engine.assert_not_called()

    assert result[
        "status"
    ] == "abstained"

    assert result[
        "decision"
    ] == "ABSTAIN"

    assert result[
        "owner_strategy_applied"
    ] is False

    assert result[
        "reason"
    ] == "owner_enabled_evaluator_failed_closed"

    assert result[
        "portfolio_output"
    ] is None


@pytest.mark.asyncio
async def test_duplicate_owner_enabled_names_evaluate_once(
    monkeypatch,
):
    evaluator = MagicMock(
        return_value=evaluator_result(
            BREAKOUT,
            "HOLD",
            0.0,
        )
    )

    _, bars_mock, engine = install_common(
        monkeypatch,
        enabled_names=[
            BREAKOUT,
            BREAKOUT,
            BREAKOUT,
        ],
        evaluator=evaluator,
    )

    result = await (
        strategy_service
        .get_strategy_decision_for_api(
            "AAPL",
            owner_subject="owner-duplicate",
        )
    )

    evaluator.assert_called_once_with(
        BREAKOUT,
        bars_mock.return_value,
    )

    engine.assert_not_called()

    assert result[
        "enabled_strategy_names"
    ] == [
        BREAKOUT
    ]

    assert result[
        "enabled_strategy_count"
    ] == 1


@pytest.mark.asyncio
async def test_no_owner_strategies_preserves_existing_fallback(
    monkeypatch,
):
    evaluator = MagicMock()

    _, bars_mock, engine = install_common(
        monkeypatch,
        enabled_names=[],
        evaluator=evaluator,
    )

    result = await (
        strategy_service
        .get_strategy_decision_for_api(
            "AAPL",
            owner_subject="owner-empty",
        )
    )

    bars_mock.assert_not_called()
    evaluator.assert_not_called()
    engine.assert_called_once_with(
        "AAPL"
    )

    assert result[
        "owner_strategy_applied"
    ] is False

    assert result[
        "owner_strategy_reason"
    ] == "qualified_sma_not_enabled"

from unittest.mock import (
    AsyncMock,
    MagicMock,
    call,
)

import pytest

from backend.app.stacks.strategy import strategy_service
from backend.app.stacks.strategy.evaluators.aggregation import (
    COMPATIBLE_AGGREGATION_NAMES,
)
from backend.app.stacks.strategy.evaluators.bulk_indicator_family_v3 import (
    BULK_OFFLINE_EVALUATORS_V3,
)
from backend.app.stacks.strategy.evaluators.registry import (
    ALLOWLISTED_EVALUATORS,
)


NAMES = tuple(
    ALLOWLISTED_EVALUATORS
)[:54]

THIRD_FIFTEEN = tuple(
    BULK_OFFLINE_EVALUATORS_V3
)


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
        for index in range(253)
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
                name.lower()
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
            evaluator_results[name]
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

    return (
        enabled_lookup,
        supplied_bars,
        bars_mock,
        evaluator,
        fallback,
    )


def test_registry_fixture_is_exact_fifty_four():
    assert len(NAMES) == 54

    assert (
        NAMES
        ==
        COMPATIBLE_AGGREGATION_NAMES
    )

    assert len(
        THIRD_FIFTEEN
    ) == 15

    assert (
        NAMES[39:]
        ==
        THIRD_FIFTEEN
    )


@pytest.mark.asyncio
async def test_owner_all_fifty_four_use_one_253_bar_fetch(
    monkeypatch,
):
    decisions = (
        *("BUY",) * 24,
        *("SELL",) * 16,
        *("HOLD",) * 10,
        *("ABSTAIN",) * 4,
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
        *reversed(NAMES),
        NAMES[0],
        NAMES[39],
        NAMES[53],
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
            owner_subject="owner-54",
        )
    )

    enabled_lookup.assert_awaited_once_with(
        owner_subject="owner-54"
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

    assert output["symbol"] == "AAPL"
    assert output["decision"] == "BUY"
    assert output["reason"] == "buy_vote_majority"

    assert output["provider"] == (
        "owner_enabled_reference_strategy_aggregation"
    )

    assert output["owner_strategy_applied"] is True
    assert output["enabled_strategy_names"] == list(NAMES)
    assert output["enabled_strategy_count"] == 54
    assert output["buy_votes"] == 24
    assert output["sell_votes"] == 16
    assert output["hold_votes"] == 10
    assert output["abstaining_results"] == 4
    assert output["received_results"] == 54
    assert output["eligible_results"] == 50
    assert len(output["strategy_results"]) == 54
    assert output.get("portfolio_output") is None
    assert output["execution_enabled"] is False


@pytest.mark.asyncio
async def test_owner_third_batch_subset_uses_253_once(
    monkeypatch,
):
    selected = (
        "Parabolic SAR Trend",
        "Ichimoku Trend",
        "N-Day Low Breakdown",
        "Inside Bar Breakout",
        "Williams %R Reversion",
        "Gap Fade",
        "Short-Term Reversal Factor",
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
        enabled_lookup,
        supplied_bars,
        bars_mock,
        evaluator,
        fallback,
    ) = install(
        monkeypatch,
        enabled_names=[
            *reversed(selected),
            selected[0],
            selected[-1],
            "Unknown Metadata Strategy",
        ],
        evaluator_results=evaluator_results,
    )

    output = await (
        strategy_service
        .get_strategy_decision_for_api(
            " msft ",
            owner_subject="owner-third-batch",
        )
    )

    enabled_lookup.assert_awaited_once_with(
        owner_subject="owner-third-batch"
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

    assert output["symbol"] == "MSFT"
    assert output["decision"] == "HOLD"
    assert output["reason"] == "no_directional_vote"
    assert output["enabled_strategy_names"] == list(selected)
    assert output["enabled_strategy_count"] == 7
    assert output["received_results"] == 7
    assert output["eligible_results"] == 7
    assert output["hold_votes"] == 7
    assert output["execution_enabled"] is False


@pytest.mark.asyncio
async def test_duplicate_third_batch_metadata_evaluates_once(
    monkeypatch,
):
    selected = (
        "Aroon Trend",
        "Supertrend",
        "NR7 Breakout",
        "Z-Score Mean Reversion",
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
            selected[3],
            selected[0],
            selected[2],
            selected[1],
            selected[0],
            selected[3],
        ],
        evaluator_results=evaluator_results,
    )

    output = await (
        strategy_service
        .get_strategy_decision_for_api(
            "NVDA",
            owner_subject="owner-duplicates-54",
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
    assert output["enabled_strategy_names"] == list(selected)
    assert output["enabled_strategy_count"] == 4
    assert output["received_results"] == 4


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
            " td ",
            owner_subject="owner-fallback-54",
        )
    )

    enabled_lookup.assert_awaited_once_with(
        owner_subject="owner-fallback-54"
    )

    bars_mock.assert_not_called()
    evaluator.assert_not_called()
    fallback.assert_called_once_with(
        "TD"
    )

    assert output["symbol"] == "TD"
    assert output["decision"] == "HOLD"
    assert output["provider"] == "strategy_engine"


@pytest.mark.asyncio
async def test_owner_evaluator_failure_fails_closed(
    monkeypatch,
):
    selected = (
        "Parabolic SAR Trend",
        "Aroon Trend",
    )

    enabled_lookup = AsyncMock(
        return_value=list(selected)
    )

    supplied_bars = bars()

    bars_mock = MagicMock(
        return_value=supplied_bars
    )

    evaluator = MagicMock(
        side_effect=RuntimeError(
            "fixture evaluator failure"
        )
    )

    fallback = MagicMock()

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
            "AAPL",
            owner_subject="owner-failure-54",
        )
    )

    bars_mock.assert_called_once_with(
        "AAPL",
        limit=253,
    )

    fallback.assert_not_called()

    assert output["status"] == "abstained"
    assert output["decision"] == "ABSTAIN"

    assert (
        output.get(
            "execution_enabled",
            False,
        )
        is False
    )

# Historical fifty-four strategy owner fixture.
NAMES = NAMES[:54]

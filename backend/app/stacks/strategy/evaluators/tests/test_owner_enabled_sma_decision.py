from types import SimpleNamespace
from unittest.mock import (
    AsyncMock,
    MagicMock,
)

import pytest

from backend.app.stacks.market_data.bars import (
    HistoricalBarsUnavailableError,
)
from backend.app.stacks.strategy import (
    strategy_service,
)
from backend.app.stacks.strategy.evaluators.sma_crossover import (
    STRATEGY_NAME,
)


@pytest.fixture(autouse=True)
def isolate_runtime_trace(
    monkeypatch,
):
    trace = AsyncMock()

    monkeypatch.setattr(
        strategy_service,
        "emit_runtime_step",
        trace,
    )

    monkeypatch.setattr(
        strategy_service,
        "create_trace_id",
        lambda prefix: "owner-sma-trace",
    )

    return trace


@pytest.mark.asyncio
async def test_enabled_owner_uses_exact_sma_evaluator(
    monkeypatch,
):
    enabled_lookup = AsyncMock(
        return_value=[
            STRATEGY_NAME,
        ]
    )

    bars = [
        {
            "close": 100.0,
            "provider": "fixture",
        }
        for _ in range(
            50
        )
    ]

    evaluator_result = {
        "status": "ok",
        "strategy_name": STRATEGY_NAME,
        "evaluator_id":
            "simple_moving_average_crossover_v1",
        "decision": "HOLD",
        "signal": "hold",
        "confidence": 0.0,
        "reason": "no_new_sma_crossover",
    }

    evaluator = MagicMock(
        return_value=evaluator_result
    )

    engine = MagicMock()

    monkeypatch.setattr(
        strategy_service,
        "list_enabled_strategy_names",
        enabled_lookup,
    )

    monkeypatch.setattr(
        strategy_service,
        "get_bars",
        MagicMock(
            return_value=bars
        ),
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

    result = (
        await strategy_service
        .get_strategy_decision_for_api(
            " aapl ",
            owner_subject="owner-a",
        )
    )

    enabled_lookup.assert_awaited_once_with(
        owner_subject="owner-a"
    )

    evaluator.assert_called_once_with(
        STRATEGY_NAME,
        bars,
    )

    engine.assert_not_called()

    assert result["symbol"] == "AAPL"
    assert result["provider"] == (
        "owner_enabled_reference_strategy"
    )
    assert result[
        "owner_strategy_applied"
    ] is True
    assert result[
        "enabled_strategy_name"
    ] == STRATEGY_NAME
    assert result[
        "portfolio_output"
    ] is None


@pytest.mark.asyncio
async def test_disabled_owner_preserves_system_engine(
    monkeypatch,
):
    monkeypatch.setattr(
        strategy_service,
        "list_enabled_strategy_names",
        AsyncMock(
            return_value=[]
        ),
    )

    evaluator = MagicMock()
    bars = MagicMock()

    engine = MagicMock(
        return_value={
            "status": "rebalanced",
            "symbol": "AAPL",
            "decision": "BUY",
            "signal": "buy",
            "confidence": 0.2,
            "provider": "strategy_engine",
        }
    )

    monkeypatch.setattr(
        strategy_service,
        "evaluate_allowlisted_strategy",
        evaluator,
    )

    monkeypatch.setattr(
        strategy_service,
        "get_bars",
        bars,
    )

    monkeypatch.setattr(
        strategy_service,
        "generate_strategy_decision",
        engine,
    )

    result = (
        await strategy_service
        .get_strategy_decision_for_api(
            "AAPL",
            owner_subject="owner-b",
        )
    )

    evaluator.assert_not_called()
    bars.assert_not_called()
    engine.assert_called_once_with(
        "AAPL"
    )

    assert result[
        "owner_strategy_applied"
    ] is False
    assert result[
        "owner_strategy_reason"
    ] == "qualified_sma_not_enabled"
    assert result["provider"] == "strategy_engine"


@pytest.mark.asyncio
async def test_other_enabled_metadata_does_not_execute(
    monkeypatch,
):
    monkeypatch.setattr(
        strategy_service,
        "list_enabled_strategy_names",
        AsyncMock(
            return_value=[
                "ATR Position Sizing",
            ]
        ),
    )

    evaluator = MagicMock()
    bars = MagicMock()

    engine = MagicMock(
        return_value={
            "status": "ok",
            "symbol": "MSFT",
            "decision": "HOLD",
            "signal": "hold",
            "confidence": 0.0,
        }
    )

    monkeypatch.setattr(
        strategy_service,
        "evaluate_allowlisted_strategy",
        evaluator,
    )

    monkeypatch.setattr(
        strategy_service,
        "get_bars",
        bars,
    )

    monkeypatch.setattr(
        strategy_service,
        "generate_strategy_decision",
        engine,
    )

    result = (
        await strategy_service
        .get_strategy_decision_for_api(
            "MSFT",
            owner_subject="owner-c",
        )
    )

    evaluator.assert_not_called()
    bars.assert_not_called()
    engine.assert_called_once_with(
        "MSFT"
    )

    assert result[
        "owner_strategy_applied"
    ] is False


@pytest.mark.asyncio
async def test_two_owners_receive_separate_enablement(
    monkeypatch,
):
    async def enabled_for_owner(
        *,
        owner_subject,
    ):
        if owner_subject == "enabled-owner":
            return [
                STRATEGY_NAME,
            ]

        return []

    engine = MagicMock(
        return_value={
            "status": "ok",
            "symbol": "AAPL",
            "decision": "HOLD",
            "signal": "hold",
            "confidence": 0.0,
        }
    )

    evaluator = MagicMock(
        return_value={
            "status": "ok",
            "strategy_name": STRATEGY_NAME,
            "evaluator_id":
                "simple_moving_average_crossover_v1",
            "decision": "BUY",
            "signal": "buy",
            "confidence": 0.01,
            "reason":
                "fast_sma_crossed_above_slow_sma",
        }
    )

    monkeypatch.setattr(
        strategy_service,
        "list_enabled_strategy_names",
        enabled_for_owner,
    )

    monkeypatch.setattr(
        strategy_service,
        "get_bars",
        MagicMock(
            return_value=[
                {
                    "close": 100.0,
                    "provider": "fixture",
                }
                for _ in range(
                    50
                )
            ]
        ),
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

    enabled_result = (
        await strategy_service
        .get_strategy_decision_for_api(
            "AAPL",
            owner_subject="enabled-owner",
        )
    )

    disabled_result = (
        await strategy_service
        .get_strategy_decision_for_api(
            "AAPL",
            owner_subject="disabled-owner",
        )
    )

    assert enabled_result[
        "owner_strategy_applied"
    ] is True

    assert disabled_result[
        "owner_strategy_applied"
    ] is False

    assert evaluator.call_count == 1
    assert engine.call_count == 1


@pytest.mark.asyncio
async def test_enabled_lookup_failure_abstains_without_fallback(
    monkeypatch,
):
    lookup = AsyncMock(
        side_effect=RuntimeError(
            "fixture activation unavailable"
        )
    )

    engine = MagicMock()
    evaluator = MagicMock()

    monkeypatch.setattr(
        strategy_service,
        "list_enabled_strategy_names",
        lookup,
    )

    monkeypatch.setattr(
        strategy_service,
        "generate_strategy_decision",
        engine,
    )

    monkeypatch.setattr(
        strategy_service,
        "evaluate_allowlisted_strategy",
        evaluator,
    )

    result = (
        await strategy_service
        .get_strategy_decision_for_api(
            "AAPL",
            owner_subject="owner-d",
        )
    )

    engine.assert_not_called()
    evaluator.assert_not_called()

    assert result["status"] == "abstained"
    assert result["decision"] == "ABSTAIN"
    assert result["signal"] == "hold"
    assert result[
        "reason"
    ] == "owner_strategy_selection_unavailable"


@pytest.mark.asyncio
async def test_enabled_sma_history_failure_abstains(
    monkeypatch,
):
    monkeypatch.setattr(
        strategy_service,
        "list_enabled_strategy_names",
        AsyncMock(
            return_value=[
                STRATEGY_NAME,
            ]
        ),
    )

    def fail_history(
        symbol,
        limit,
    ):
        raise HistoricalBarsUnavailableError(
            "fixture bars unavailable"
        )

    monkeypatch.setattr(
        strategy_service,
        "get_bars",
        fail_history,
    )

    evaluator = MagicMock()
    engine = MagicMock()

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

    result = (
        await strategy_service
        .get_strategy_decision_for_api(
            "AAPL",
            owner_subject="owner-e",
        )
    )

    evaluator.assert_not_called()
    engine.assert_not_called()

    assert result["status"] == "abstained"
    assert result["decision"] == "ABSTAIN"
    assert result[
        "reason"
    ] == "truthful_historical_bars_unavailable"


@pytest.mark.asyncio
async def test_missing_owner_fails_closed(
    monkeypatch,
):
    lookup = AsyncMock()

    monkeypatch.setattr(
        strategy_service,
        "list_enabled_strategy_names",
        lookup,
    )

    result = (
        await strategy_service
        .get_strategy_decision_for_api(
            "AAPL",
            owner_subject=" ",
        )
    )

    lookup.assert_not_awaited()

    assert result["status"] == "error"
    assert result["error"] == "missing_owner_subject"


def test_main_route_forwards_authenticated_subject():
    from backend.app import main

    source = open(
        main.__file__,
        encoding="utf-8",
    ).read()

    route_start = source.index(
        '@app.get("/api/v1/strategy/decision/{symbol}")'
    )

    route_end = source.index(
        "\n\n",
        route_start,
    )

    route = source[
        route_start:route_end
    ]

    assert (
        "require_authenticated_principal"
        in route
    )

    assert "principal.subject" in route

    assert (
        "owner_subject=principal.subject"
        in route
    )

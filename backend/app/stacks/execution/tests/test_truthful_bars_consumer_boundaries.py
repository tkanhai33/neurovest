from unittest.mock import (
    AsyncMock,
    MagicMock,
)

import pytest

from backend.app.stacks.market_data.bars import (
    HistoricalBarsUnavailableError,
)
from backend.app.stacks.strategy import (
    engine,
)
from backend.app.stacks.portfolio import (
    allocator,
)
from backend.app.stacks.execution import (
    paper_broker,
)


def unavailable_error():
    return HistoricalBarsUnavailableError(
        "fixture truthful history unavailable"
    )


def test_strategy_abstains_when_history_is_unavailable(
    monkeypatch,
):
    monkeypatch.setattr(
        engine,
        "get_latest_price",
        lambda symbol: {
            "symbol": symbol,
            "price": 100.0,
        },
    )

    def fail_history(
        symbol,
        limit,
    ):
        raise unavailable_error()

    monkeypatch.setattr(
        engine,
        "get_bars",
        fail_history,
    )

    rebalance = MagicMock()

    monkeypatch.setattr(
        engine,
        "rebalance_portfolio",
        rebalance,
    )

    result = engine.generate_strategy_decision(
        "AAPL"
    )

    assert result["status"] == "abstained"
    assert result["symbol"] == "AAPL"
    assert result["signal"] == "hold"
    assert result["decision"] == "ABSTAIN"
    assert result["confidence"] == 0.0
    assert result["portfolio_output"] is None

    assert (
        result["strategy_signal"]["reason"]
        ==
        "truthful_historical_bars_unavailable"
    )

    rebalance.assert_not_called()


def test_strategy_empty_replay_abstains_without_provider(
    monkeypatch,
):
    monkeypatch.setattr(
        engine,
        "get_latest_price",
        lambda symbol: {
            "symbol": symbol,
            "price": 100.0,
        },
    )

    provider = MagicMock()

    monkeypatch.setattr(
        engine,
        "get_bars",
        provider,
    )

    result = engine.generate_strategy_decision(
        "AAPL",
        replay_bars=[],
    )

    assert result["status"] == "abstained"
    assert result["decision"] == "ABSTAIN"
    assert (
        result["strategy_signal"]["reason"]
        ==
        "no_truthful_historical_bars"
    )

    provider.assert_not_called()


def test_allocator_refuses_sizing_when_history_is_unavailable(
    monkeypatch,
):
    def fail_history(
        symbol,
        limit,
    ):
        raise unavailable_error()

    monkeypatch.setattr(
        allocator,
        "get_bars",
        fail_history,
    )

    result = allocator.calculate_position_size(
        "AAPL",
        total_capital=100000.0,
    )

    assert result["status"] == "sizing_refused"
    assert result["allocated_capital"] == 0.0
    assert result["allocation_percentage"] == 0.0
    assert result["volatility_index"] is None
    assert (
        result["reason"]
        ==
        "truthful_historical_bars_unavailable"
    )


def test_allocator_refuses_empty_history_without_fake_prices(
    monkeypatch,
):
    monkeypatch.setattr(
        allocator,
        "get_bars",
        lambda symbol, limit: [],
    )

    result = allocator.calculate_position_size(
        "AAPL",
        total_capital=100000.0,
    )

    assert result == {
        "status": "sizing_refused",
        "symbol": "AAPL",
        "allocated_capital": 0.0,
        "volatility_index": None,
        "allocation_percentage": 0.0,
        "reason": "no_truthful_historical_bars",
    }


def test_allocator_preserves_truthful_success_path(
    monkeypatch,
):
    monkeypatch.setattr(
        allocator,
        "get_bars",
        lambda symbol, limit: [
            {
                "close": 100.0,
                "provider": "fixture",
            },
            {
                "close": 101.0,
                "provider": "fixture",
            },
            {
                "close": 102.0,
                "provider": "fixture",
            },
            {
                "close": 103.0,
                "provider": "fixture",
            },
            {
                "close": 104.0,
                "provider": "fixture",
            },
        ],
    )

    result = allocator.calculate_position_size(
        "AAPL",
        total_capital=100000.0,
    )

    assert result["status"] == "ok"
    assert result["allocated_capital"] > 0.0
    assert result["allocation_percentage"] > 0.0


@pytest.mark.asyncio
async def test_paper_broker_rejects_refused_sizing_before_quote_or_execution(
    monkeypatch,
):
    save_log = AsyncMock()
    emit_step = AsyncMock()
    quote = AsyncMock()
    execute = MagicMock()

    monkeypatch.setattr(
        paper_broker.execution_control,
        "assert_paper_execution_allowed",
        lambda: None,
    )

    monkeypatch.setattr(
        paper_broker,
        "calculate_live_portfolio_equity",
        AsyncMock(
            return_value={
                "current_cash_balance": 100000.0,
            }
        ),
    )

    monkeypatch.setattr(
        paper_broker,
        "drawdown_healthcheck",
        AsyncMock(
            return_value={
                "status": "ok",
            }
        ),
    )

    monkeypatch.setattr(
        paper_broker,
        "is_kill_switch_active",
        lambda: False,
    )

    monkeypatch.setattr(
        paper_broker,
        "calculate_position_size",
        lambda symbol, total_capital: {
            "status": "sizing_refused",
            "symbol": symbol,
            "allocated_capital": 0.0,
            "volatility_index": None,
            "allocation_percentage": 0.0,
            "reason":
                "truthful_historical_bars_unavailable",
            "error":
                "fixture truthful history unavailable",
        },
    )

    monkeypatch.setattr(
        paper_broker,
        "get_risk_valuation_quote",
        quote,
    )

    monkeypatch.setattr(
        paper_broker,
        "execute_trade",
        execute,
    )

    monkeypatch.setattr(
        paper_broker,
        "save_log",
        save_log,
    )

    monkeypatch.setattr(
        paper_broker,
        "emit_runtime_step",
        emit_step,
    )

    await paper_broker.process_portfolio_output(
        [],
        {
            "symbol": "AAPL",
            "signal": "buy",
            "status": "rebalanced",
        },
        user_id="truthful-history-owner",
        trace_id="truthful-history-trace",
    )

    quote.assert_not_awaited()
    execute.assert_not_called()

    assert save_log.await_count == 1

    payload = save_log.await_args.args[0]

    assert (
        payload["status"]
        ==
        "rejected_history_unavailable"
    )

    assert payload["allocated_capital"] == 0.0
    assert payload["allocation_percentage"] == 0.0
    assert (
        payload["reason"]
        ==
        "truthful_historical_bars_unavailable"
    )

    events = [
        call.kwargs.get(
            "event_type"
        )
        for call in emit_step.await_args_list
    ]

    assert "PAPER_EXECUTION_REJECTED" in events
    assert "PAPER_EXECUTION_STARTED" not in events


def test_sources_contain_no_allocation_fallback_capital():
    allocator_source = open(
        allocator.__file__,
        encoding="utf-8",
    ).read()

    broker_source = open(
        paper_broker.__file__,
        encoding="utf-8",
    ).read()

    assert "closes = [100.0, 100.0" not in allocator_source
    assert "total_capital * 0.01" not in allocator_source
    assert (
        'sizing_matrix.get("allocated_capital", live_capital * 0.01)'
        not in broker_source
    )

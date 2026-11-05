from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.app.stacks.execution import paper_broker


def source_quote(*, age_seconds=30, **changes):
    value = {
        "status": "ok",
        "symbol": "AAPL",
        "price": "100",
        "currency": "USD",
        "provider": "yfinance",
        "observed_at": (
            datetime.now(timezone.utc)
            - timedelta(seconds=age_seconds)
        ),
    }
    value.update(changes)
    return value


def install(monkeypatch, quote_result):
    monkeypatch.setattr(
        paper_broker.execution_control,
        "assert_paper_execution_allowed",
        lambda: None,
    )
    monkeypatch.setattr(
        paper_broker,
        "calculate_live_portfolio_equity",
        AsyncMock(return_value={
            "current_cash_balance": 10000.0
        }),
    )
    monkeypatch.setattr(
        paper_broker,
        "drawdown_healthcheck",
        AsyncMock(return_value={"status": "ok"}),
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
            "status": "ok",
            "allocated_capital": 500.0,
            "allocation_percentage": 0.05,
        },
    )

    quote_loader = AsyncMock(
        side_effect=quote_result
        if isinstance(quote_result, Exception)
        else None,
        return_value=(
            None
            if isinstance(quote_result, Exception)
            else quote_result
        ),
    )
    execute = MagicMock(return_value={
        "symbol": "AAPL",
        "signal": "buy",
        "status": "executed",
    })
    save = AsyncMock(return_value={
        "status": "rejected_market_quote_unavailable"
    })

    monkeypatch.setattr(
        paper_broker,
        "get_risk_valuation_quote",
        quote_loader,
    )
    monkeypatch.setattr(
        paper_broker,
        "execute_trade",
        execute,
    )
    monkeypatch.setattr(
        paper_broker,
        "save_log",
        save,
    )
    monkeypatch.setattr(
        paper_broker,
        "emit_runtime_step",
        AsyncMock(),
    )
    return quote_loader, execute, save


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "payload",
    [
        source_quote(age_seconds=301),
        source_quote(age_seconds=-30),
        source_quote(status="unavailable"),
        source_quote(symbol="MSFT"),
        source_quote(currency=None),
        source_quote(currency="usd"),
        source_quote(provider="unknown"),
        source_quote(observed_at=None),
        source_quote(price="NaN"),
        source_quote(price="0"),
        None,
        RuntimeError("vendor_unavailable"),
    ],
)
async def test_unverified_quote_cannot_generate_fill(
    monkeypatch, payload
):
    loader, execute, save = install(monkeypatch, payload)

    result = await paper_broker.process_portfolio_output(
        [],
        {"symbol": "AAPL", "signal": "buy"},
        user_id="isolated-owner",
    )

    loader.assert_awaited_once_with("AAPL")
    execute.assert_not_called()
    save.assert_awaited_once()

    logged = save.await_args.args[0]
    assert logged["status"] == (
        "rejected_market_quote_unavailable"
    )
    assert result["status"] == logged["status"]


@pytest.mark.asyncio
async def test_valid_quote_reaches_ledger_without_bypass(
    monkeypatch
):
    loader, execute, save = install(
        monkeypatch, source_quote()
    )

    # A successful quote is not approval to commit a trade.
    # The mocked ledger represents the final blocked path.
    save.return_value = {
        "status": "paper_execution_financial_risk_not_qualified"
    }

    result = await paper_broker.process_portfolio_output(
        [],
        {"symbol": "AAPL", "signal": "buy"},
        user_id="isolated-owner",
        request_id=None,
    )

    loader.assert_awaited_once_with("AAPL")
    execute.assert_called_once_with("AAPL", "buy")
    save.assert_awaited_once()

    payload = save.await_args.args[0]
    assert payload["status"] == "executed"
    assert payload["slippage_price"] > 0
    assert payload["commission_paid"] == 1.00
    assert result["status"] == "executed"


def test_no_legacy_quote_call_or_fallback():
    import inspect
    source = inspect.getsource(
        paper_broker.process_portfolio_output
    )
    assert (
        "await get_risk_valuation_quote(symbol)"
        in source
    )
    assert (
        "await get_live_market_price(symbol)"
        not in source
    )
    assert "quote_age <= timedelta(seconds=300)" in source
    assert 'quote_provider == "yfinance"' in source


@pytest.mark.asyncio
async def test_expiring_quote_cannot_reach_simulated_fill(
    monkeypatch,
):
    from datetime import datetime, timedelta, timezone

    observation = datetime.now(timezone.utc) - timedelta(
        seconds=290
    )

    loader, execute, save = install(
        monkeypatch,
        source_quote(observed_at=observation),
    )

    # Both clock readings are deterministic:
    # initially fresh, then expired before the fill.
    clock_readings = iter([
        observation + timedelta(seconds=290),
        observation + timedelta(seconds=301),
    ])

    def controlled_clock():
        return next(clock_readings)

    monkeypatch.setattr(
        paper_broker,
        "_broker_quote_utc_now",
        controlled_clock,
    )

    with pytest.raises(
        RuntimeError,
        match="paper_quote_expired_before_fill",
    ):
        await paper_broker.process_portfolio_output(
            [],
            {"symbol": "AAPL", "signal": "buy"},
            user_id="isolated-owner",
        )

    loader.assert_awaited_once_with("AAPL")
    execute.assert_not_called()
    save.assert_not_awaited()


@pytest.mark.asyncio
async def test_fresh_quote_passes_both_clock_checks(
    monkeypatch,
):
    from datetime import datetime, timedelta, timezone

    observation = datetime.now(timezone.utc) - timedelta(
        seconds=10
    )

    loader, execute, save = install(
        monkeypatch,
        source_quote(observed_at=observation),
    )

    clock_readings = iter([
        observation + timedelta(seconds=10),
        observation + timedelta(seconds=11),
    ])

    monkeypatch.setattr(
        paper_broker,
        "_broker_quote_utc_now",
        lambda: next(clock_readings),
    )

    result = await paper_broker.process_portfolio_output(
        [],
        {"symbol": "AAPL", "signal": "buy"},
        user_id="isolated-owner",
    )

    loader.assert_awaited_once_with("AAPL")
    execute.assert_called_once_with("AAPL", "buy")
    save.assert_awaited_once()
    assert result["status"] == "executed"


def test_prefill_guard_and_clock_contract():
    import inspect

    source = inspect.getsource(
        paper_broker.process_portfolio_output
    )

    assert source.count("_broker_quote_utc_now()") == 2
    assert source.index(
        "quote_age_before_fill = ("
    ) < source.index(
        "trade_result = execute_trade(symbol, signal)"
    )
    assert "paper_quote_expired_before_fill" in source
    assert "await get_live_market_price(symbol)" not in source

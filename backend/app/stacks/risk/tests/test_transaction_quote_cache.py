from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock

import pytest

from backend.app.stacks.risk.transaction_quote_cache import (
    TransactionQuoteUnavailable,
    make_transaction_quote_loader,
)
from backend.app.stacks.risk.transaction_fill import (
    PaperFillUnavailable,
    validate_transaction_fill,
)

NOW = datetime(2026, 10, 13, 19, 0, tzinfo=timezone.utc)


def quote(symbol="AAPL", observed_at=NOW):
    return {
        "status": "ok",
        "symbol": symbol,
        "price": "100",
        "currency": "USD",
        "provider": "isolated_fixture",
        "observed_at": observed_at,
    }


@pytest.mark.asyncio
async def test_same_symbol_fetched_only_once():
    upstream = AsyncMock(return_value=quote())
    load = make_transaction_quote_loader(upstream)

    first = await load("AAPL")
    second = await load(" aapl ")

    assert first == second
    assert first["observed_at"] == NOW
    upstream.assert_awaited_once_with("AAPL")


@pytest.mark.asyncio
async def test_different_symbols_fetched_independently():
    upstream = AsyncMock(side_effect=lambda s: quote(s))
    load = make_transaction_quote_loader(upstream)

    a = await load("AAPL")
    m = await load("MSFT")

    assert a["symbol"] == "AAPL"
    assert m["symbol"] == "MSFT"
    assert upstream.await_count == 2


@pytest.mark.asyncio
async def test_no_cross_transaction_reuse():
    upstream = AsyncMock(return_value=quote())

    first = make_transaction_quote_loader(upstream)
    second = make_transaction_quote_loader(upstream)

    await first("AAPL")
    await second("AAPL")

    assert upstream.await_count == 2


@pytest.mark.asyncio
async def test_cached_quote_cannot_be_mutated():
    upstream = AsyncMock(return_value=quote())
    load = make_transaction_quote_loader(upstream)

    first = await load("AAPL")
    first["price"] = "999"
    assert (await load("AAPL"))["price"] == "100"
    upstream.assert_awaited_once()


@pytest.mark.asyncio
async def test_missing_source_quote_rejected():
    upstream = AsyncMock(return_value=None)
    load = make_transaction_quote_loader(upstream)

    with pytest.raises(
        TransactionQuoteUnavailable, match="quote_unavailable"
    ):
        await load("AAPL")


@pytest.mark.asyncio
async def test_cached_quote_still_subject_to_freshness():
    upstream = AsyncMock(return_value=quote(
        observed_at=NOW - timedelta(seconds=301)
    ))
    load = make_transaction_quote_loader(upstream)

    await load("AAPL")
    reused = await load("AAPL")

    with pytest.raises(
        PaperFillUnavailable,
        match="execution_quote_stale_or_future",
    ):
        validate_transaction_fill(
            symbol="AAPL",
            action="buy",
            allocated_capital="500",
            fill_price="100",
            commission="1",
            account_currency="USD",
            execution_quote=reused,
            positions=[],
            now=NOW,
            max_slippage_bps="50",
        )
    upstream.assert_awaited_once()


def test_ledger_shared_binding_contract():
    import inspect
    from backend.app.stacks.journal_ledger import ledger

    source = inspect.getsource(ledger.save_log)

    assert (
        "transaction_quote_loader = make_transaction_quote_loader("
        in source
    )
    assert "quote_loader=transaction_quote_loader" in source
    assert "execution_quote = await transaction_quote_loader(" in source
    assert "quote_loader=get_risk_valuation_quote," not in source


def test_financial_gate_order_is_preserved():
    import inspect
    from backend.app.stacks.journal_ledger import ledger

    source = inspect.getsource(ledger.save_log)
    sequence = [
        "SELECT pg_advisory_xact_lock(742618390125)",
        "transaction_quote_loader = make_transaction_quote_loader(",
        "transaction_valuation = (",
        "transaction_fill_decision = validate_transaction_fill(",
        "transaction_risk_decision = (",
        "paper_execution_financial_risk_not_qualified",
        "new_order = OrderHistory(",
    ]
    offsets = [source.index(s) for s in sequence]
    assert offsets == sorted(offsets)
    assert '"executed" in status.casefold()' in source

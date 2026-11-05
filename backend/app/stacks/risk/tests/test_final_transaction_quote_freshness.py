from datetime import datetime, timedelta, timezone

import pytest

from backend.app.stacks.risk.final_transaction_quote_freshness import (
    FinalTransactionQuoteUnavailable,
    validate_final_transaction_quote_freshness,
)


NOW = datetime(2026, 10, 14, tzinfo=timezone.utc)


def mark(symbol="AAPL", age=30):
    return {
        "symbol": symbol,
        "price": "100",
        "currency": "USD",
        "provider": "controlled_fixture",
        "observed_at": (
            NOW - timedelta(seconds=age)
        ).isoformat(),
    }


def execution(symbol="AAPL", age=30):
    return {
        "status": "ok",
        "symbol": symbol,
        "price": "100",
        "currency": "USD",
        "provider": "controlled_fixture",
        "observed_at": NOW - timedelta(seconds=age),
    }


def check(*, positions=None, marks=None, quote=None, now=NOW):
    return validate_final_transaction_quote_freshness(
        positions=(
            [{"symbol": "AAPL", "shares_quantity": "1"},
             {"symbol": "MSFT", "shares_quantity": "10"}]
            if positions is None else positions
        ),
        marks=(
            [mark("AAPL"), mark("MSFT")]
            if marks is None else marks
        ),
        execution_quote=execution() if quote is None else quote,
        symbol="AAPL",
        account_currency="USD",
        now=now,
    )


def test_valid_held_and_execution_quotes():
    result = check()
    assert result["status"] == "validated"
    assert result["marked_position_count"] == 2
    assert result["execution_authorized"] is False


def test_expired_other_holding():
    with pytest.raises(
        FinalTransactionQuoteUnavailable,
        match="final_quote_stale_or_future",
    ):
        check(marks=[mark("AAPL"), mark("MSFT", 301)])


def test_expired_execution_quote():
    with pytest.raises(
        FinalTransactionQuoteUnavailable,
        match="final_quote_stale_or_future",
    ):
        check(quote=execution(age=301))


def test_future_held_quote():
    with pytest.raises(
        FinalTransactionQuoteUnavailable,
        match="final_quote_stale_or_future",
    ):
        check(marks=[mark("AAPL", -1), mark("MSFT")])


def test_missing_position_mark():
    with pytest.raises(
        FinalTransactionQuoteUnavailable,
        match="final_mark_coverage_mismatch",
    ):
        check(marks=[mark("AAPL")])


def test_unexpected_position_mark():
    with pytest.raises(
        FinalTransactionQuoteUnavailable,
        match="final_mark_unexpected_symbol",
    ):
        check(marks=[mark("AAPL"), mark("NVDA")])


def test_duplicate_mark():
    with pytest.raises(
        FinalTransactionQuoteUnavailable,
        match="final_mark_duplicate_symbol",
    ):
        check(marks=[mark("AAPL"), mark("AAPL"), mark("MSFT")])


def test_execution_symbol_mismatch():
    with pytest.raises(
        FinalTransactionQuoteUnavailable,
        match="final_quote_symbol_mismatch",
    ):
        check(quote=execution("MSFT"))


def test_missing_mark_timestamp():
    bad = mark("MSFT")
    bad.pop("observed_at")

    with pytest.raises(
        FinalTransactionQuoteUnavailable,
        match="final_quote_timestamp_invalid",
    ):
        check(marks=[mark("AAPL"), bad])


def test_empty_inventory_requires_no_marks_but_execution_quote():
    result = check(positions=[], marks=[])
    assert result["marked_position_count"] == 0
    assert result["execution_authorized"] is False


def test_policy_delay_expires_original_observations():
    with pytest.raises(
        FinalTransactionQuoteUnavailable,
        match="final_quote_stale_or_future",
    ):
        check(now=NOW + timedelta(seconds=280))


def test_final_gate_precedes_blockade_and_persistence():
    import inspect
    from backend.app.stacks.journal_ledger import ledger

    source = inspect.getsource(ledger.save_log)

    ordered = [
        "transaction_risk_decision = (",
        "final_quote_decision = (",
        "paper_execution_financial_risk_not_qualified",
        "new_order = OrderHistory(",
    ]

    offsets = [source.index(item) for item in ordered]
    assert offsets == sorted(offsets)
    assert 'marks=transaction_valuation["marks"]' in source
    assert "positions=authoritative_inventory" in source
    assert "execution_quote=execution_quote" in source

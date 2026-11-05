from __future__ import annotations

import ast
from pathlib import Path


LEDGER = (
    Path(__file__).resolve().parents[2]
    / "journal_ledger" / "ledger.py"
)


def source():
    return LEDGER.read_text()


def save_log_ast():
    tree = ast.parse(source())
    return next(
        node for node in tree.body
        if isinstance(node, ast.AsyncFunctionDef)
        and node.name == "save_log"
    )


def test_valuation_is_after_lock_and_before_blockade():
    data = source()
    parts = [
        "SELECT pg_advisory_xact_lock(742618390125)",
        "if existing is not None:",
        "authoritative_cash = await calculate_cash_in_session",
        "authoritative_inventory = await read_inventory_in_session",
        "FROM paper_equity_high_water ",
        "transaction_valuation = (",
        "paper_execution_financial_risk_not_qualified",
        "new_order = OrderHistory(",
    ]
    offsets = [data.index(part) for part in parts]
    assert offsets == sorted(offsets)


def test_valuation_uses_same_transaction_and_owner():
    calls = [
        node for node in ast.walk(save_log_ast())
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "read_transaction_verified_equity"
    ]
    assert len(calls) == 1
    kwargs = {
        kw.arg: ast.unparse(kw.value)
        for kw in calls[0].keywords
    }
    assert kwargs["session"] == "session"
    assert kwargs["user_id"] == "normalized_user_id"
    assert kwargs["cash_currency"] == "account_currency"


def test_missing_currency_cannot_succeed():
    data = source()
    assert "if len(currency_rows) != 1:" in data
    assert "paper_account_currency_unverified" in data
    assert "WHERE user_id = :owner " in data
    assert "FOR UPDATE" in data


def test_quote_source_does_not_invent_observation_time():
    data = source()
    assert (
        "transaction_quote_loader = make_transaction_quote_loader("
        in data
    )
    assert "get_risk_valuation_quote" in data
    assert "quote_loader=transaction_quote_loader" in data
    assert "execution_quote = await transaction_quote_loader(" in data
    assert "observed_at=datetime.now" not in data
    assert "timestamp=datetime.now" not in data


def test_executed_orders_remain_blocked():
    nodes = [
        node for node in ast.walk(save_log_ast())
        if isinstance(node, ast.Raise)
        and node.exc is not None
        and "paper_execution_financial_risk_not_qualified"
        in ast.unparse(node.exc)
    ]
    assert len(nodes) == 1

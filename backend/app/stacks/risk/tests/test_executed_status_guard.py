from __future__ import annotations

import ast
import inspect
from unittest.mock import patch

import pytest

import backend.app.stacks.journal_ledger.ledger as ledger


@pytest.mark.parametrize("status", [
    "EXECUTED",
    "Executed",
    "eXeCuTeD",
    " executed",
    "executed ",
    " EXECUTED ",
    "ExEcUtEd\t",
    "ExEcUtEd\\t",
    "executed\n",
    "executed\r",
    "executed_extra",
])
async def test_executed_alias_rejected_before_database(status):
    trade = {
        "symbol": "AAPL",
        "signal": "buy",
        "status": status,
        "allocated_capital": "100",
        "slippage_price": "100",
        "commission_paid": "1",
    }

    with patch.object(
        ledger,
        "async_session",
        side_effect=AssertionError("Database accessed"),
    ):
        with pytest.raises(
            ValueError,
            match="paper_executed_status_noncanonical",
        ):
            await ledger.save_log(trade, user_id="owner-A")


@pytest.mark.parametrize("status", [
    None, "", "  ", 123, True,
])
async def test_invalid_status_rejected_before_database(status):
    trade = {
        "symbol": "AAPL",
        "signal": "buy",
        "status": status,
    }

    with patch.object(
        ledger,
        "async_session",
        side_effect=AssertionError("Database accessed"),
    ):
        with pytest.raises(
            ValueError,
            match="paper_trade_status_invalid",
        ):
            await ledger.save_log(trade, user_id="owner-A")


def test_guard_precedes_transaction_and_replay():
    source = inspect.getsource(ledger.save_log)
    assert source.index(
        '"executed" in status.casefold()'
    ) < source.index(
        "async with async_session() as session:"
    )


def test_canonical_execution_remains_blocked():
    source = inspect.getsource(ledger.save_log)
    tree = ast.parse(source)
    fn = tree.body[0]

    guards = [
        node for node in ast.walk(fn)
        if isinstance(node, ast.If)
        and ast.unparse(node.test) == "status == 'executed'"
        and any(
            isinstance(child, ast.Raise)
            and child.exc is not None
            and "paper_execution_financial_risk_not_qualified"
            in ast.unparse(child.exc)
            for child in ast.walk(node)
        )
    ]

    assert len(guards) == 1
    assert source.index(
        "paper_execution_financial_risk_not_qualified"
    ) < source.index("new_order = OrderHistory(")

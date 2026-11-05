from __future__ import annotations

import ast
import inspect

from backend.app.stacks.journal_ledger.ledger import save_log


def test_fill_validation_stays_within_ledger_transaction():
    source = inspect.getsource(save_log)
    assert source.index(
        "async with session.begin():"
    ) < source.index(
        "transaction_fill_decision = validate_transaction_fill("
    )


def test_authoritative_inventory_and_actual_fill_are_used():
    source = inspect.getsource(save_log)
    for field in (
        "positions=authoritative_inventory",
        "allocated_capital=allocated_capital",
        "fill_price=slippage_price",
        "commission=commission_paid",
        "account_currency=account_currency",
    ):
        assert field in source


def test_no_slippage_setting_means_no_approval():
    source = inspect.getsource(save_log)
    assert "NEUROVEST_PAPER_MAX_SLIPPAGE_BPS" in source
    assert "paper_slippage_limit_unconfigured" in source


def test_quote_validation_precedes_policy_and_blockade():
    source = inspect.getsource(save_log)
    ordered = [
        "transaction_fill_decision = validate_transaction_fill(",
        "transaction_risk_decision = (",
        "paper_execution_financial_risk_not_qualified",
        "new_order = OrderHistory(",
    ]
    offsets = [source.index(value) for value in ordered]
    assert offsets == sorted(offsets)


def test_execution_gate_still_unconditional_for_executed():
    source = inspect.getsource(save_log)
    tree = ast.parse(source)
    fn = tree.body[0]

    matches = [
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
    assert len(matches) == 1
    assert '"executed" in status.casefold()' in source

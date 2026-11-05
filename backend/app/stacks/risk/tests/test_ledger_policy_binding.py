from __future__ import annotations

import ast
from pathlib import Path


LEDGER = (
    Path(__file__).resolve().parents[2]
    / "journal_ledger" / "ledger.py"
)


def source():
    return LEDGER.read_text()


def save_ast():
    tree = ast.parse(source())
    return next(
        node for node in tree.body
        if isinstance(node, ast.AsyncFunctionDef)
        and node.name == "save_log"
    )


def test_policy_is_inside_commit_boundary():
    parts = [
        "SELECT pg_advisory_xact_lock(742618390125)",
        "if existing is not None:",
        "transaction_valuation = (",
        "transaction_risk_decision = (",
        "paper_execution_financial_risk_not_qualified",
        "new_order = OrderHistory(",
    ]
    offsets = [source().index(part) for part in parts]
    assert offsets == sorted(offsets)


def test_coordinator_uses_same_session_and_owner():
    calls = [
        node for node in ast.walk(save_ast())
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id
            == "evaluate_transactional_financial_policy"
    ]

    assert len(calls) == 1

    kwargs = {
        kw.arg: ast.unparse(kw.value)
        for kw in calls[0].keywords
    }

    assert kwargs["session"] == "session"
    assert kwargs["owner"] == "normalized_user_id"
    assert kwargs["currency"] == "account_currency"
    assert kwargs["verified_equity"] == "transaction_valuation"
    assert kwargs["limits"] == "configured_limits"
    assert kwargs["order_value"] == "allocated_capital"
    assert kwargs["commission"] == "commission_paid"


def test_no_hardcoded_risk_limits():
    data = source()
    assert "NEUROVEST_PAPER_MAX_ORDER_VALUE" in data
    assert "NEUROVEST_PAPER_MAX_GROSS_EXPOSURE" in data
    assert "NEUROVEST_PAPER_MAX_DRAWDOWN_FRACTION" in data
    assert "paper_financial_limits_unconfigured" in data


def test_unapproved_decision_fails_closed():
    data = source()
    assert 'transaction_risk_decision.get("approved")' in data
    assert "paper_financial_policy_rejected" in data
    assert "paper_financial_action_unsupported" in data


def test_execution_blockade_remains():
    raises = [
        node for node in ast.walk(save_ast())
        if isinstance(node, ast.Raise)
        and node.exc is not None
        and "paper_execution_financial_risk_not_qualified"
            in ast.unparse(node.exc)
    ]
    assert len(raises) == 1

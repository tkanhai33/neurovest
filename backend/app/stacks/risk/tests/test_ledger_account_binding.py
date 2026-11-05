from __future__ import annotations

import ast
from pathlib import Path


LEDGER = (
    Path(__file__).resolve().parents[2]
    / "journal_ledger" / "ledger.py"
)


def source():
    return LEDGER.read_text()


def test_account_reads_follow_advisory_lock_and_replay():
    data = source()

    sections = [
        "SELECT pg_advisory_xact_lock(742618390125)",
        "if existing is not None:",
        "authoritative_cash = await calculate_cash_in_session",
        "authoritative_inventory = await read_inventory_in_session",
        "paper_execution_financial_risk_not_qualified",
        "new_order = OrderHistory(",
    ]

    offsets = [data.index(section) for section in sections]
    assert offsets == sorted(offsets)


def test_both_readers_use_same_session_and_owner():
    tree = ast.parse(source())
    save = next(
        node for node in tree.body
        if isinstance(node, ast.AsyncFunctionDef)
        and node.name == "save_log"
    )

    calls = [
        node for node in ast.walk(save)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id in {
            "calculate_cash_in_session",
            "read_inventory_in_session",
        }
    ]

    assert len(calls) == 2

    for call in calls:
        kwargs = {
            item.arg: ast.unparse(item.value)
            for item in call.keywords
        }
        assert kwargs["session"] == "session"
        assert kwargs["user_id"] == "normalized_user_id"


def test_execution_still_unconditionally_blocked():
    tree = ast.parse(source())
    save = next(
        node for node in tree.body
        if isinstance(node, ast.AsyncFunctionDef)
        and node.name == "save_log"
    )

    blocks = [
        node for node in ast.walk(save)
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

    assert len(blocks) == 1
    assert "new_order = OrderHistory(" in source()

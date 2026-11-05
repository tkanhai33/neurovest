from __future__ import annotations

import ast
from pathlib import Path


LEDGER = (
    Path(__file__).resolve().parents[2]
    / "journal_ledger" / "ledger.py"
)


def _source():
    return LEDGER.read_text()


def test_guard_is_inside_postgres_transaction():
    source = _source()

    transaction = source.index(
        "async with session.begin():"
    )
    lock = source.index(
        "SELECT pg_advisory_xact_lock(742618390125)"
    )
    guard = source.index(
        "paper_execution_financial_risk_not_qualified"
    )
    insert = source.index(
        "new_order = OrderHistory("
    )
    flush = source.index(
        "await session.flush()"
    )

    assert transaction < lock < guard < insert < flush


def test_guard_blocks_executed_before_inventory_mutation():
    tree = ast.parse(_source())

    save_log = next(
        node for node in tree.body
        if isinstance(node, ast.AsyncFunctionDef)
        and node.name == "save_log"
    )

    blockers = [
        node for node in ast.walk(save_log)
        if isinstance(node, ast.Raise)
        and node.exc is not None
        and "paper_execution_financial_risk_not_qualified"
        in ast.unparse(node.exc)
    ]

    assert len(blockers) == 1

    blocker = blockers[0]

    assert any(
        isinstance(node, ast.If)
        and isinstance(node.test, ast.Compare)
        and ast.unparse(node.test)
            == "status == 'executed'"
        and blocker in list(ast.walk(node))
        for node in ast.walk(save_log)
    )


def test_idempotency_replay_precedes_guard():
    source = _source()

    assert source.index(
        "if existing is not None:"
    ) < source.index(
        "paper_execution_financial_risk_not_qualified"
    )


def test_guard_does_not_enable_live_execution():
    source = _source()
    assert "paper_execution_financial_risk_not_qualified" in source
    assert "execution_control.assert_paper_execution_allowed()" in source

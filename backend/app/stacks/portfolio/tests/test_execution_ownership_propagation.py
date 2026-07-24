from __future__ import annotations

import ast
from pathlib import Path

import pytest

from backend.app.stacks.execution import (
    paper_broker,
)
from backend.app.stacks.journal_ledger import (
    ledger,
)


@pytest.mark.asyncio
async def test_paper_execution_rejects_empty_user_id() -> None:
    with pytest.raises(
        ValueError,
        match="user_id cannot be empty",
    ):
        await paper_broker.process_portfolio_output(
            [],
            {
                "symbol": "AAPL",
                "signal": "hold",
            },
            user_id="",
        )


@pytest.mark.asyncio
async def test_ledger_rejects_empty_user_id() -> None:
    with pytest.raises(
        ValueError,
        match="user_id cannot be empty",
    ):
        await ledger.save_log(
            {
                "symbol": "AAPL",
                "signal": "hold",
                "status": "blocked_by_risk",
            },
            user_id="",
        )


def test_all_paper_broker_save_log_calls_propagate_user_id() -> None:
    path = Path(
        "backend/app/stacks/execution/paper_broker.py"
    )

    tree = ast.parse(
        path.read_text(
            encoding="utf-8",
        )
    )

    calls = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        if (
            isinstance(node.func, ast.Name)
            and node.func.id == "save_log"
        ):
            calls.append(node)

    assert calls

    for call in calls:
        keyword_names = {
            keyword.arg
            for keyword in call.keywords
        }

        assert "user_id" in keyword_names


def test_ledger_inventory_lookup_is_account_scoped() -> None:
    text = Path(
        "backend/app/stacks/journal_ledger/ledger.py"
    ).read_text(
        encoding="utf-8",
    )

    assert (
        "PortfolioInventory.user_id"
        in text
    )

    assert (
        "PortfolioInventory.symbol"
        in text
    )

    assert (
        "user_id=normalized_user_id"
        in text
    )


def test_order_history_write_is_account_scoped() -> None:
    text = Path(
        "backend/app/stacks/journal_ledger/ledger.py"
    ).read_text(
        encoding="utf-8",
    )

    order_start = text.index(
        "new_order = OrderHistory("
    )

    order_end = text.index(
        "session.add(new_order)",
        order_start,
    )

    order_block = text[
        order_start:
        order_end
    ]

    assert (
        "user_id=normalized_user_id"
        in order_block
    )

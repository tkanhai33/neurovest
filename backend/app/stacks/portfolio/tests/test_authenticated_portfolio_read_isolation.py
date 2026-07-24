from __future__ import annotations

import ast
from pathlib import Path

import pytest

from backend.app.stacks.journal_ledger.ledger import (
    read_max_allocated_capital,
)

from backend.app.stacks.portfolio.accounting import (
    calculate_live_portfolio_equity,
)


MAIN = Path(
    "backend/app/main.py"
)

ACCOUNTING = Path(
    "backend/app/stacks/portfolio/accounting.py"
)

LEDGER = Path(
    "backend/app/stacks/journal_ledger/ledger.py"
)

DRAWDOWN = Path(
    "backend/app/stacks/risk/drawdown_guard.py"
)

BROKER = Path(
    "backend/app/stacks/execution/paper_broker.py"
)


def function_source(
    path: Path,
    name: str,
) -> str:
    tree = ast.parse(
        path.read_text(
            encoding="utf-8",
        )
    )

    node = next(
        (
            item
            for item in ast.walk(tree)
            if (
                isinstance(
                    item,
                    (
                        ast.FunctionDef,
                        ast.AsyncFunctionDef,
                    ),
                )
                and item.name == name
            )
        ),
        None,
    )

    assert node is not None

    return ast.unparse(
        node
    )


@pytest.mark.asyncio
async def test_accounting_rejects_empty_owner() -> None:
    with pytest.raises(
        ValueError,
        match="user_id cannot be empty",
    ):
        await calculate_live_portfolio_equity(
            user_id=" ",
        )


@pytest.mark.asyncio
async def test_ledger_read_rejects_empty_owner() -> None:
    with pytest.raises(
        ValueError,
        match="user_id cannot be empty",
    ):
        await read_max_allocated_capital(
            user_id="",
        )


def test_position_route_is_authenticated_and_scoped() -> None:
    source = function_source(
        MAIN,
        "get_active_positions",
    )

    assert (
        "require_authenticated_principal"
        in source
    )

    assert (
        "PortfolioInventory.user_id == principal.subject"
        in source
    )


def test_orders_route_is_authenticated_and_scoped() -> None:
    source = function_source(
        MAIN,
        "get_orders",
    )

    assert (
        "require_authenticated_principal"
        in source
    )

    assert (
        "OrderHistory.user_id == principal.subject"
        in source
    )


def test_analytics_route_is_authenticated_and_scoped() -> None:
    source = function_source(
        MAIN,
        "get_analytics",
    )

    assert (
        "require_authenticated_principal"
        in source
    )

    assert (
        "OrderHistory.user_id == principal.subject"
        in source
    )


def test_accounting_is_owner_scoped() -> None:
    source = function_source(
        ACCOUNTING,
        "calculate_live_portfolio_equity",
    )

    assert (
        "OrderHistory.user_id == normalized_user_id"
        in source
    )


def test_max_allocation_is_owner_scoped() -> None:
    source = function_source(
        LEDGER,
        "read_max_allocated_capital",
    )

    assert (
        "OrderHistory.user_id == normalized_user_id"
        in source
    )


def test_risk_propagates_owner() -> None:
    source = function_source(
        DRAWDOWN,
        "healthcheck",
    )

    assert (
        "read_max_allocated_capital(user_id=user_id)"
        in source
    )


def test_execution_propagates_owner() -> None:
    source = function_source(
        BROKER,
        "process_portfolio_output",
    )

    assert (
        "calculate_live_portfolio_equity(user_id=user_id)"
        in source
    )

    assert (
        "drawdown_healthcheck(live_capital, user_id=user_id)"
        in source
    )

from __future__ import annotations

import ast
from pathlib import Path

import pytest
from sqlalchemy import inspect

from backend.app.stacks.db_runtime.database import (
    engine,
)


LEDGER = Path(
    "backend/app/stacks/journal_ledger/ledger.py"
)


def test_orm_enforces_owned_rows() -> None:
    tree = ast.parse(
        LEDGER.read_text(
            encoding="utf-8",
        )
    )

    classes = {
        node.name: ast.unparse(node)
        for node in ast.walk(tree)
        if isinstance(
            node,
            ast.ClassDef,
        )
    }

    order_source = classes[
        "OrderHistory"
    ]

    inventory_source = classes[
        "PortfolioInventory"
    ]

    assert (
        "user_id: Mapped[str]"
        in order_source
    )

    assert (
        "user_id: Mapped[str]"
        in inventory_source
    )

    assert (
        "nullable=False"
        in order_source
    )

    assert (
        "nullable=False"
        in inventory_source
    )

    assert (
        "uq_portfolio_inventory_user_id_symbol"
        in inventory_source
    )

    assert (
        "unique=True"
        not in inventory_source
    )


@pytest.mark.asyncio
async def test_live_database_enforces_owned_rows() -> None:
    await engine.dispose(close=False)

    async with engine.connect() as connection:
        def inspect_schema(sync_connection):
            inspector = inspect(sync_connection)

            return {
                "orders": inspector.get_columns(
                    "order_history"
                ),
                "inventory": inspector.get_columns(
                    "portfolio_inventory"
                ),
                "uniques":
                    inspector.get_unique_constraints(
                        "portfolio_inventory"
                    ),
            }

        schema = await connection.run_sync(
            inspect_schema
        )

    order_owner = next(
        column
        for column in schema["orders"]
        if column["name"] == "user_id"
    )

    inventory_owner = next(
        column
        for column in schema["inventory"]
        if column["name"] == "user_id"
    )

    constraints = {
        constraint["name"]:
            constraint["column_names"]
        for constraint in schema["uniques"]
    }

    assert order_owner[
        "nullable"
    ] is False

    assert inventory_owner[
        "nullable"
    ] is False

    assert constraints[
        "uq_portfolio_inventory_user_id_symbol"
    ] == [
        "user_id",
        "symbol",
    ]

    assert (
        "portfolio_inventory_symbol_key"
        not in constraints
    )

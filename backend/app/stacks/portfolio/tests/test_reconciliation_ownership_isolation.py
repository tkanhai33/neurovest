from __future__ import annotations

import ast
from pathlib import Path

import pytest

from backend.app.stacks.portfolio.reconciliation import (
    run_reconciliation_audit,
    start_periodic_reconciliation_daemon,
)


RECONCILIATION_PATH = Path(
    "backend/app/stacks/portfolio/reconciliation.py"
)

MAIN_PATH = Path(
    "backend/app/main.py"
)


def _function(
    tree: ast.AST,
    name: str,
) -> ast.AsyncFunctionDef:
    function = next(
        (
            node
            for node in ast.walk(
                tree
            )
            if (
                isinstance(
                    node,
                    ast.AsyncFunctionDef,
                )
                and node.name
                == name
            )
        ),
        None,
    )

    assert function is not None

    return function


def _calls(
    tree: ast.AST,
    name: str,
) -> list[ast.Call]:
    return [
        node
        for node in ast.walk(
            tree
        )
        if (
            isinstance(
                node,
                ast.Call,
            )
            and (
                (
                    isinstance(
                        node.func,
                        ast.Name,
                    )
                    and node.func.id
                    == name
                )
                or (
                    isinstance(
                        node.func,
                        ast.Attribute,
                    )
                    and node.func.attr
                    == name
                )
            )
        )
    ]


@pytest.mark.asyncio
async def test_reconciliation_rejects_empty_owner() -> None:
    with pytest.raises(
        ValueError,
        match="user_id cannot be empty",
    ):
        await run_reconciliation_audit(
            user_id="   ",
        )


@pytest.mark.asyncio
async def test_daemon_rejects_empty_owner_before_loop() -> None:
    with pytest.raises(
        ValueError,
        match="user_id cannot be empty",
    ):
        await start_periodic_reconciliation_daemon(
            user_id="",
            interval_seconds=0,
        )


def test_reconciliation_inventory_query_is_owner_scoped() -> None:
    tree = ast.parse(
        RECONCILIATION_PATH.read_text(
            encoding="utf-8",
        )
    )

    function = _function(
        tree,
        "run_reconciliation_audit",
    )

    source = ast.unparse(
        function
    )

    assert (
        "PortfolioInventory.user_id == normalized_user_id"
        in source
    )

    assert (
        "select(PortfolioInventory)"
        in source
    )


def test_reconciliation_order_query_is_owner_and_symbol_scoped() -> None:
    tree = ast.parse(
        RECONCILIATION_PATH.read_text(
            encoding="utf-8",
        )
    )

    function = _function(
        tree,
        "run_reconciliation_audit",
    )

    source = ast.unparse(
        function
    )

    assert (
        "OrderHistory.user_id == normalized_user_id"
        in source
    )

    assert (
        "OrderHistory.symbol == position.symbol"
        in source
    )

    assert (
        "OrderHistory.status == 'executed'"
        in source
    )


def test_daemon_propagates_owner_to_each_audit() -> None:
    tree = ast.parse(
        RECONCILIATION_PATH.read_text(
            encoding="utf-8",
        )
    )

    function = _function(
        tree,
        "start_periodic_reconciliation_daemon",
    )

    calls = _calls(
        function,
        "run_reconciliation_audit",
    )

    assert len(calls) == 1

    keywords = {
        keyword.arg:
            ast.unparse(
                keyword.value
            )
        for keyword in calls[
            0
        ].keywords
    }

    assert keywords.get(
        "user_id"
    ) == "normalized_user_id"


def test_main_propagates_owner_to_both_runtime_callers() -> None:
    tree = ast.parse(
        MAIN_PATH.read_text(
            encoding="utf-8",
        )
    )

    audit_calls = _calls(
        tree,
        "run_reconciliation_audit",
    )

    daemon_calls = _calls(
        tree,
        "start_periodic_reconciliation_daemon",
    )

    assert len(
        audit_calls
    ) == 1

    assert len(
        daemon_calls
    ) == 1

    audit_keywords = {
        keyword.arg:
            ast.unparse(
                keyword.value
            )
        for keyword in audit_calls[
            0
        ].keywords
    }

    daemon_keywords = {
        keyword.arg:
            ast.unparse(
                keyword.value
            )
        for keyword in daemon_calls[
            0
        ].keywords
    }

    assert audit_keywords.get(
        "user_id"
    ) == "principal.subject"

    assert daemon_keywords.get(
        "user_id"
    ) == "reconciliation_owner_id"

    source = MAIN_PATH.read_text(
        encoding="utf-8",
    )

    assert (
        "reconciliation_owner_id = ("
        in source
    )

    assert (
        "await resolve_reconciliation_owner_id()"
        in source
    )

    assert (
        "if reconciliation_owner_id is not None:"
        in source
    )

    assert (
        "periodic reconciliation daemon skipped"
        in source
    )

    assert (
        "user_id=await "
        "resolve_reconciliation_owner_id()"
        not in source
    )

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from backend.app.stacks.db_runtime.transaction_guard import (
    transaction_guard,
)


class FakeSession:
    def __init__(
        self,
    ) -> None:
        self.rollback_calls = 0

    async def rollback(
        self,
    ) -> None:
        self.rollback_calls += 1


@pytest.mark.asyncio
async def test_guard_does_not_rollback_successful_scope() -> None:
    session = FakeSession()

    async with transaction_guard(
        session
    ):
        value = 42

    assert value == 42
    assert session.rollback_calls == 0


@pytest.mark.asyncio
async def test_guard_rolls_back_write_failure_and_reraises() -> None:
    session = FakeSession()

    with pytest.raises(
        RuntimeError,
        match="write failed",
    ):
        async with transaction_guard(
            session
        ):
            raise RuntimeError(
                "write failed"
            )

    assert session.rollback_calls == 1


@pytest.mark.asyncio
async def test_guard_rolls_back_commit_failure_and_reraises() -> None:
    session = FakeSession()

    class CommitFailure(
        RuntimeError
    ):
        pass

    with pytest.raises(
        CommitFailure,
    ):
        async with transaction_guard(
            session
        ):
            raise CommitFailure(
                "commit failed"
            )

    assert session.rollback_calls == 1


@pytest.mark.asyncio
async def test_guard_rolls_back_cancellation() -> None:
    session = FakeSession()

    class Cancellation(
        BaseException
    ):
        pass

    with pytest.raises(
        Cancellation,
    ):
        async with transaction_guard(
            session
        ):
            raise Cancellation()

    assert session.rollback_calls == 1


TARGETS = {
    Path(
        "backend/app/stacks/learning_research/"
        "research_loader.py"
    ): {
        "add_research",
    },
    Path(
        "backend/app/stacks/market_data/"
        "yfinance_ingestor.py"
    ): {
        "load_full_history",
        "update_live_price",
    },
}


def _call_terminal(
    node: ast.Call,
) -> str | None:
    if isinstance(
        node.func,
        ast.Name,
    ):
        return node.func.id

    if isinstance(
        node.func,
        ast.Attribute,
    ):
        return node.func.attr

    return None


@pytest.mark.parametrize(
    (
        "path",
        "function_name",
    ),
    [
        (
            path,
            function_name,
        )
        for path, functions
        in TARGETS.items()
        for function_name
        in sorted(
            functions
        )
    ],
)
def test_approved_write_path_uses_transaction_guard(
    path: Path,
    function_name: str,
) -> None:
    source = path.read_text(
        encoding="utf-8"
    )

    tree = ast.parse(
        source,
        filename=str(
            path
        ),
    )

    functions = [
        node
        for node in tree.body
        if (
            isinstance(
                node,
                ast.AsyncFunctionDef,
            )
            and node.name == function_name
        )
    ]

    assert len(
        functions
    ) == 1

    function = functions[
        0
    ]

    guard_calls = [
        node
        for node in ast.walk(
            function
        )
        if (
            isinstance(
                node,
                ast.Call,
            )
            and _call_terminal(
                node
            )
            == "transaction_guard"
        )
    ]

    commit_calls = [
        node
        for node in ast.walk(
            function
        )
        if (
            isinstance(
                node,
                ast.Call,
            )
            and _call_terminal(
                node
            )
            == "commit"
        )
    ]

    assert len(
        guard_calls
    ) == 1

    assert len(
        commit_calls
    ) >= 1


def test_legacy_market_schema_remains_isolated() -> None:
    source = Path(
        "backend/app/stacks/db_model/"
        "market_schema.py"
    ).read_text(
        encoding="utf-8"
    )

    assert (
        "create_async_engine"
        not in source
    )

    assert (
        "async_sessionmaker"
        not in source
    )

    assert (
        "backend.app.stacks.db_runtime.database "
        "import Base"
        not in source
    )

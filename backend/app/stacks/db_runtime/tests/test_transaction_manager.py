from __future__ import annotations

import pytest

from backend.app.stacks.db_runtime.transaction_manager import (
    TransactionManager,
)


class FakeSession:
    def __init__(
        self,
        *,
        fail_flush: bool = False,
        fail_commit: bool = False,
        fail_rollback: bool = False,
    ) -> None:
        self.fail_flush = fail_flush
        self.fail_commit = fail_commit
        self.fail_rollback = fail_rollback

        self.flush_calls = 0
        self.commit_calls = 0
        self.rollback_calls = 0

        self.events: list[
            str
        ] = []

    async def flush(
        self,
    ) -> None:
        self.flush_calls += 1
        self.events.append(
            "flush"
        )

        if self.fail_flush:
            raise RuntimeError(
                "flush failed"
            )

    async def commit(
        self,
    ) -> None:
        self.commit_calls += 1
        self.events.append(
            "commit"
        )

        if self.fail_commit:
            raise RuntimeError(
                "commit failed"
            )

    async def rollback(
        self,
    ) -> None:
        self.rollback_calls += 1
        self.events.append(
            "rollback"
        )

        if self.fail_rollback:
            raise RuntimeError(
                "rollback failed"
            )


@pytest.mark.asyncio
async def test_success_executes_flush_then_commit() -> None:
    session = FakeSession()

    manager = TransactionManager(
        session
    )

    async def operation(
        active_session: FakeSession,
    ) -> str:
        assert active_session is session

        active_session.events.append(
            "operation"
        )

        return "complete"

    result = await manager.execute(
        operation
    )

    assert result == "complete"

    assert session.events == [
        "operation",
        "flush",
        "commit",
    ]

    assert session.rollback_calls == 0


@pytest.mark.asyncio
async def test_operation_failure_rolls_back_and_reraises() -> None:
    session = FakeSession()

    manager = TransactionManager(
        session
    )

    async def operation(
        active_session: FakeSession,
    ) -> None:
        active_session.events.append(
            "operation"
        )

        raise RuntimeError(
            "operation failed"
        )

    with pytest.raises(
        RuntimeError,
        match="operation failed",
    ):
        await manager.execute(
            operation
        )

    assert session.events == [
        "operation",
        "rollback",
    ]

    assert session.flush_calls == 0
    assert session.commit_calls == 0
    assert session.rollback_calls == 1


@pytest.mark.asyncio
async def test_flush_failure_rolls_back_and_reraises() -> None:
    session = FakeSession(
        fail_flush=True
    )

    manager = TransactionManager(
        session
    )

    async def operation(
        active_session: FakeSession,
    ) -> str:
        active_session.events.append(
            "operation"
        )

        return "pending"

    with pytest.raises(
        RuntimeError,
        match="flush failed",
    ):
        await manager.execute(
            operation
        )

    assert session.events == [
        "operation",
        "flush",
        "rollback",
    ]

    assert session.commit_calls == 0
    assert session.rollback_calls == 1


@pytest.mark.asyncio
async def test_commit_failure_rolls_back_and_reraises() -> None:
    session = FakeSession(
        fail_commit=True
    )

    manager = TransactionManager(
        session
    )

    async def operation(
        active_session: FakeSession,
    ) -> str:
        active_session.events.append(
            "operation"
        )

        return "pending"

    with pytest.raises(
        RuntimeError,
        match="commit failed",
    ):
        await manager.execute(
            operation
        )

    assert session.events == [
        "operation",
        "flush",
        "commit",
        "rollback",
    ]

    assert session.rollback_calls == 1


@pytest.mark.asyncio
async def test_non_callable_operation_is_rejected() -> None:
    session = FakeSession()

    manager = TransactionManager(
        session
    )

    with pytest.raises(
        TypeError,
        match="must be callable",
    ):
        await manager.execute(
            None  # type: ignore[arg-type]
        )

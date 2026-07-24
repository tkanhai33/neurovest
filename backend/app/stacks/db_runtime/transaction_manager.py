"""
Canonical transaction-manager contract and implementation.

This component provides one explicit transaction boundary for a caller-
supplied asynchronous database session.

It does not:

- create a session
- own an engine
- retry failed operations
- suppress exceptions
- perform ORM writes by itself
- modify runtime composition
- expose an API route
- enable broker execution
- enable live trading
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Protocol, TypeVar

from backend.app.stacks.db_runtime.transaction_guard import (
    transaction_guard,
)


ResultT = TypeVar(
    "ResultT",
)


class TransactionSession(
    Protocol,
):
    async def flush(
        self,
    ) -> None:
        """Flush pending changes."""

    async def commit(
        self,
    ) -> None:
        """Commit the active transaction."""

    async def rollback(
        self,
    ) -> None:
        """Roll back the active transaction."""


TransactionOperation = Callable[
    [
        TransactionSession,
    ],
    Awaitable[
        ResultT
    ],
]


class TransactionManager:
    """
    Execute exactly one asynchronous operation inside one failure guard.

    Successful execution order:

        operation
        flush
        commit

    Failure behavior:

        rollback
        re-raise original exception

    Commit failures are also rolled back and re-raised.
    """

    def __init__(
        self,
        session: TransactionSession,
    ) -> None:
        self._session = session

    @property
    def session(
        self,
    ) -> TransactionSession:
        return self._session

    async def execute(
        self,
        operation: TransactionOperation[
            ResultT
        ],
    ) -> ResultT:
        if not callable(
            operation
        ):
            raise TypeError(
                "operation must be callable"
            )

        async with transaction_guard(
            self._session
        ):
            result = await operation(
                self._session
            )

            await self._session.flush()
            await self._session.commit()

            return result

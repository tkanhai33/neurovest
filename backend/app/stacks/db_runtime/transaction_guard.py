"""
Canonical asynchronous transaction failure guard.

This helper does not decide when a transaction commits. Existing callers
retain their current commit behavior.

It guarantees that an exception raised anywhere inside the protected
write scope triggers session.rollback() before the original exception
is re-raised.

The guard:

- does not create sessions
- does not commit automatically
- does not retry writes
- does not suppress exceptions
- does not enable broker execution
- does not enable live trading
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator, Protocol, TypeVar


class RollbackCapableSession(
    Protocol,
):
    async def rollback(
        self,
    ) -> None:
        """Roll back the active transaction."""


SessionT = TypeVar(
    "SessionT",
    bound=RollbackCapableSession,
)


@asynccontextmanager
async def transaction_guard(
    session: SessionT,
) -> AsyncIterator[SessionT]:
    """
    Roll back and re-raise when a protected write scope fails.

    Successful scopes are unchanged. The caller remains responsible for
    flush and commit behavior.
    """

    try:
        yield session

    except BaseException:
        await session.rollback()
        raise

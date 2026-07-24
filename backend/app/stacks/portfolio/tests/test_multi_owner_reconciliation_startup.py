from __future__ import annotations

import inspect

import pytest

from backend.app import main
from backend.app.stacks.portfolio import reconciliation


class FakeScalarResult:
    def __init__(
        self,
        values: list[str],
    ) -> None:
        self.values = values

    def scalars(
        self,
    ) -> "FakeScalarResult":
        return self

    def all(
        self,
    ) -> list[str]:
        return self.values


class FakeSession:
    def __init__(
        self,
        responses: list[list[str]],
    ) -> None:
        self.responses = responses
        self.calls = 0

    async def __aenter__(
        self,
    ) -> "FakeSession":
        return self

    async def __aexit__(
        self,
        exc_type,
        exc,
        traceback,
    ) -> None:
        return None

    async def execute(
        self,
        statement,
    ) -> FakeScalarResult:
        response = self.responses[
            self.calls
        ]

        self.calls += 1

        return FakeScalarResult(
            response
        )


@pytest.mark.asyncio
async def test_ambiguous_owner_resolution_returns_none(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = FakeSession(
        [
            ["owner-a"],
            ["owner-b"],
        ]
    )

    monkeypatch.setattr(
        reconciliation,
        "async_session",
        lambda: session,
    )

    result = await reconciliation.resolve_reconciliation_owner_id()

    assert result is None
    assert session.calls == 2


@pytest.mark.asyncio
async def test_single_owner_resolution_returns_owner(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = FakeSession(
        [
            ["owner-a"],
            ["owner-a"],
        ]
    )

    monkeypatch.setattr(
        reconciliation,
        "async_session",
        lambda: session,
    )

    result = await reconciliation.resolve_reconciliation_owner_id()

    assert result == "owner-a"
    assert session.calls == 2


@pytest.mark.asyncio
async def test_empty_owner_resolution_returns_none(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = FakeSession(
        [
            [],
            [],
        ]
    )

    monkeypatch.setattr(
        reconciliation,
        "async_session",
        lambda: session,
    )

    result = await reconciliation.resolve_reconciliation_owner_id()

    assert result is None


def test_lifespan_guards_legacy_reconciliation_daemon() -> None:
    source = inspect.getsource(
        main.lifespan
    )

    assert (
        "reconciliation_owner_id is not None"
        in source
    )

    assert (
        "periodic reconciliation daemon skipped"
        in source
    )

    assert (
        "user_id=reconciliation_owner_id"
        in source
    )


def test_lifespan_does_not_inline_owner_resolution() -> None:
    source = inspect.getsource(
        main.lifespan
    )

    assert (
        "user_id=await resolve_reconciliation_owner_id()"
        not in source
    )

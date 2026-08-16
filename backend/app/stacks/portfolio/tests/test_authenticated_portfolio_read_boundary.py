from __future__ import annotations

from typing import Any
from types import SimpleNamespace

import pytest

from backend.app.stacks.identity_auth.contracts import (
    AuthenticatedPrincipal,
)
from backend.app.stacks.portfolio import (
    portfolio_service,
)


def make_principal(
    subject: str,
) -> AuthenticatedPrincipal:
    return AuthenticatedPrincipal(
        subject=subject,
        token_id="portfolio-test-token",
        claims={
            "sub": subject,
            "role": "user",
        },
    )


@pytest.mark.asyncio
async def test_portfolio_service_scopes_durable_query_to_principal_subject(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    principal = SimpleNamespace(
        subject="owner-123",
    )

    captured = []


    class FakeScalars:

        def all(
            self,
        ):
            return []


    class FakeResult:

        def scalars(
            self,
        ):
            return FakeScalars()


    class FakeSession:

        async def __aenter__(
            self,
        ):
            return self

        async def __aexit__(
            self,
            exc_type,
            exc,
            tb,
        ):
            return False

        async def execute(
            self,
            statement,
        ):
            captured.append(
                statement
            )

            return FakeResult()


    def fake_session_factory():
        return FakeSession()


    monkeypatch.setattr(
        portfolio_service,
        "async_session",
        fake_session_factory,
    )


    result = await (
        portfolio_service
        .get_portfolio_positions_for_api(
            principal
        )
    )


    assert result[
        "status"
    ] == "ok"

    assert result[
        "scope"
    ] == "authenticated_account"

    assert result[
        "provider"
    ] == "portfolio_inventory"

    assert result[
        "positions"
    ] == []

    assert result[
        "count"
    ] == 0

    assert len(
        captured
    ) == 1


    statement = str(
        captured[0]
    )


    assert (
        "portfolio_inventory.user_id"
        in statement
    )

    assert (
        "WHERE portfolio_inventory.user_id"
        in statement
    )



@pytest.mark.asyncio
async def test_portfolio_service_rejects_empty_subject() -> None:
    principal = AuthenticatedPrincipal(
        subject="",
        token_id="portfolio-test-token",
        claims={},
    )

    with pytest.raises(
        ValueError,
        match="subject cannot be empty",
    ):
        await (
            portfolio_service
            .get_portfolio_positions_for_api(
                principal
            )
        )


@pytest.mark.asyncio
async def test_paper_snapshot_rejects_empty_user_id() -> None:
    from backend.app.stacks.execution.paper_broker import (
        get_positions_snapshot,
    )

    with pytest.raises(
        ValueError,
        match="user_id cannot be empty",
    ):
        await get_positions_snapshot(
            user_id=""
        )


@pytest.mark.asyncio
async def test_paper_snapshot_is_explicitly_account_scoped() -> None:
    from backend.app.stacks.execution.paper_broker import (
        get_positions_snapshot,
    )

    result = await get_positions_snapshot(
        user_id="user-account-456"
    )

    assert result == {
        "status": "ok",
        "positions": [],
        "count": 0,
        "provider": "paper_broker",
        "scope": "authenticated_account",
    }

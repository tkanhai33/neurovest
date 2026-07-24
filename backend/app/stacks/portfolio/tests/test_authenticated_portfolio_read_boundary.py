from __future__ import annotations

from typing import Any

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
async def test_portfolio_service_passes_principal_subject(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    async def fake_snapshot(
        *,
        user_id: str,
    ) -> dict[str, object]:
        captured["user_id"] = user_id

        return {
            "status": "ok",
            "positions": [],
            "count": 0,
            "provider": "test",
            "scope": "authenticated_account",
        }

    monkeypatch.setattr(
        portfolio_service,
        "get_positions_snapshot",
        fake_snapshot,
    )

    result = (
        await portfolio_service
        .get_portfolio_positions_for_api(
            make_principal(
                "user-account-123"
            )
        )
    )

    assert (
        captured["user_id"]
        == "user-account-123"
    )

    assert (
        result["scope"]
        == "authenticated_account"
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

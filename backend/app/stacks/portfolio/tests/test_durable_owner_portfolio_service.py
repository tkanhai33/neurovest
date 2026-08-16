from __future__ import annotations

from decimal import Decimal
from types import SimpleNamespace

import pytest

from backend.app.stacks.portfolio import (
    portfolio_service,
)


class FakeScalarResult:

    def __init__(
        self,
        rows,
    ):
        self._rows = rows

    def all(
        self,
    ):
        return list(
            self._rows
        )


class FakeExecuteResult:

    def __init__(
        self,
        rows,
    ):
        self._rows = rows

    def scalars(
        self,
    ):
        return FakeScalarResult(
            self._rows
        )


class FakeSession:

    def __init__(
        self,
        rows,
        captured,
    ):
        self._rows = rows
        self._captured = captured

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
        self._captured.append(
            statement
        )

        return FakeExecuteResult(
            self._rows
        )


@pytest.mark.asyncio
async def test_portfolio_service_reads_durable_owner_inventory(
    monkeypatch: pytest.MonkeyPatch,
) -> None:

    rows = [
        SimpleNamespace(
            id=1,
            user_id="owner-123",
            symbol="TD.TO",
            shares_quantity=Decimal(
                "1.2500000000000000000000000000"
            ),
            average_entry_price=Decimal(
                "100.0000000000000000000000000000"
            ),
            total_cost_basis=Decimal(
                "125.0000000000000000000000000000"
            ),
            realized_pnl=Decimal(
                "0"
            ),
            last_updated=None,
        ),
    ]

    captured = []

    def fake_session_factory():
        return FakeSession(
            rows,
            captured,
        )

    monkeypatch.setattr(
        portfolio_service,
        "async_session",
        fake_session_factory,
    )

    principal = SimpleNamespace(
        subject="owner-123",
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
        "provider"
    ] == "portfolio_inventory"

    assert result[
        "scope"
    ] == "authenticated_account"

    assert result[
        "count"
    ] == 1

    assert len(
        result[
            "positions"
        ]
    ) == 1

    assert result[
        "positions"
    ][0][
        "symbol"
    ] == "TD.TO"

    assert result[
        "positions"
    ][0][
        "shares_quantity"
    ] == (
        "1.2500000000000000000000000000"
    )

    assert len(
        captured
    ) == 1

    compiled = str(
        captured[0]
    )

    assert (
        "portfolio_inventory.user_id"
        in compiled
    )


@pytest.mark.asyncio
async def test_portfolio_service_fails_closed_to_authenticated_owner(
    monkeypatch: pytest.MonkeyPatch,
) -> None:

    captured = []

    def fake_session_factory():
        return FakeSession(
            [],
            captured,
        )

    monkeypatch.setattr(
        portfolio_service,
        "async_session",
        fake_session_factory,
    )

    principal = SimpleNamespace(
        subject="owner-empty",
    )

    result = await (
        portfolio_service
        .get_portfolio_positions_for_api(
            principal
        )
    )

    assert result == {
        "status":
            "ok",

        "positions":
            [],

        "count":
            0,

        "provider":
            "portfolio_inventory",

        "scope":
            "authenticated_account",
    }

    assert len(
        captured
    ) == 1


def test_portfolio_service_no_longer_imports_paper_broker_snapshot() -> None:

    source = (
        portfolio_service
        .__file__
    )

    from pathlib import Path

    text = Path(
        source
    ).read_text(
        encoding="utf-8"
    )

    assert (
        "get_positions_snapshot"
        not in text
    )

    assert (
        "paper_broker"
        not in text
    )

    assert (
        "PortfolioInventory.user_id"
        in text
    )

    assert (
        "not yet ownership-aware"
        not in text
    )

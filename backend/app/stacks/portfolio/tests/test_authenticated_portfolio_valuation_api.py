from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from backend.app import main
from backend.app.stacks.identity_auth.route_protection import (
    AUTHENTICATED,
    resolve_route_policy,
)


def test_portfolio_valuation_policy_is_authenticated() -> None:
    assert (
        resolve_route_policy(
            "GET",
            "/api/v1/portfolio/valuation",
        )
        == AUTHENTICATED
    )


def test_portfolio_valuation_route_is_registered() -> None:
    matching = [
        route
        for route in main.app.routes
        if (
            getattr(
                route,
                "path",
                None,
            )
            == "/api/v1/portfolio/valuation"
        )
    ]

    assert len(matching) == 1

    assert "GET" in getattr(
        matching[0],
        "methods",
        set(),
    )


@pytest.mark.asyncio
async def test_portfolio_valuation_propagates_owner(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    accounting = AsyncMock(
        return_value={
            "starting_capital": 100000.0,
            "current_cash_balance": 75000.25,
            "total_fees_paid": 12.5,
            "net_liquidation_value": 75000.25,
        }
    )

    monkeypatch.setattr(
        main,
        "calculate_live_portfolio_equity",
        accounting,
    )

    result = await main.get_authenticated_portfolio_valuation(
        principal=SimpleNamespace(
            subject="valuation-owner-1",
        ),
    )

    accounting.assert_awaited_once_with(
        user_id="valuation-owner-1"
    )

    assert result == {
        "starting_capital": 100000.0,
        "current_cash_balance": 75000.25,
        "total_fees_paid": 12.5,
        "net_liquidation_value": 75000.25,
        "valuation_basis": "cash_ledger",
        "live_market_marking": False,
    }


@pytest.mark.asyncio
async def test_portfolio_valuation_keeps_owners_separate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    accounting = AsyncMock(
        side_effect=[
            {
                "starting_capital": 100000.0,
                "current_cash_balance": 90000.0,
                "total_fees_paid": 1.0,
                "net_liquidation_value": 90000.0,
            },
            {
                "starting_capital": 100000.0,
                "current_cash_balance": 70000.0,
                "total_fees_paid": 2.0,
                "net_liquidation_value": 70000.0,
            },
        ]
    )

    monkeypatch.setattr(
        main,
        "calculate_live_portfolio_equity",
        accounting,
    )

    first = await main.get_authenticated_portfolio_valuation(
        principal=SimpleNamespace(
            subject="valuation-owner-a",
        ),
    )

    second = await main.get_authenticated_portfolio_valuation(
        principal=SimpleNamespace(
            subject="valuation-owner-b",
        ),
    )

    assert accounting.await_args_list[0].kwargs == {
        "user_id": "valuation-owner-a",
    }

    assert accounting.await_args_list[1].kwargs == {
        "user_id": "valuation-owner-b",
    }

    assert (
        first["current_cash_balance"]
        != second["current_cash_balance"]
    )

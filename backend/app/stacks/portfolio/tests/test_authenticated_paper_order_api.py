from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from pydantic import ValidationError

from backend.app import main
from backend.app.stacks.identity_auth.route_protection import (
    AUTHENTICATED,
    resolve_route_policy,
)


def test_paper_order_route_policy_is_authenticated() -> None:
    assert (
        resolve_route_policy(
            "POST",
            "/api/v1/paper/orders",
        )
        == AUTHENTICATED
    )


def test_paper_order_route_is_registered() -> None:
    matching = [
        route
        for route in main.app.routes
        if (
            getattr(
                route,
                "path",
                None,
            )
            == "/api/v1/paper/orders"
        )
    ]

    assert len(matching) == 1

    assert "POST" in getattr(
        matching[0],
        "methods",
        set(),
    )


def test_paper_order_normalizes_symbol() -> None:
    request = main.PaperOrderRequest(
        symbol="  aapl  ",
        action="buy",
    )

    assert request.symbol == "AAPL"
    assert request.action == "buy"


@pytest.mark.parametrize(
    "symbol",
    [
        "",
        "AAPL!",
        "AAPL TEST",
        "../AAPL",
        "A" * 16,
    ],
)
def test_paper_order_rejects_invalid_symbol(
    symbol: str,
) -> None:
    with pytest.raises(
        ValidationError,
    ):
        main.PaperOrderRequest(
            symbol=symbol,
            action="buy",
        )


def test_paper_order_rejects_invalid_action() -> None:
    with pytest.raises(
        ValidationError,
    ):
        main.PaperOrderRequest(
            symbol="AAPL",
            action="hold",
        )


@pytest.mark.asyncio
async def test_paper_order_propagates_authenticated_owner(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    processor = AsyncMock()

    monkeypatch.setattr(
        main,
        "process_portfolio_output",
        processor,
    )

    monkeypatch.setattr(
        main,
        "create_trace_id",
        lambda prefix: (
            f"{prefix}-trace"
        ),
    )

    result = await main.submit_authenticated_paper_order(
        main.PaperOrderRequest(
            symbol="msft",
            action="sell",
        ),
        principal=SimpleNamespace(
            subject="paper-owner-1",
        ),
    )

    processor.assert_awaited_once_with(
        [
            {
                "symbol": "MSFT",
                "signal": "sell",
            }
        ],
        {
            "symbol": "MSFT",
            "signal": "sell",
            "status": "rebalanced",
            "execution_mode": "paper",
            "source": "authenticated_user_order",
        },
        user_id="paper-owner-1",
        trace_id=(
            "authenticated-paper-order-trace"
        ),
    )

    assert result[
        "execution_mode"
    ] == "paper"

    assert result[
        "live_execution"
    ] is False

    assert result[
        "owner_scope"
    ] == "authenticated_account"


@pytest.mark.asyncio
async def test_two_orders_keep_owners_separate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    processor = AsyncMock()

    monkeypatch.setattr(
        main,
        "process_portfolio_output",
        processor,
    )

    counter = 0

    def fake_trace(
        prefix: str,
    ) -> str:
        nonlocal counter
        counter += 1

        return (
            f"{prefix}-{counter}"
        )

    monkeypatch.setattr(
        main,
        "create_trace_id",
        fake_trace,
    )

    await main.submit_authenticated_paper_order(
        main.PaperOrderRequest(
            symbol="AAPL",
            action="buy",
        ),
        principal=SimpleNamespace(
            subject="paper-owner-a",
        ),
    )

    await main.submit_authenticated_paper_order(
        main.PaperOrderRequest(
            symbol="AAPL",
            action="buy",
        ),
        principal=SimpleNamespace(
            subject="paper-owner-b",
        ),
    )

    assert processor.await_count == 2

    first = processor.await_args_list[
        0
    ]

    second = processor.await_args_list[
        1
    ]

    assert (
        first.kwargs["user_id"]
        == "paper-owner-a"
    )

    assert (
        second.kwargs["user_id"]
        == "paper-owner-b"
    )

    assert (
        first.kwargs["user_id"]
        != second.kwargs["user_id"]
    )

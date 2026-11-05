from decimal import Decimal
from types import SimpleNamespace

import pytest

from backend.app.stacks.snaptrade.application.portfolio_inventory_persistence import (
    SnapTradePortfolioPersistenceError,
    _aggregate_positions,
    _validate_snapshot_boundary,
)


def position(
    *,
    symbol,
    quantity,
    average_entry_price,
    source_provider="snaptrade",
    read_only=True,
):

    return SimpleNamespace(
        symbol=symbol,
        quantity=Decimal(
            quantity
        ),
        average_entry_price=(
            Decimal(
                average_entry_price
            )
            if average_entry_price
            is not None
            else None
        ),
        cost_basis=None,
        source_provider=(
            source_provider
        ),
        read_only=read_only,
    )


def snapshot(
    *,
    source_provider="snaptrade",
    read_only=True,
    trading_enabled=False,
    order_operations_enabled=False,
):

    return SimpleNamespace(
        source_provider=(
            source_provider
        ),
        read_only=read_only,
        trading_enabled=(
            trading_enabled
        ),
        order_operations_enabled=(
            order_operations_enabled
        ),
    )


def test_boundary_accepts_readonly_snaptrade():

    _validate_snapshot_boundary(
        snapshot()
    )


@pytest.mark.parametrize(
    "kwargs",
    [
        {
            "source_provider":
                "other",
        },
        {
            "read_only":
                False,
        },
        {
            "trading_enabled":
                True,
        },
        {
            "order_operations_enabled":
                True,
        },
    ],
)
def test_boundary_rejects_unsafe_snapshot(
    kwargs,
):

    with pytest.raises(
        SnapTradePortfolioPersistenceError
    ):

        _validate_snapshot_boundary(
            snapshot(
                **kwargs
            )
        )


def test_aggregate_single_position():

    result = _aggregate_positions(
        [
            position(
                symbol="td.to",
                quantity="1.0668",
                average_entry_price=(
                    "141.7041619797525309336332958"
                ),
            )
        ]
    )


    item = result[
        "TD.TO"
    ]


    assert (
        item.quantity
        ==
        Decimal(
            "1.0668"
        )
    )


    assert (
        item.total_cost_basis
        ==
        Decimal(
            "151.1700000000000000000000000"
        )
    )


def test_aggregate_duplicate_symbol_across_accounts():

    result = _aggregate_positions(
        [
            position(
                symbol="ABC",
                quantity="1",
                average_entry_price="10",
            ),
            position(
                symbol="ABC",
                quantity="2",
                average_entry_price="20",
            ),
        ]
    )


    item = result[
        "ABC"
    ]


    assert item.quantity == Decimal(
        "3"
    )

    assert (
        item.total_cost_basis
        ==
        Decimal(
            "50"
        )
    )


def test_negative_quantity_fails_closed():

    with pytest.raises(
        SnapTradePortfolioPersistenceError
    ):

        _aggregate_positions(
            [
                position(
                    symbol="ABC",
                    quantity="-1",
                    average_entry_price="10",
                )
            ]
        )


def test_wrong_provider_position_fails_closed():

    with pytest.raises(
        SnapTradePortfolioPersistenceError
    ):

        _aggregate_positions(
            [
                position(
                    symbol="ABC",
                    quantity="1",
                    average_entry_price="10",
                    source_provider="other",
                )
            ]
        )

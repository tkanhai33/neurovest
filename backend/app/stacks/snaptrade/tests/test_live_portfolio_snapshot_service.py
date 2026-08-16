from decimal import Decimal

import pytest

from backend.app.stacks.snaptrade.application.live_portfolio_snapshot_service import (
    SnapTradeLivePortfolioSnapshotError,
    build_live_readonly_snapshot,
)


def real_accounts():

    return [
        {
            "id":
                "wealthsimple-open",

            "name":
                "Wealthsimple Trade PERSONAL",

            "institution_name":
                "Wealthsimple Trade",

            "status":
                "open",
        },

        {
            "id":
                "wealthsimple-closed",

            "name":
                "Historical Account",

            "institution_name":
                "Wealthsimple Trade",

            "status":
                "closed",
        },
    ]


def real_positions():

    return {
        "wealthsimple-open":
            [
                {
                    "units":
                        "0.0255",

                    "price":
                        "6.04",

                    "cost_basis":
                        "5.490196078431372549019607843",

                    "currency":
                        "CAD",

                    "instrument":
                        {
                            "id":
                                "instrument-bte",

                            "symbol":
                                "BTE.TO",

                            "kind":
                                "EQUITY",
                        },
                },

                {
                    "units":
                        "1.0668",

                    "price":
                        "172.61",

                    "cost_basis":
                        "141.7041619797525309336332958",

                    "currency":
                        "CAD",

                    "instrument":
                        {
                            "id":
                                "instrument-td",

                            "symbol":
                                "TD.TO",

                            "kind":
                                "EQUITY",
                        },
                },

                {
                    "units":
                        "12.7299",

                    "price":
                        "17.07",

                    "cost_basis":
                        "15.78409885387944917084973173",

                    "currency":
                        "CAD",

                    "instrument":
                        {
                            "id":
                                "instrument-wcp",

                            "symbol":
                                "WCP.TO",

                            "kind":
                                "EQUITY",
                        },
                },
            ],
    }


def real_balances():

    return {
        "wealthsimple-open":
            [
                {
                    "cash":
                        123.45,

                    "buying_power":
                        123.45,

                    "currency":
                        {
                            "code":
                                "CAD",

                            "name":
                                "Canadian Dollar",
                        },
                },
            ],
    }


def build_snapshot():

    return build_live_readonly_snapshot(
        accounts=(
            real_accounts()
        ),
        positions_by_account=(
            real_positions()
        ),
        balances_by_account=(
            real_balances()
        ),
        network_request_count=3,
    )


def find_position(
    snapshot,
    symbol,
):

    return next(
        position
        for account in snapshot.accounts
        for position in account.positions
        if position.symbol == symbol
    )


def test_snapshot_boundary():

    snapshot = build_snapshot()

    assert snapshot.source_provider == "snaptrade"

    assert (
        snapshot.source_environment
        ==
        "external_readonly"
    )

    assert snapshot.read_only is True
    assert snapshot.paper_only is False
    assert snapshot.trading_enabled is False

    assert (
        snapshot.order_operations_enabled
        is False
    )

    assert (
        snapshot.database_persisted
        is False
    )

    assert snapshot.network_request_count == 3


def test_closed_account_is_excluded():

    snapshot = build_snapshot()

    assert snapshot.account_count == 1

    assert len(
        snapshot.accounts
    ) == 1


def test_exact_symbol_contract():

    snapshot = build_snapshot()

    assert snapshot.position_count == 3

    assert snapshot.symbols == (
        "BTE.TO",
        "TD.TO",
        "WCP.TO",
    )


def test_bte_exact_decimal_contract():

    position = find_position(
        build_snapshot(),
        "BTE.TO",
    )

    assert (
        position.quantity
        ==
        Decimal(
            "0.0255"
        )
    )

    assert (
        position.average_entry_price
        ==
        Decimal(
            "5.490196078431372549019607843"
        )
    )

    assert (
        position.cost_basis
        ==
        Decimal(
            "0.1400000000000000000000000000"
        )
    )

    assert (
        position.current_price
        ==
        Decimal(
            "6.04"
        )
    )

    assert (
        position.market_value
        ==
        Decimal(
            "0.154020"
        )
    )


def test_td_exact_decimal_contract():

    position = find_position(
        build_snapshot(),
        "TD.TO",
    )

    assert (
        position.quantity
        ==
        Decimal(
            "1.0668"
        )
    )

    assert (
        position.average_entry_price
        ==
        Decimal(
            "141.7041619797525309336332958"
        )
    )

    assert (
        position.cost_basis
        ==
        Decimal(
            "151.1700000000000000000000000"
        )
    )

    assert (
        position.current_price
        ==
        Decimal(
            "172.61"
        )
    )

    assert (
        position.market_value
        ==
        Decimal(
            "184.140348"
        )
    )


def test_wcp_exact_decimal_contract():

    position = find_position(
        build_snapshot(),
        "WCP.TO",
    )

    assert (
        position.quantity
        ==
        Decimal(
            "12.7299"
        )
    )

    assert (
        position.average_entry_price
        ==
        Decimal(
            "15.78409885387944917084973173"
        )
    )

    assert (
        position.cost_basis
        ==
        Decimal(
            "200.9299999999999999999999999"
        )
    )

    assert (
        position.current_price
        ==
        Decimal(
            "17.07"
        )
    )

    assert (
        position.market_value
        ==
        Decimal(
            "217.299393"
        )
    )


def test_balance_decimal_contract():

    snapshot = build_snapshot()

    assert snapshot.balance_record_count == 1

    balance = (
        snapshot.accounts[
            0
        ].balances[
            0
        ]
    )

    assert balance.currency == "CAD"

    assert (
        balance.cash_amount
        ==
        Decimal(
            "123.45"
        )
    )

    assert (
        balance.buying_power
        ==
        Decimal(
            "123.45"
        )
    )


def test_account_id_is_hashed():

    snapshot = build_snapshot()

    account_hash = (
        snapshot.accounts[
            0
        ].account_id_hash
    )

    assert (
        account_hash
        !=
        "wealthsimple-open"
    )

    assert len(
        account_hash
    ) == 64

    int(
        account_hash,
        16,
    )


def test_position_id_is_hashed():

    snapshot = build_snapshot()

    for account in snapshot.accounts:

        for position in account.positions:

            assert (
                position.position_id_hash
                is not None
            )

            assert len(
                position.position_id_hash
            ) == 64

            int(
                position.position_id_hash,
                16,
            )


def test_cost_basis_semantics_are_not_reversed():

    snapshot = build_snapshot()

    position = find_position(
        snapshot,
        "TD.TO",
    )

    assert (
        position.average_entry_price
        ==
        Decimal(
            "141.7041619797525309336332958"
        )
    )

    assert (
        position.cost_basis
        ==
        (
            position.quantity
            *
            position.average_entry_price
        )
    )


def test_total_market_value():

    snapshot = build_snapshot()

    expected = (
        Decimal(
            "0.154020"
        )
        +
        Decimal(
            "184.140348"
        )
        +
        Decimal(
            "217.299393"
        )
    )

    assert (
        snapshot.totals.market_value
        ==
        expected
    )


def test_total_cost_basis():

    snapshot = build_snapshot()

    expected = (
        Decimal(
            "0.1400000000000000000000000000"
        )
        +
        Decimal(
            "151.1700000000000000000000000"
        )
        +
        Decimal(
            "200.9299999999999999999999999"
        )
    )

    assert (
        snapshot.totals.cost_basis
        ==
        expected
    )


def test_negative_quantity_fails_closed():

    positions = real_positions()

    positions[
        "wealthsimple-open"
    ][
        0
    ][
        "units"
    ] = "-1"

    with pytest.raises(
        SnapTradeLivePortfolioSnapshotError
    ):

        build_live_readonly_snapshot(
            accounts=(
                real_accounts()
            ),
            positions_by_account=(
                positions
            ),
            balances_by_account=(
                real_balances()
            ),
            network_request_count=3,
        )


def test_negative_market_price_fails_closed():

    positions = real_positions()

    positions[
        "wealthsimple-open"
    ][
        0
    ][
        "price"
    ] = "-1"

    with pytest.raises(
        SnapTradeLivePortfolioSnapshotError
    ):

        build_live_readonly_snapshot(
            accounts=(
                real_accounts()
            ),
            positions_by_account=(
                positions
            ),
            balances_by_account=(
                real_balances()
            ),
            network_request_count=3,
        )


def test_negative_average_entry_fails_closed():

    positions = real_positions()

    positions[
        "wealthsimple-open"
    ][
        0
    ][
        "cost_basis"
    ] = "-1"

    with pytest.raises(
        SnapTradeLivePortfolioSnapshotError
    ):

        build_live_readonly_snapshot(
            accounts=(
                real_accounts()
            ),
            positions_by_account=(
                positions
            ),
            balances_by_account=(
                real_balances()
            ),
            network_request_count=3,
        )

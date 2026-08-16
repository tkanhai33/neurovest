from __future__ import annotations

from backend.app.stacks.snaptrade.persistence.external_portfolio_models import (
    SnapTradeExternalPortfolioPosition,
)


def test_external_inventory_uses_distinct_table() -> None:

    assert (
        SnapTradeExternalPortfolioPosition
        .__tablename__
        ==
        "snaptrade_external_portfolio_positions"
    )

    assert (
        SnapTradeExternalPortfolioPosition
        .__tablename__
        !=
        "portfolio_inventory"
    )


def test_external_inventory_is_owner_scoped() -> None:

    table = (
        SnapTradeExternalPortfolioPosition
        .__table__
    )

    columns = {
        column.name
        for column in table.columns
    }

    required = {
        "neurovest_user_id",
        "account_id_hash",
        "position_id_hash",
        "symbol",
        "shares_quantity",
        "average_entry_price",
        "current_price",
        "market_value",
        "total_cost_basis",
        "unrealized_gain",
        "source_provider",
        "read_only",
        "last_synced_at",
    }

    assert required.issubset(
        columns
    )


def test_external_inventory_has_no_secret_columns() -> None:

    columns = {
        column.name.lower()
        for column
        in (
            SnapTradeExternalPortfolioPosition
            .__table__
            .columns
        )
    }

    forbidden = {
        "user_secret",
        "encrypted_user_secret",
        "consumer_key",
        "client_secret",
        "access_token",
        "refresh_token",
        "password",
    }

    assert columns.isdisjoint(
        forbidden
    )


def test_external_inventory_has_owner_position_uniqueness() -> None:

    table = (
        SnapTradeExternalPortfolioPosition
        .__table__
    )

    matches = []

    for constraint in table.constraints:

        names = tuple(
            column.name
            for column
            in getattr(
                constraint,
                "columns",
                (),
            )
        )

        if names == (
            "neurovest_user_id",
            "account_id_hash",
            "position_id_hash",
        ):
            matches.append(
                constraint
            )

    assert len(
        matches
    ) == 1

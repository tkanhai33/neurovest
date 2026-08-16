from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.stacks.journal_ledger.ledger import (
    PortfolioInventory,
)
from backend.app.stacks.portfolio.read_models.readonly_portfolio_snapshot import (
    ReadOnlyPortfolioSnapshot,
    ReadOnlyPosition,
)


class SnapTradePortfolioPersistenceError(
    ValueError
):
    pass


@dataclass(frozen=True)
class PortfolioPersistenceSummary:
    user_id: str
    inserted: int
    updated: int
    symbols: tuple[str, ...]


@dataclass(frozen=True)
class _AggregatedPosition:
    symbol: str
    quantity: Decimal
    total_cost_basis: Decimal


def _normalize_user_id(
    user_id: str,
) -> str:

    value = str(
        user_id
    ).strip()

    if not value:

        raise SnapTradePortfolioPersistenceError(
            "Authenticated owner is required."
        )

    return value


def _validate_snapshot_boundary(
    snapshot: ReadOnlyPortfolioSnapshot,
) -> None:

    if snapshot.source_provider != "snaptrade":

        raise SnapTradePortfolioPersistenceError(
            "Snapshot source_provider must be snaptrade."
        )

    if snapshot.read_only is not True:

        raise SnapTradePortfolioPersistenceError(
            "Snapshot must remain read-only."
        )

    if snapshot.trading_enabled is not False:

        raise SnapTradePortfolioPersistenceError(
            "Trading must remain disabled."
        )

    if snapshot.order_operations_enabled is not False:

        raise SnapTradePortfolioPersistenceError(
            "Order operations must remain disabled."
        )


def _position_average_entry(
    position: ReadOnlyPosition,
) -> Decimal:

    if position.quantity < 0:

        raise SnapTradePortfolioPersistenceError(
            "Negative position quantity is unsupported."
        )

    average = (
        position.average_entry_price
    )

    cost_basis = (
        position.cost_basis
    )

    if average is not None:

        if average < 0:

            raise SnapTradePortfolioPersistenceError(
                "Negative average entry price is invalid."
            )

        return average

    if (
        cost_basis is not None
        and
        position.quantity > 0
    ):

        if cost_basis < 0:

            raise SnapTradePortfolioPersistenceError(
                "Negative cost basis is invalid."
            )

        return (
            cost_basis
            /
            position.quantity
        )

    if position.quantity == 0:

        return Decimal(
            "0"
        )

    raise SnapTradePortfolioPersistenceError(
        "Position lacks qualified cost basis."
    )


def _aggregate_positions(
    positions: Iterable[
        ReadOnlyPosition
    ],
) -> dict[
    str,
    _AggregatedPosition,
]:

    aggregate: dict[
        str,
        _AggregatedPosition,
    ] = {}


    for position in positions:

        if position.source_provider != "snaptrade":

            raise SnapTradePortfolioPersistenceError(
                "Unexpected position provider."
            )


        if position.read_only is not True:

            raise SnapTradePortfolioPersistenceError(
                "Position is not read-only."
            )


        symbol = str(
            position.symbol
        ).strip().upper()


        if not symbol:

            raise SnapTradePortfolioPersistenceError(
                "Position symbol is required."
            )


        quantity = Decimal(
            position.quantity
        )


        average_entry = (
            _position_average_entry(
                position
            )
        )


        total_cost = (
            quantity
            *
            average_entry
        )


        existing = aggregate.get(
            symbol
        )


        if existing is None:

            aggregate[
                symbol
            ] = _AggregatedPosition(
                symbol=symbol,
                quantity=quantity,
                total_cost_basis=(
                    total_cost
                ),
            )

            continue


        aggregate[
            symbol
        ] = _AggregatedPosition(
            symbol=symbol,
            quantity=(
                existing.quantity
                +
                quantity
            ),
            total_cost_basis=(
                existing.total_cost_basis
                +
                total_cost
            ),
        )


    return aggregate


async def persist_owned_snaptrade_snapshot(
    *,
    session: AsyncSession,
    neurovest_user_id: str,
    snapshot: ReadOnlyPortfolioSnapshot,
) -> PortfolioPersistenceSummary:
    """
    Persist one already-qualified read-only SnapTrade snapshot.

    Transaction ownership remains with the caller.

    This function:
      * never commits,
      * never contacts SnapTrade,
      * never invokes execution/order code,
      * scopes every query/write to one NeuroVest owner.
    """

    owner = _normalize_user_id(
        neurovest_user_id
    )


    _validate_snapshot_boundary(
        snapshot
    )


    aggregate = _aggregate_positions(
        position
        for account in snapshot.accounts
        for position in account.positions
    )


    symbols = tuple(
        sorted(
            aggregate
        )
    )


    if not symbols:

        return PortfolioPersistenceSummary(
            user_id=owner,
            inserted=0,
            updated=0,
            symbols=(),
        )


    rows = (
        await session.execute(
            select(
                PortfolioInventory
            )
            .where(
                PortfolioInventory.user_id
                ==
                owner
            )
            .where(
                PortfolioInventory.symbol.in_(
                    symbols
                )
            )
        )
    ).scalars().all()


    existing = {
        str(
            row.symbol
        ).strip().upper():
            row
        for row in rows
    }


    inserted = 0
    updated = 0


    for symbol in symbols:

        source = aggregate[
            symbol
        ]


        quantity = (
            source.quantity
        )


        total_cost = (
            source.total_cost_basis
        )


        average_entry = (
            total_cost
            /
            quantity
            if quantity != 0
            else Decimal(
                "0"
            )
        )


        row = existing.get(
            symbol
        )


        if row is None:

            row = PortfolioInventory(
                user_id=owner,
                symbol=symbol,
                shares_quantity=(
                    quantity
                ),
                average_entry_price=(
                    average_entry
                ),
                total_cost_basis=(
                    total_cost
                ),
                realized_pnl=Decimal(
                    "0"
                ),
            )


            session.add(
                row
            )


            inserted += 1

        else:

            # Preserve execution-derived realized P&L.
            row.shares_quantity = (
                quantity
            )

            row.average_entry_price = (
                average_entry
            )

            row.total_cost_basis = (
                total_cost
            )


            updated += 1


    await session.flush()


    return PortfolioPersistenceSummary(
        user_id=owner,
        inserted=inserted,
        updated=updated,
        symbols=symbols,
    )

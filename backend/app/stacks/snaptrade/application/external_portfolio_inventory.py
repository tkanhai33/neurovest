from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import (
    delete,
    select,
)
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from backend.app.stacks.portfolio.read_models.readonly_portfolio_snapshot import (
    ReadOnlyPortfolioSnapshot,
)

from backend.app.stacks.snaptrade.persistence.external_portfolio_models import (
    SnapTradeExternalPortfolioPosition,
)


class SnapTradeExternalPortfolioInventoryError(
    RuntimeError
):
    pass


@dataclass(
    frozen=True,
    slots=True,
)
class ExternalPortfolioReconciliationSummary:
    neurovest_user_id: str
    inserted: int
    updated: int
    removed: int
    position_count: int
    symbols: tuple[str, ...]


def _normalize_owner(
    value: str,
) -> str:

    owner = str(
        value
    ).strip()

    if not owner:

        raise (
            SnapTradeExternalPortfolioInventoryError(
                "Authenticated NeuroVest owner is required."
            )
        )

    return owner


def _require_hash(
    value: str | None,
    *,
    label: str,
) -> str:

    text = str(
        value or ""
    ).strip().lower()

    if len(
        text
    ) != 64:

        raise (
            SnapTradeExternalPortfolioInventoryError(
                f"{label} must be a SHA-256 hash."
            )
        )

    try:
        int(
            text,
            16,
        )
    except ValueError as exc:
        raise (
            SnapTradeExternalPortfolioInventoryError(
                f"{label} must be hexadecimal."
            )
        ) from exc

    return text


def _validate_snapshot(
    snapshot: ReadOnlyPortfolioSnapshot,
) -> None:

    if snapshot.source_provider != "snaptrade":

        raise (
            SnapTradeExternalPortfolioInventoryError(
                "External portfolio snapshot must come from SnapTrade."
            )
        )

    if snapshot.read_only is not True:

        raise (
            SnapTradeExternalPortfolioInventoryError(
                "External portfolio snapshot must remain read-only."
            )
        )

    if snapshot.trading_enabled is not False:

        raise (
            SnapTradeExternalPortfolioInventoryError(
                "Trading must remain disabled."
            )
        )

    if (
        snapshot.order_operations_enabled
        is not False
    ):

        raise (
            SnapTradeExternalPortfolioInventoryError(
                "Order operations must remain disabled."
            )
        )


async def reconcile_external_snaptrade_portfolio(
    *,
    session: AsyncSession,
    neurovest_user_id: str,
    snapshot: ReadOnlyPortfolioSnapshot,
) -> ExternalPortfolioReconciliationSummary:
    """
    Reconcile one already-fetched SnapTrade read-only snapshot.

    Transaction ownership remains with the caller.

    This function:
      * performs no provider/network request,
      * performs no commit,
      * does not touch PortfolioInventory,
      * has no order or execution capability,
      * removes only stale rows belonging to this owner.
    """

    owner = _normalize_owner(
        neurovest_user_id
    )

    _validate_snapshot(
        snapshot
    )

    incoming = {}

    for account in snapshot.accounts:

        account_hash = _require_hash(
            account.account_id_hash,
            label="account_id_hash",
        )

        for position in account.positions:

            position_hash = _require_hash(
                position.position_id_hash,
                label="position_id_hash",
            )

            symbol = str(
                position.symbol
            ).strip().upper()

            if not symbol:

                raise (
                    SnapTradeExternalPortfolioInventoryError(
                        "Position symbol is required."
                    )
                )

            key = (
                account_hash,
                position_hash,
            )

            if key in incoming:

                raise (
                    SnapTradeExternalPortfolioInventoryError(
                        "Duplicate external position identity."
                    )
                )

            incoming[
                key
            ] = (
                account,
                position,
                symbol,
            )


    existing_rows = (
        await session.execute(
            select(
                SnapTradeExternalPortfolioPosition
            )
            .where(
                SnapTradeExternalPortfolioPosition
                .neurovest_user_id
                ==
                owner
            )
        )
    ).scalars().all()


    existing = {
        (
            str(
                row.account_id_hash
            ).strip().lower(),
            str(
                row.position_id_hash
            ).strip().lower(),
        ):
            row
        for row in existing_rows
    }


    now = datetime.now(
        UTC
    )

    inserted = 0
    updated = 0


    for key, (
        account,
        position,
        symbol,
    ) in incoming.items():

        row = existing.get(
            key
        )

        if row is None:

            row = (
                SnapTradeExternalPortfolioPosition(
                    neurovest_user_id=owner,
                    account_id_hash=key[0],
                    position_id_hash=key[1],
                    symbol=symbol,
                    instrument_kind=(
                        position.instrument_kind
                    ),
                    currency=(
                        position.currency
                    ),
                    shares_quantity=(
                        Decimal(
                            position.quantity
                        )
                    ),
                    average_entry_price=(
                        position.average_entry_price
                    ),
                    current_price=(
                        position.current_price
                    ),
                    market_value=(
                        position.market_value
                    ),
                    total_cost_basis=(
                        position.cost_basis
                    ),
                    unrealized_gain=(
                        position.unrealized_gain
                    ),
                    source_provider="snaptrade",
                    read_only=True,
                    last_synced_at=now,
                )
            )

            session.add(
                row
            )

            inserted += 1

        else:

            row.symbol = symbol

            row.instrument_kind = (
                position.instrument_kind
            )

            row.currency = (
                position.currency
            )

            row.shares_quantity = (
                Decimal(
                    position.quantity
                )
            )

            row.average_entry_price = (
                position.average_entry_price
            )

            row.current_price = (
                position.current_price
            )

            row.market_value = (
                position.market_value
            )

            row.total_cost_basis = (
                position.cost_basis
            )

            row.unrealized_gain = (
                position.unrealized_gain
            )

            row.source_provider = (
                "snaptrade"
            )

            row.read_only = True

            row.last_synced_at = now

            updated += 1


    stale_keys = (
        set(
            existing
        )
        -
        set(
            incoming
        )
    )


    removed = 0

    for (
        account_hash,
        position_hash,
    ) in sorted(
        stale_keys
    ):

        await session.execute(
            delete(
                SnapTradeExternalPortfolioPosition
            )
            .where(
                SnapTradeExternalPortfolioPosition
                .neurovest_user_id
                ==
                owner
            )
            .where(
                SnapTradeExternalPortfolioPosition
                .account_id_hash
                ==
                account_hash
            )
            .where(
                SnapTradeExternalPortfolioPosition
                .position_id_hash
                ==
                position_hash
            )
        )

        removed += 1


    await session.flush()


    symbols = tuple(
        sorted(
            {
                symbol
                for (
                    _account,
                    _position,
                    symbol,
                )
                in incoming.values()
            }
        )
    )


    return (
        ExternalPortfolioReconciliationSummary(
            neurovest_user_id=owner,
            inserted=inserted,
            updated=updated,
            removed=removed,
            position_count=len(
                incoming
            ),
            symbols=symbols,
        )
    )

async def get_external_snaptrade_portfolio(
    *,
    session: AsyncSession,
    neurovest_user_id: str,
) -> dict[str, object]:
    """
    Read the authenticated owner's durable external SnapTrade
    portfolio inventory.

    This operation:
      * performs no provider/network request,
      * performs no commit,
      * performs no database mutation,
      * exposes no account or position identifier hashes,
      * has no trading or order capability.
    """

    owner = _normalize_owner(
        neurovest_user_id
    )


    rows = (
        await session.execute(
            select(
                SnapTradeExternalPortfolioPosition
            )
            .where(
                SnapTradeExternalPortfolioPosition
                .neurovest_user_id
                ==
                owner
            )
            .order_by(
                SnapTradeExternalPortfolioPosition
                .symbol
                .asc()
            )
        )
    ).scalars().all()


    positions = [
        {
            "symbol":
                str(
                    row.symbol
                ).strip().upper(),

            "instrument_kind":
                row.instrument_kind,

            "currency":
                row.currency,

            "shares_quantity":
                str(
                    row.shares_quantity
                ),

            "average_entry_price":
                (
                    str(
                        row.average_entry_price
                    )
                    if
                    row.average_entry_price
                    is not None
                    else None
                ),

            "current_price":
                (
                    str(
                        row.current_price
                    )
                    if
                    row.current_price
                    is not None
                    else None
                ),

            "market_value":
                (
                    str(
                        row.market_value
                    )
                    if
                    row.market_value
                    is not None
                    else None
                ),

            "total_cost_basis":
                (
                    str(
                        row.total_cost_basis
                    )
                    if
                    row.total_cost_basis
                    is not None
                    else None
                ),

            "unrealized_gain":
                (
                    str(
                        row.unrealized_gain
                    )
                    if
                    row.unrealized_gain
                    is not None
                    else None
                ),

            "source_provider":
                "snaptrade",

            "read_only":
                True,

            "last_synced_at":
                (
                    row.last_synced_at
                    .isoformat()
                    if
                    row.last_synced_at
                    is not None
                    else None
                ),
        }
        for row in rows
    ]


    symbols = sorted(
        {
            item[
                "symbol"
            ]
            for item in positions
            if item[
                "symbol"
            ]
        }
    )


    return {
        "status":
            "ok",

        "source_provider":
            "snaptrade",

        "scope":
            "authenticated_owner",

        "read_only":
            True,

        "trading_enabled":
            False,

        "order_operations_enabled":
            False,

        "position_count":
            len(
                positions
            ),

        "symbols":
            symbols,

        "positions":
            positions,

        "account_identifiers_exposed":
            False,

        "position_identifiers_exposed":
            False,
    }


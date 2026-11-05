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

from backend.app.stacks.snaptrade.persistence.external_balance_models import (
    SnapTradeExternalBalance,
)


class SnapTradeExternalBalanceInventoryError(
    RuntimeError
):
    pass


@dataclass(
    frozen=True,
    slots=True,
)
class ExternalBalanceReconciliationSummary:
    neurovest_user_id: str
    inserted: int
    updated: int
    removed: int
    balance_count: int
    currencies: tuple[str, ...]


def _normalize_owner(
    value: str,
) -> str:

    owner = str(
        value
    ).strip()

    if not owner:

        raise SnapTradeExternalBalanceInventoryError(
            "Authenticated NeuroVest owner is required."
        )

    return owner


def _require_hash(
    value: str | None,
    *,
    label: str,
) -> str:

    rendered = str(
        value or ""
    ).strip().lower()

    if len(
        rendered
    ) != 64:

        raise SnapTradeExternalBalanceInventoryError(
            f"{label} must be a SHA-256 hash."
        )

    try:

        int(
            rendered,
            16,
        )

    except ValueError as exc:

        raise SnapTradeExternalBalanceInventoryError(
            f"{label} must be hexadecimal."
        ) from exc

    return rendered


def _currency(
    value: str | None,
) -> str:

    rendered = str(
        value or ""
    ).strip().upper()

    if not rendered:

        raise SnapTradeExternalBalanceInventoryError(
            "Balance currency is required."
        )

    if len(
        rendered
    ) > 16:

        raise SnapTradeExternalBalanceInventoryError(
            "Balance currency is invalid."
        )

    return rendered


def _validate_snapshot(
    snapshot: ReadOnlyPortfolioSnapshot,
) -> None:

    if snapshot.source_provider != "snaptrade":

        raise SnapTradeExternalBalanceInventoryError(
            "External balance snapshot must come from SnapTrade."
        )

    if snapshot.read_only is not True:

        raise SnapTradeExternalBalanceInventoryError(
            "External balance snapshot must remain read-only."
        )

    if snapshot.trading_enabled is not False:

        raise SnapTradeExternalBalanceInventoryError(
            "Trading must remain disabled."
        )

    if snapshot.order_operations_enabled is not False:

        raise SnapTradeExternalBalanceInventoryError(
            "Order operations must remain disabled."
        )


async def reconcile_external_snaptrade_balances(
    *,
    session: AsyncSession,
    neurovest_user_id: str,
    snapshot: ReadOnlyPortfolioSnapshot,
) -> ExternalBalanceReconciliationSummary:
    """
    Reconcile one already-fetched normalized SnapTrade snapshot.

    Transaction ownership belongs to the caller.

    This function performs:
      * no provider request,
      * no commit,
      * no paper-portfolio inventory mutation,
      * no order operation,
      * no execution operation.
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

        for balance in account.balances:

            currency = _currency(
                balance.currency
            )

            key = (
                account_hash,
                currency,
            )

            if key in incoming:

                raise SnapTradeExternalBalanceInventoryError(
                    "Duplicate external balance identity."
                )

            incoming[
                key
            ] = balance


    existing_rows = (
        await session.execute(
            select(
                SnapTradeExternalBalance
            )
            .where(
                SnapTradeExternalBalance
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
                row.currency
            ).strip().upper(),
        ):
            row
        for row in existing_rows
    }


    now = datetime.now(
        UTC
    )

    inserted = 0
    updated = 0


    for (
        account_hash,
        currency,
    ), balance in incoming.items():

        row = existing.get(
            (
                account_hash,
                currency,
            )
        )

        if row is None:

            row = SnapTradeExternalBalance(
                neurovest_user_id=owner,
                account_id_hash=account_hash,
                currency=currency,
                cash_amount=(
                    Decimal(
                        balance.cash_amount
                    )
                    if balance.cash_amount
                    is not None
                    else None
                ),
                buying_power=(
                    Decimal(
                        balance.buying_power
                    )
                    if balance.buying_power
                    is not None
                    else None
                ),
                cash_available=(
                    Decimal(
                        balance.cash_available
                    )
                    if balance.cash_available
                    is not None
                    else None
                ),
                settled_cash=(
                    Decimal(
                        balance.settled_cash
                    )
                    if balance.settled_cash
                    is not None
                    else None
                ),
                source_provider="snaptrade",
                read_only=True,
                last_synced_at=now,
            )

            session.add(
                row
            )

            inserted += 1

        else:

            row.cash_amount = (
                Decimal(
                    balance.cash_amount
                )
                if balance.cash_amount
                is not None
                else None
            )

            row.buying_power = (
                Decimal(
                    balance.buying_power
                )
                if balance.buying_power
                is not None
                else None
            )

            row.cash_available = (
                Decimal(
                    balance.cash_available
                )
                if balance.cash_available
                is not None
                else None
            )

            row.settled_cash = (
                Decimal(
                    balance.settled_cash
                )
                if balance.settled_cash
                is not None
                else None
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
        currency,
    ) in sorted(
        stale_keys
    ):

        await session.execute(
            delete(
                SnapTradeExternalBalance
            )
            .where(
                SnapTradeExternalBalance
                .neurovest_user_id
                ==
                owner
            )
            .where(
                SnapTradeExternalBalance
                .account_id_hash
                ==
                account_hash
            )
            .where(
                SnapTradeExternalBalance
                .currency
                ==
                currency
            )
        )

        removed += 1


    await session.flush()


    currencies = tuple(
        sorted(
            {
                currency
                for (
                    _account_hash,
                    currency,
                )
                in incoming
            }
        )
    )


    return ExternalBalanceReconciliationSummary(
        neurovest_user_id=owner,
        inserted=inserted,
        updated=updated,
        removed=removed,
        balance_count=len(
            incoming
        ),
        currencies=currencies,
    )


async def get_external_snaptrade_balances(
    *,
    session: AsyncSession,
    neurovest_user_id: str,
) -> dict[str, object]:
    """
    Return durable external balances for one authenticated owner.

    No provider/network request occurs here.
    """

    owner = _normalize_owner(
        neurovest_user_id
    )


    rows = (
        await session.execute(
            select(
                SnapTradeExternalBalance
            )
            .where(
                SnapTradeExternalBalance
                .neurovest_user_id
                ==
                owner
            )
            .order_by(
                SnapTradeExternalBalance
                .currency
                .asc()
            )
        )
    ).scalars().all()


    balances = [
        {
            "currency":
                row.currency,

            "cash_amount":
                (
                    str(
                        row.cash_amount
                    )
                    if row.cash_amount
                    is not None
                    else None
                ),

            "buying_power":
                (
                    str(
                        row.buying_power
                    )
                    if row.buying_power
                    is not None
                    else None
                ),

            "cash_available":
                (
                    str(
                        row.cash_available
                    )
                    if row.cash_available
                    is not None
                    else None
                ),

            "settled_cash":
                (
                    str(
                        row.settled_cash
                    )
                    if row.settled_cash
                    is not None
                    else None
                ),

            "source_provider":
                "snaptrade",

            "read_only":
                True,

            "last_synced_at":
                (
                    row.last_synced_at.isoformat()
                    if row.last_synced_at
                    is not None
                    else None
                ),
        }
        for row in rows
    ]


    cash_total = sum(
        (
            row.cash_amount
            or
            Decimal(
                "0"
            )
        )
        for row in rows
    )


    buying_power_values = [
        row.buying_power
        for row in rows
        if row.buying_power
        is not None
    ]


    buying_power_total = (
        sum(
            buying_power_values,
            Decimal(
                "0"
            ),
        )
        if buying_power_values
        else None
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

        "balance_count":
            len(
                balances
            ),

        "cash_total":
            str(
                cash_total
            ),

        "buying_power_total":
            (
                str(
                    buying_power_total
                )
                if buying_power_total
                is not None
                else None
            ),

        "balances":
            balances,

        "account_identifiers_exposed":
            False,
    }

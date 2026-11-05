from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.stacks.portfolio.read_models.readonly_portfolio_snapshot import (
    ReadOnlyPortfolioSnapshot,
)

from backend.app.stacks.snaptrade.persistence.external_portfolio_value_history_models import (
    SnapTradeExternalPortfolioValueObservation,
)


class SnapTradePortfolioValueHistoryError(RuntimeError):
    pass


def _decimal(
    value: Any,
    *,
    field: str,
) -> Decimal:

    if value is None:
        raise SnapTradePortfolioValueHistoryError(
            f"{field} is required."
        )

    try:
        return Decimal(
            str(value)
        )
    except Exception as error:
        raise SnapTradePortfolioValueHistoryError(
            f"{field} is invalid."
        ) from error


def _datetime(
    value: Any,
) -> datetime:

    if isinstance(
        value,
        datetime,
    ):
        result = value

    elif isinstance(
        value,
        str,
    ):
        result = datetime.fromisoformat(
            value.replace(
                "Z",
                "+00:00",
            )
        )

    else:
        raise SnapTradePortfolioValueHistoryError(
            "generated_at is invalid."
        )

    if result.tzinfo is None:
        result = result.replace(
            tzinfo=UTC
        )

    return result


async def stage_external_portfolio_value_observation(
    *,
    session: AsyncSession,
    neurovest_user_id: str,
    snapshot: ReadOnlyPortfolioSnapshot,
) -> bool:

    owner = str(
        neurovest_user_id
    ).strip()

    if not owner:
        raise SnapTradePortfolioValueHistoryError(
            "Authenticated owner required."
        )

    if snapshot.source_provider != "snaptrade":
        raise SnapTradePortfolioValueHistoryError(
            "Source must be SnapTrade."
        )

    if snapshot.read_only is not True:
        raise SnapTradePortfolioValueHistoryError(
            "Snapshot must remain read-only."
        )

    if snapshot.trading_enabled is not False:
        raise SnapTradePortfolioValueHistoryError(
            "Trading must remain disabled."
        )

    if snapshot.order_operations_enabled is not False:
        raise SnapTradePortfolioValueHistoryError(
            "Order operations must remain disabled."
        )

    totals = snapshot.totals

    if totals.market_value_complete is not True:
        raise SnapTradePortfolioValueHistoryError(
            "Market value is incomplete."
        )

    market_value = _decimal(
        totals.market_value,
        field="market_value",
    )

    cash = _decimal(
        totals.cash,
        field="cash",
    )

    unrealized_gain = (
        None
        if totals.unrealized_gain is None
        else _decimal(
            totals.unrealized_gain,
            field="unrealized_gain",
        )
    )

    account_value = (
        market_value
        +
        cash
    )

    observed_at = _datetime(
        snapshot.generated_at
    )

    existing = await session.scalar(
        select(
            SnapTradeExternalPortfolioValueObservation.id
        ).where(
            SnapTradeExternalPortfolioValueObservation.neurovest_user_id
            == owner,
            SnapTradeExternalPortfolioValueObservation.observed_at
            == observed_at,
        )
    )

    if existing is not None:
        return False

    session.add(
        SnapTradeExternalPortfolioValueObservation(
            neurovest_user_id=owner,
            observed_at=observed_at,
            market_value=market_value,
            cash=cash,
            account_value=account_value,
            unrealized_gain=unrealized_gain,
            source_provider="snaptrade",
            read_only=True,
        )
    )

    return True


async def list_external_portfolio_value_history(
    *,
    session: AsyncSession,
    neurovest_user_id: str,
    limit: int = 1000,
) -> list[dict[str, object]]:

    owner = str(
        neurovest_user_id
    ).strip()

    if not owner:
        raise SnapTradePortfolioValueHistoryError(
            "Authenticated owner required."
        )

    bounded_limit = max(
        1,
        min(
            int(limit),
            5000,
        ),
    )

    result = await session.execute(
        select(
            SnapTradeExternalPortfolioValueObservation
        )
        .where(
            SnapTradeExternalPortfolioValueObservation.neurovest_user_id
            == owner
        )
        .order_by(
            SnapTradeExternalPortfolioValueObservation.observed_at.desc()
        )
        .limit(
            bounded_limit
        )
    )

    observations = list(
        result.scalars()
    )

    observations.reverse()

    return [
        {
            "observed_at":
                item.observed_at.isoformat(),

            "market_value":
                str(item.market_value),

            "cash":
                str(item.cash),

            "account_value":
                str(item.account_value),

            "unrealized_gain":
                (
                    None
                    if item.unrealized_gain is None
                    else str(
                        item.unrealized_gain
                    )
                ),

            "source_provider":
                item.source_provider,

            "read_only":
                item.read_only,
        }
        for item in observations
    ]

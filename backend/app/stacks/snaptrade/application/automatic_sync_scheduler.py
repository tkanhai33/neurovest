from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import select

from backend.app.stacks.db_runtime.database import (
    async_session,
)
from backend.app.stacks.snaptrade.application.connection_service import (
    SnapTradeConnectionService,
)
from backend.app.stacks.snaptrade.application.external_portfolio_value_history import (
    stage_external_portfolio_value_observation,
)
from backend.app.stacks.snaptrade.application.live_portfolio_sync_service import (
    SnapTradeLivePortfolioSyncService,
)
from backend.app.stacks.snaptrade.persistence.credential_models import (
    SnapTradeUserCredential,
)


_MARKET_TIMEZONE = ZoneInfo(
    "America/Toronto"
)

_MARKET_OPEN = (
    9,
    35,
)

_MARKET_CLOSE = (
    15,
    55,
)

_MINIMUM_OWNER_SYNC_INTERVAL = timedelta(
    hours=2
)

_FAILURE_NOT_BEFORE: dict[
    str,
    datetime,
] = {}

_FAILURE_COUNT: dict[
    str,
    int,
] = {}


@dataclass(
    frozen=True,
    slots=True,
)
class AutomaticSyncCycleSummary:
    eligible: int
    synchronized: int
    skipped: int
    failed: int


def _boolean(
    value: str | None,
    *,
    default: bool,
) -> bool:

    if value is None:
        return default

    return str(
        value
    ).strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def automatic_sync_enabled() -> bool:
    """
    Disabled by default.

    External provider activity begins only when the backend
    environment explicitly sets:

        SNAPTRADE_AUTOMATIC_SYNC_ENABLED=true
    """

    return _boolean(
        os.getenv(
            "SNAPTRADE_AUTOMATIC_SYNC_ENABLED"
        ),
        default=False,
    )


def _positive_integer(
    name: str,
    *,
    default: int,
    minimum: int,
    maximum: int,
) -> int:

    try:
        value = int(
            str(
                os.getenv(
                    name,
                    default,
                )
            ).strip()
        )
    except (
        TypeError,
        ValueError,
    ):
        value = default

    return max(
        minimum,
        min(
            maximum,
            value,
        ),
    )


def _market_window_open(
    now: datetime,
) -> bool:

    localized = now.astimezone(
        _MARKET_TIMEZONE
    )

    if localized.weekday() >= 5:
        return False

    current = (
        localized.hour,
        localized.minute,
    )

    return (
        _MARKET_OPEN
        <= current
        <= _MARKET_CLOSE
    )


def _owner_due(
    *,
    last_synced_at: datetime | None,
    now: datetime,
) -> bool:

    if last_synced_at is None:
        return True

    if last_synced_at.tzinfo is None:
        last_synced_at = last_synced_at.replace(
            tzinfo=UTC
        )

    return (
        last_synced_at.astimezone(
            UTC
        )
        +
        _MINIMUM_OWNER_SYNC_INTERVAL
        <=
        now.astimezone(
            UTC
        )
    )


def _failure_delay(
    failure_count: int,
) -> timedelta:

    seconds = min(
        3600,
        60 * (
            2 ** max(
                0,
                failure_count - 1,
            )
        ),
    )

    return timedelta(
        seconds=seconds
    )


def _retry_permitted(
    *,
    owner: str,
    now: datetime,
) -> bool:

    not_before = _FAILURE_NOT_BEFORE.get(
        owner
    )

    return (
        not_before is None
        or
        not_before <= now
    )


async def _eligible_owners(
    *,
    now: datetime,
    limit: int,
) -> list[str]:

    async with async_session() as session:
        result = await session.execute(
            select(
                SnapTradeUserCredential
            )
            .where(
                SnapTradeUserCredential
                .connection_status
                ==
                "connected"
            )
            .order_by(
                SnapTradeUserCredential
                .last_synced_at
            )
        )

        records = list(
            result.scalars()
        )

    owners: list[str] = []

    for record in records:
        owner = str(
            record.neurovest_user_id
        ).strip()

        if (
            not owner
            or
            not _owner_due(
                last_synced_at=(
                    record.last_synced_at
                ),
                now=now,
            )
            or
            not _retry_permitted(
                owner=owner,
                now=now,
            )
        ):
            continue

        owners.append(
            owner
        )

        if len(
            owners
        ) >= limit:
            break

    return owners


async def _synchronize_one_owner(
    *,
    owner: str,
) -> bool:
    """
    Run the same read-only services used by the authenticated route.

    This worker never imports or calls an order, execution, paper
    broker, or trading service.
    """

    async with async_session() as session:

        try:
            connection_service = (
                SnapTradeConnectionService(
                    session
                )
            )

            connection_state = (
                await connection_service
                .synchronize_status(
                    neurovest_user_id=owner
                )
            )

            if (
                connection_state.get(
                    "connection_status"
                )
                !=
                "connected"
            ):
                return False

            portfolio_service = (
                SnapTradeLivePortfolioSyncService(
                    session
                )
            )

            synchronized = (
                await portfolio_service
                .synchronize(
                    neurovest_user_id=owner
                )
            )

            await stage_external_portfolio_value_observation(
                session=session,
                neurovest_user_id=owner,
                snapshot=synchronized.snapshot,
            )

            await session.commit()

            return True

        except Exception:
            await session.rollback()
            raise


async def run_automatic_snaptrade_sync_cycle(
    *,
    now: datetime | None = None,
) -> AutomaticSyncCycleSummary:
    """
    Refresh due connected owners sequentially.

    A two-hour per-owner cooldown within the weekday market window
    permits at most four automatic refreshes in one market day.
    The batch is intentionally small and sequential to keep provider
    traffic well below rate limits.
    """

    current = now or datetime.now(
        UTC
    )

    if (
        not automatic_sync_enabled()
        or
        not _market_window_open(
            current
        )
    ):
        return AutomaticSyncCycleSummary(
            eligible=0,
            synchronized=0,
            skipped=0,
            failed=0,
        )

    batch_size = _positive_integer(
        "SNAPTRADE_AUTOMATIC_SYNC_BATCH_SIZE",
        default=2,
        minimum=1,
        maximum=10,
    )

    owners = await _eligible_owners(
        now=current,
        limit=batch_size,
    )

    synchronized_count = 0
    skipped_count = 0
    failed_count = 0

    for owner in owners:

        try:
            completed = (
                await _synchronize_one_owner(
                    owner=owner
                )
            )
        except asyncio.CancelledError:
            raise
        except Exception:
            failure_count = (
                _FAILURE_COUNT.get(
                    owner,
                    0,
                )
                + 1
            )

            _FAILURE_COUNT[
                owner
            ] = failure_count

            _FAILURE_NOT_BEFORE[
                owner
            ] = (
                current
                +
                _failure_delay(
                    failure_count
                )
            )

            failed_count += 1
            continue

        if completed:
            _FAILURE_COUNT.pop(
                owner,
                None,
            )

            _FAILURE_NOT_BEFORE.pop(
                owner,
                None,
            )

            synchronized_count += 1
        else:
            skipped_count += 1

    return AutomaticSyncCycleSummary(
        eligible=len(
            owners
        ),
        synchronized=synchronized_count,
        skipped=skipped_count,
        failed=failed_count,
    )


async def _automatic_sync_daemon() -> None:

    interval_seconds = _positive_integer(
        "SNAPTRADE_AUTOMATIC_SYNC_INTERVAL_SECONDS",
        default=300,
        minimum=60,
        maximum=3600,
    )

    while True:

        try:
            await run_automatic_snaptrade_sync_cycle()
        except asyncio.CancelledError:
            raise
        except Exception:
            # Deliberately avoid printing owner identity, provider
            # payloads, credentials, or account details.
            pass

        await asyncio.sleep(
            interval_seconds
        )


def start_snaptrade_auto_sync_daemon() -> (
    asyncio.Task[None]
    |
    None
):
    """
    Start only when explicitly enabled by backend configuration.
    """

    if not automatic_sync_enabled():
        return None

    return asyncio.create_task(
        _automatic_sync_daemon(),
        name=(
            "snaptrade-readonly-auto-sync"
        ),
    )

from __future__ import annotations

from dataclasses import dataclass
from typing import (
    Awaitable,
    Callable,
)

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.stacks.portfolio.read_models.readonly_portfolio_snapshot import (
    ReadOnlyPortfolioSnapshot,
)

from backend.app.stacks.snaptrade.application.live_portfolio_snapshot_service import (
    SnapTradeLivePortfolioSnapshotService,
)

from backend.app.stacks.snaptrade.application.external_portfolio_inventory import (
    ExternalPortfolioReconciliationSummary,
    reconcile_external_snaptrade_portfolio,
)

from backend.app.stacks.snaptrade.application.external_balance_inventory import (
    ExternalBalanceReconciliationSummary,
    reconcile_external_snaptrade_balances,
)


class SnapTradeLivePortfolioSyncError(
    RuntimeError
):
    pass


@dataclass(frozen=True)
class SnapTradeLivePortfolioSyncResult:
    snapshot: ReadOnlyPortfolioSnapshot
    persistence: ExternalPortfolioReconciliationSummary
    balance_persistence: ExternalBalanceReconciliationSummary


SnapshotServiceFactory = Callable[
    [AsyncSession],
    SnapTradeLivePortfolioSnapshotService,
]


PersistenceFunction = Callable[
    ...,
    Awaitable[
        ExternalPortfolioReconciliationSummary
    ],
]


BalancePersistenceFunction = Callable[
    ...,
    Awaitable[
        ExternalBalanceReconciliationSummary
    ],
]


class SnapTradeLivePortfolioSyncService:
    """
    Coordinate one owner-bound SnapTrade portfolio synchronization.

    Transaction ownership belongs to the caller.

    This service does NOT:
      * commit,
      * rollback,
      * submit orders,
      * enable trading,
      * mutate brokerage state.

    Sequence:
      1. fetch externally-gated read-only SnapTrade snapshot
      2. normalize it through the qualified live bridge
      3. stage owner-bound external position persistence
      4. stage owner-bound external balance persistence
      5. return control to caller for commit or rollback
    """

    def __init__(
        self,
        session: AsyncSession,
        *,
        snapshot_service_factory: SnapshotServiceFactory | None = None,
        persistence_function: PersistenceFunction = (
            reconcile_external_snaptrade_portfolio
        ),
        balance_persistence_function: BalancePersistenceFunction = (
            reconcile_external_snaptrade_balances
        ),
    ) -> None:

        self._session = session

        self._snapshot_service_factory = (
            snapshot_service_factory
            or
            (
                lambda session:
                    SnapTradeLivePortfolioSnapshotService(
                        session
                    )
            )
        )

        self._persistence_function = (
            persistence_function
        )

        self._balance_persistence_function = (
            balance_persistence_function
        )


    async def synchronize(
        self,
        *,
        neurovest_user_id: str,
    ) -> SnapTradeLivePortfolioSyncResult:

        owner = str(
            neurovest_user_id
        ).strip()


        if not owner:

            raise SnapTradeLivePortfolioSyncError(
                "Authenticated NeuroVest owner is required."
            )


        snapshot_service = (
            self._snapshot_service_factory(
                self._session
            )
        )


        snapshot = (
            await snapshot_service.fetch_snapshot(
                neurovest_user_id=owner
            )
        )


        if snapshot.source_provider != "snaptrade":

            raise SnapTradeLivePortfolioSyncError(
                "Unexpected portfolio source provider."
            )


        if snapshot.read_only is not True:

            raise SnapTradeLivePortfolioSyncError(
                "SnapTrade snapshot must remain read-only."
            )


        if snapshot.trading_enabled is not False:

            raise SnapTradeLivePortfolioSyncError(
                "Trading must remain disabled."
            )


        if snapshot.order_operations_enabled is not False:

            raise SnapTradeLivePortfolioSyncError(
                "Order operations must remain disabled."
            )


        persistence = (
            await self._persistence_function(
                session=self._session,
                neurovest_user_id=owner,
                snapshot=snapshot,
            )
        )


        if persistence.neurovest_user_id != owner:

            raise SnapTradeLivePortfolioSyncError(
                "Persistence owner does not match authenticated owner."
            )


        balance_persistence = (
            await self._balance_persistence_function(
                session=self._session,
                neurovest_user_id=owner,
                snapshot=snapshot,
            )
        )


        if balance_persistence.neurovest_user_id != owner:

            raise SnapTradeLivePortfolioSyncError(
                "Balance persistence owner does not match authenticated owner."
            )


        return SnapTradeLivePortfolioSyncResult(
            snapshot=snapshot,
            persistence=persistence,
            balance_persistence=balance_persistence,
        )

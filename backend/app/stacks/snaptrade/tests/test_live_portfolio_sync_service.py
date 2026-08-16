from types import SimpleNamespace

import pytest

from backend.app.stacks.snaptrade.application.live_portfolio_sync_service import (
    SnapTradeLivePortfolioSyncError,
    SnapTradeLivePortfolioSyncService,
)

from backend.app.stacks.snaptrade.application.external_portfolio_inventory import (
    ExternalPortfolioReconciliationSummary,
)


class FakeSnapshotService:

    def __init__(
        self,
        snapshot,
    ):

        self.snapshot = snapshot

        self.calls = []


    async def fetch_snapshot(
        self,
        *,
        neurovest_user_id,
    ):

        self.calls.append(
            neurovest_user_id
        )

        return self.snapshot


def safe_snapshot():

    return SimpleNamespace(
        source_provider="snaptrade",
        read_only=True,
        trading_enabled=False,
        order_operations_enabled=False,
    )


@pytest.mark.asyncio
async def test_sync_calls_snapshot_then_persistence():

    snapshot = safe_snapshot()

    fake_snapshot_service = (
        FakeSnapshotService(
            snapshot
        )
    )

    persistence_calls = []


    async def persist(
        *,
        session,
        neurovest_user_id,
        snapshot,
    ):

        persistence_calls.append(
            {
                "session":
                    session,

                "user_id":
                    neurovest_user_id,

                "snapshot":
                    snapshot,
            }
        )


        return ExternalPortfolioReconciliationSummary(
            neurovest_user_id=neurovest_user_id,
            inserted=0,
            updated=3,
            removed=0,
            position_count=3,
            symbols=(
                "BTE.TO",
                "TD.TO",
                "WCP.TO",
            ),
        )


    fake_session = object()


    service = (
        SnapTradeLivePortfolioSyncService(
            fake_session,
            snapshot_service_factory=(
                lambda session:
                    fake_snapshot_service
            ),
            persistence_function=persist,
        )
    )


    result = await service.synchronize(
        neurovest_user_id="owner-1"
    )


    assert (
        fake_snapshot_service.calls
        ==
        [
            "owner-1"
        ]
    )


    assert len(
        persistence_calls
    ) == 1


    assert (
        persistence_calls[
            0
        ][
            "session"
        ]
        is
        fake_session
    )


    assert (
        persistence_calls[
            0
        ][
            "user_id"
        ]
        ==
        "owner-1"
    )


    assert (
        persistence_calls[
            0
        ][
            "snapshot"
        ]
        is
        snapshot
    )


    assert (
        result.persistence.inserted
        ==
        0
    )


    assert (
        result.persistence.updated
        ==
        3
    )


@pytest.mark.asyncio
async def test_empty_owner_fails_before_provider_call():

    fake_snapshot_service = (
        FakeSnapshotService(
            safe_snapshot()
        )
    )


    async def persist(
        **kwargs,
    ):

        raise AssertionError(
            "Persistence must not run."
        )


    service = (
        SnapTradeLivePortfolioSyncService(
            object(),
            snapshot_service_factory=(
                lambda session:
                    fake_snapshot_service
            ),
            persistence_function=persist,
        )
    )


    with pytest.raises(
        SnapTradeLivePortfolioSyncError
    ):

        await service.synchronize(
            neurovest_user_id=" "
        )


    assert (
        fake_snapshot_service.calls
        ==
        []
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "field,value",
    [
        (
            "source_provider",
            "other",
        ),
        (
            "read_only",
            False,
        ),
        (
            "trading_enabled",
            True,
        ),
        (
            "order_operations_enabled",
            True,
        ),
    ],
)
async def test_unsafe_snapshot_fails_before_persistence(
    field,
    value,
):

    snapshot = safe_snapshot()

    setattr(
        snapshot,
        field,
        value,
    )


    fake_snapshot_service = (
        FakeSnapshotService(
            snapshot
        )
    )


    persistence_called = False


    async def persist(
        **kwargs,
    ):

        nonlocal persistence_called

        persistence_called = True

        raise AssertionError(
            "Persistence must not run."
        )


    service = (
        SnapTradeLivePortfolioSyncService(
            object(),
            snapshot_service_factory=(
                lambda session:
                    fake_snapshot_service
            ),
            persistence_function=persist,
        )
    )


    with pytest.raises(
        SnapTradeLivePortfolioSyncError
    ):

        await service.synchronize(
            neurovest_user_id="owner-1"
        )


    assert persistence_called is False


@pytest.mark.asyncio
async def test_persistence_owner_mismatch_fails_closed():

    snapshot = safe_snapshot()


    async def persist(
        **kwargs,
    ):

        return ExternalPortfolioReconciliationSummary(
            neurovest_user_id="wrong-owner",
            inserted=0,
            updated=3,
            removed=0,
            position_count=3,
            symbols=(
                "BTE.TO",
                "TD.TO",
                "WCP.TO",
            ),
        )


    service = (
        SnapTradeLivePortfolioSyncService(
            object(),
            snapshot_service_factory=(
                lambda session:
                    FakeSnapshotService(
                        snapshot
                    )
            ),
            persistence_function=persist,
        )
    )


    with pytest.raises(
        SnapTradeLivePortfolioSyncError
    ):

        await service.synchronize(
            neurovest_user_id="owner-1"
        )

from types import SimpleNamespace

import pytest

from backend.app.stacks.snaptrade import (
    api_router,
)


class FakeSession:

    def __init__(
        self,
    ):

        self.commit_count = 0
        self.rollback_count = 0


    async def commit(
        self,
    ):

        self.commit_count += 1


    async def rollback(
        self,
    ):

        self.rollback_count += 1


class FakeSessionContext:

    def __init__(
        self,
        session,
    ):

        self.session = session


    async def __aenter__(
        self,
    ):

        return self.session


    async def __aexit__(
        self,
        exc_type,
        exc,
        tb,
    ):

        return False


class FakeConnectionService:

    owners = []


    def __init__(
        self,
        session,
    ):

        self.session = session


    async def synchronize_status(
        self,
        *,
        neurovest_user_id,
    ):

        self.__class__.owners.append(
            neurovest_user_id
        )

        return {
            "registered":
                True,

            "connection_status":
                "connected",

            "last_sync_status":
                "connected",

            "trading_enabled":
                False,
        }


class FakePortfolioSyncService:

    owners = []


    def __init__(
        self,
        session,
    ):

        self.session = session


    async def synchronize(
        self,
        *,
        neurovest_user_id,
    ):

        self.__class__.owners.append(
            neurovest_user_id
        )

        return SimpleNamespace(
            snapshot=SimpleNamespace(
                read_only=True,
                trading_enabled=False,
                order_operations_enabled=False,
                account_count=4,
                position_count=3,
                balance_record_count=4,
                network_request_count=9,
                symbols=(
                    "BTE.TO",
                    "TD.TO",
                    "WCP.TO",
                ),
            ),
            persistence=SimpleNamespace(
                user_id=(
                    neurovest_user_id
                ),
                inserted=0,
                updated=3,
                removed=0,
            ),
        )


@pytest.mark.asyncio
async def test_authenticated_route_runs_both_sync_paths_and_commits(
    monkeypatch,
):

    session = FakeSession()

    monkeypatch.setattr(
        api_router,
        "async_session",
        lambda:
            FakeSessionContext(
                session
            ),
    )

    monkeypatch.setattr(
        api_router,
        "SnapTradeConnectionService",
        FakeConnectionService,
    )

    monkeypatch.setattr(
        api_router,
        "SnapTradeLivePortfolioSyncService",
        FakePortfolioSyncService,
    )

    FakeConnectionService.owners = []
    FakePortfolioSyncService.owners = []

    response = (
        await api_router
        .synchronize_snaptrade_status(
            principal=SimpleNamespace(
                subject="owner-route-1"
            )
        )
    )

    assert (
        FakeConnectionService.owners
        ==
        [
            "owner-route-1"
        ]
    )

    assert (
        FakePortfolioSyncService.owners
        ==
        [
            "owner-route-1"
        ]
    )

    assert session.commit_count == 1
    assert session.rollback_count == 0

    assert response[
        "registered"
    ] is True

    assert response[
        "connection_status"
    ] == "connected"

    portfolio = response[
        "portfolio_sync"
    ]

    assert portfolio[
        "status"
    ] == "synchronized"

    assert portfolio[
        "read_only"
    ] is True

    assert portfolio[
        "trading_enabled"
    ] is False

    assert portfolio[
        "order_operations_enabled"
    ] is False

    assert portfolio[
        "account_count"
    ] == 4

    assert portfolio[
        "position_count"
    ] == 3

    assert portfolio[
        "balance_record_count"
    ] == 4

    assert portfolio[
        "network_request_count"
    ] == 9

    assert portfolio[
        "symbols"
    ] == [
        "BTE.TO",
        "TD.TO",
        "WCP.TO",
    ]

    assert portfolio[
        "inserted"
    ] == 0

    assert portfolio[
        "updated"
    ] == 3

    assert portfolio[
        "removed"
    ] == 0

    assert portfolio[
        "external_inventory"
    ] is True


@pytest.mark.asyncio
async def test_portfolio_sync_failure_rolls_back_without_commit(
    monkeypatch,
):

    session = FakeSession()


    class FailingPortfolioSyncService:

        def __init__(
            self,
            session,
        ):

            self.session = session


        async def synchronize(
            self,
            *,
            neurovest_user_id,
        ):

            raise RuntimeError(
                "simulated portfolio sync failure"
            )


    monkeypatch.setattr(
        api_router,
        "async_session",
        lambda:
            FakeSessionContext(
                session
            ),
    )

    monkeypatch.setattr(
        api_router,
        "SnapTradeConnectionService",
        FakeConnectionService,
    )

    monkeypatch.setattr(
        api_router,
        "SnapTradeLivePortfolioSyncService",
        FailingPortfolioSyncService,
    )

    with pytest.raises(
        RuntimeError,
        match=(
            "simulated portfolio sync failure"
        ),
    ):

        await (
            api_router
            .synchronize_snaptrade_status(
                principal=SimpleNamespace(
                    subject="owner-route-2"
                )
            )
        )

    assert session.commit_count == 0
    assert session.rollback_count == 1

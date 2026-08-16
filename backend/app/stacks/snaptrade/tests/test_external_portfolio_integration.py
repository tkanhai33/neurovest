from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace

import pytest

from backend.app.stacks.snaptrade.application import (
    external_portfolio_inventory,
)


class FakeScalars:

    def __init__(
        self,
        rows,
    ):
        self._rows = rows

    def all(
        self,
    ):
        return list(
            self._rows
        )


class FakeResult:

    def __init__(
        self,
        rows,
    ):
        self._rows = rows

    def scalars(
        self,
    ):
        return FakeScalars(
            self._rows
        )


class FakeSession:

    def __init__(
        self,
        rows,
    ):
        self.rows = rows
        self.statements = []
        self.commit_count = 0

    async def execute(
        self,
        statement,
    ):
        self.statements.append(
            statement
        )

        return FakeResult(
            self.rows
        )


@pytest.mark.asyncio
async def test_external_portfolio_read_is_owner_scoped_and_read_only() -> None:

    now = datetime.now(
        UTC
    )

    row = SimpleNamespace(
        symbol="TD.TO",
        instrument_kind="equity",
        currency="CAD",
        shares_quantity=Decimal(
            "1.250000000000000000"
        ),
        average_entry_price=Decimal(
            "100.000000000000000000"
        ),
        current_price=Decimal(
            "110.000000000000000000"
        ),
        market_value=Decimal(
            "137.500000000000000000"
        ),
        total_cost_basis=Decimal(
            "125.000000000000000000"
        ),
        unrealized_gain=Decimal(
            "12.500000000000000000"
        ),
        last_synced_at=now,
    )

    session = FakeSession(
        [
            row,
        ]
    )

    result = await (
        external_portfolio_inventory
        .get_external_snaptrade_portfolio(
            session=session,
            neurovest_user_id="owner-123",
        )
    )

    assert result[
        "status"
    ] == "ok"

    assert result[
        "source_provider"
    ] == "snaptrade"

    assert result[
        "scope"
    ] == "authenticated_owner"

    assert result[
        "read_only"
    ] is True

    assert result[
        "trading_enabled"
    ] is False

    assert result[
        "order_operations_enabled"
    ] is False

    assert result[
        "position_count"
    ] == 1

    assert result[
        "symbols"
    ] == [
        "TD.TO"
    ]

    assert result[
        "account_identifiers_exposed"
    ] is False

    assert result[
        "position_identifiers_exposed"
    ] is False

    assert (
        "account_id_hash"
        not in result[
            "positions"
        ][0]
    )

    assert (
        "position_id_hash"
        not in result[
            "positions"
        ][0]
    )

    assert len(
        session.statements
    ) == 1

    sql = str(
        session.statements[
            0
        ]
    )

    assert (
        "snaptrade_external_portfolio_positions.neurovest_user_id"
        in sql
    )


def test_live_sync_uses_external_inventory_not_portfolio_inventory() -> None:

    root = (
        Path(
            __file__
        )
        .resolve()
        .parents[
            1
        ]
    )

    path = (
        root
        /
        "application"
        /
        "live_portfolio_sync_service.py"
    )

    text = path.read_text(
        encoding="utf-8"
    )

    assert (
        "reconcile_external_snaptrade_portfolio"
        in text
    )

    assert (
        "ExternalPortfolioReconciliationSummary"
        in text
    )

    assert (
        "persist_owned_snaptrade_snapshot"
        not in text
    )

    assert (
        "PortfolioPersistenceSummary"
        not in text
    )

    assert (
        "persistence.neurovest_user_id"
        in text
    )

    assert (
        ".commit("
        not in text
    )


def test_snaptrade_router_has_authenticated_external_portfolio_route() -> None:

    root = (
        Path(
            __file__
        )
        .resolve()
        .parents[
            1
        ]
    )

    path = (
        root
        /
        "api_router.py"
    )

    text = path.read_text(
        encoding="utf-8"
    )

    assert (
        '@router.get(\n    "/portfolio",'
        in text
    )

    assert (
        "get_snaptrade_external_portfolio"
        in text
    )

    assert (
        "require_authenticated_principal"
        in text
    )

    assert (
        "get_external_snaptrade_portfolio"
        in text
    )

    assert (
        '"/synchronize"'
        in text
    )

    assert (
        "await session.commit()"
        in text
    )

    assert (
        "await session.rollback()"
        in text
    )


def test_external_model_registered_in_runtime_registry() -> None:

    repository = (
        Path(
            __file__
        )
        .resolve()
        .parents[
            5
        ]
    )

    path = (
        repository
        /
        "backend"
        /
        "app"
        /
        "stacks"
        /
        "db_runtime"
        /
        "model_registry.py"
    )

    text = path.read_text(
        encoding="utf-8"
    )

    assert (
        "SnapTradeExternalPortfolioPosition"
        in text
    )


def test_external_model_registered_in_alembic_environment() -> None:

    repository = (
        Path(
            __file__
        )
        .resolve()
        .parents[
            5
        ]
    )

    path = (
        repository
        /
        "alembic"
        /
        "env.py"
    )

    text = path.read_text(
        encoding="utf-8"
    )

    assert (
        "SnapTradeExternalPortfolioPosition"
        in text
    )

    assert (
        "target_metadata = Base.metadata"
        in text
    )


def test_external_inventory_migration_contract() -> None:

    repository = (
        Path(
            __file__
        )
        .resolve()
        .parents[
            5
        ]
    )

    path = (
        repository
        /
        "alembic"
        /
        "versions"
        /
        "snaptrade_external_inventory_v1.py"
    )

    text = path.read_text(
        encoding="utf-8"
    )

    assert (
        'revision = "snaptrade_external_inventory_v1"'
        in text
    )

    assert (
        'down_revision = "portfolio_decimal_20260816"'
        in text
    )

    assert (
        '"snaptrade_external_portfolio_positions"'
        in text
    )

    assert (
        '"neurovest_user_id"'
        in text
    )

    assert (
        '"account_id_hash"'
        in text
    )

    assert (
        '"position_id_hash"'
        in text
    )

    assert (
        "op.create_table("
        in text
    )

    assert (
        "op.drop_table("
        in text
    )

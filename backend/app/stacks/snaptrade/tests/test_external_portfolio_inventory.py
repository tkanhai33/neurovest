from __future__ import annotations

from decimal import Decimal
from types import SimpleNamespace

import pytest

from backend.app.stacks.snaptrade.application.external_portfolio_inventory import (
    SnapTradeExternalPortfolioInventoryError,
    reconcile_external_snaptrade_portfolio,
)


HASH_A = "a" * 64
HASH_B = "b" * 64


class FakeScalarResult:

    def __init__(
        self,
        rows,
    ):
        self.rows = rows

    def all(
        self,
    ):
        return list(
            self.rows
        )


class FakeResult:

    def __init__(
        self,
        rows=None,
    ):
        self.rows = (
            []
            if rows is None
            else rows
        )

    def scalars(
        self,
    ):
        return FakeScalarResult(
            self.rows
        )


class FakeSession:

    def __init__(
        self,
        rows=None,
    ):

        self.rows = (
            []
            if rows is None
            else rows
        )

        self.added = []
        self.statements = []
        self.flush_count = 0
        self.commit_count = 0


    async def execute(
        self,
        statement,
    ):

        self.statements.append(
            statement
        )

        text = str(
            statement
        ).lstrip().upper()

        if text.startswith(
            "SELECT"
        ):

            return FakeResult(
                self.rows
            )

        return FakeResult()


    def add(
        self,
        row,
    ):

        self.added.append(
            row
        )


    async def flush(
        self,
    ):

        self.flush_count += 1


    async def commit(
        self,
    ):

        self.commit_count += 1


def position(
    *,
    symbol,
    position_hash,
):

    return SimpleNamespace(
        position_id_hash=position_hash,
        symbol=symbol,
        instrument_kind="EQUITY",
        currency="CAD",
        quantity=Decimal(
            "1.25"
        ),
        average_entry_price=Decimal(
            "100"
        ),
        current_price=Decimal(
            "110"
        ),
        market_value=Decimal(
            "137.50"
        ),
        cost_basis=Decimal(
            "125"
        ),
        unrealized_gain=Decimal(
            "12.50"
        ),
        read_only=True,
    )


def snapshot(
    *,
    positions,
):

    return SimpleNamespace(
        source_provider="snaptrade",
        read_only=True,
        trading_enabled=False,
        order_operations_enabled=False,
        accounts=(
            SimpleNamespace(
                account_id_hash=HASH_A,
                positions=tuple(
                    positions
                ),
            ),
        ),
    )


@pytest.mark.asyncio
async def test_reconciliation_inserts_only_external_rows() -> None:

    session = FakeSession()

    result = await (
        reconcile_external_snaptrade_portfolio(
            session=session,
            neurovest_user_id="owner-123",
            snapshot=snapshot(
                positions=[
                    position(
                        symbol="TD.TO",
                        position_hash=HASH_B,
                    ),
                ]
            ),
        )
    )

    assert result.inserted == 1
    assert result.updated == 0
    assert result.removed == 0
    assert result.position_count == 1

    assert result.symbols == (
        "TD.TO",
    )

    assert len(
        session.added
    ) == 1

    row = session.added[
        0
    ]

    assert (
        row.neurovest_user_id
        ==
        "owner-123"
    )

    assert (
        row.account_id_hash
        ==
        HASH_A
    )

    assert (
        row.position_id_hash
        ==
        HASH_B
    )

    assert row.symbol == "TD.TO"
    assert row.read_only is True

    assert session.flush_count == 1
    assert session.commit_count == 0


@pytest.mark.asyncio
async def test_reconciliation_stale_delete_is_owner_scoped() -> None:

    existing = SimpleNamespace(
        account_id_hash=HASH_A,
        position_id_hash=HASH_B,
    )

    session = FakeSession(
        rows=[
            existing,
        ]
    )

    result = await (
        reconcile_external_snaptrade_portfolio(
            session=session,
            neurovest_user_id="owner-123",
            snapshot=snapshot(
                positions=[]
            ),
        )
    )

    assert result.removed == 1
    assert result.position_count == 0

    statements = [
        str(
            statement
        )
        for statement
        in session.statements
    ]

    delete_statements = [
        statement
        for statement
        in statements
        if statement.lstrip().upper().startswith(
            "DELETE"
        )
    ]

    assert len(
        delete_statements
    ) == 1

    delete_sql = delete_statements[
        0
    ]

    assert (
        "neurovest_user_id"
        in delete_sql
    )

    assert (
        "account_id_hash"
        in delete_sql
    )

    assert (
        "position_id_hash"
        in delete_sql
    )

    assert session.commit_count == 0


@pytest.mark.asyncio
async def test_reconciliation_rejects_trading_enabled_snapshot() -> None:

    unsafe = snapshot(
        positions=[]
    )

    unsafe.trading_enabled = True

    with pytest.raises(
        SnapTradeExternalPortfolioInventoryError
    ):

        await (
            reconcile_external_snaptrade_portfolio(
                session=FakeSession(),
                neurovest_user_id="owner-123",
                snapshot=unsafe,
            )
        )


@pytest.mark.asyncio
async def test_reconciliation_rejects_unhashed_account_id() -> None:

    unsafe = SimpleNamespace(
        source_provider="snaptrade",
        read_only=True,
        trading_enabled=False,
        order_operations_enabled=False,
        accounts=(
            SimpleNamespace(
                account_id_hash="raw-account-id",
                positions=(),
            ),
        ),
    )

    with pytest.raises(
        SnapTradeExternalPortfolioInventoryError
    ):

        await (
            reconcile_external_snaptrade_portfolio(
                session=FakeSession(),
                neurovest_user_id="owner-123",
                snapshot=unsafe,
            )
        )

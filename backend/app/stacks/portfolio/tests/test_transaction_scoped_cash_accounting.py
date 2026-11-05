from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace

import pytest

from backend.app.stacks.portfolio.accounting import (
    calculate_cash_in_session,
)


class FakeResult:
    def __init__(self, rows):
        self.rows = rows

    def scalars(self):
        return self

    def all(self):
        return self.rows


class FakeSession:
    def __init__(self, rows):
        self.rows = rows
        self.statements = []

    async def execute(self, statement):
        self.statements.append(str(statement))
        return FakeResult(self.rows)


def order(
    *,
    id=100,
    signal="BUY",
    status="executed",
    capital="100",
    fee="1",
    symbol="AAPL",
    timestamp=None,
):
    return SimpleNamespace(
        id=id,
        signal=signal,
        status=status,
        allocated_capital=capital,
        commission_paid=fee,
        slippage_price="150",
        symbol=symbol,
        timestamp=timestamp or datetime(2026, 10, 13),
    )


async def read(rows, user=" owner-1 "):
    session = FakeSession(rows)
    result = await calculate_cash_in_session(
        session=session,
        user_id=user,
    )
    return result, session


async def test_no_orders_retains_initial_cash():
    result, session = await read([])
    assert Decimal(result["current_cash_balance"]) == 100000
    assert result["net_liquidation_value"] is None
    assert result["execution_authorized"] is False
    assert result["user_id"] == "owner-1"
    assert len(session.statements) == 1
    assert "order_history.user_id" in session.statements[0]


async def test_buy_and_commission():
    result, _ = await read([
        order(signal="BUY", capital="1000", fee="1")
    ])
    assert Decimal(result["current_cash_balance"]) == 98999


async def test_sell_restores_cash_minus_fee():
    result, _ = await read([
        order(signal="BUY", capital="1000"),
        order(id=101, signal="SELL", capital="400"),
    ])
    assert Decimal(result["current_cash_balance"]) == 99398
    assert Decimal(result["total_fees_paid"]) == 2


async def test_nonexecuted_record_does_not_move_cash():
    result, _ = await read([
        order(status="rejected", capital="5000")
    ])
    assert Decimal(result["current_cash_balance"]) == 100000


async def test_verified_legacy_hold_is_excluded():
    result, _ = await read([
        order(
            id=5,
            signal="HOLD",
            capital="7826",
            symbol="AAPL",
            timestamp=datetime(2026, 7, 4),
        )
    ])
    assert Decimal(result["current_cash_balance"]) == 100000
    assert result["executed_trade_count"] == 0


async def test_other_executed_hold_is_rejected():
    with pytest.raises(
        ValueError,
        match="Unsupported executed cash-flow action",
    ):
        await read([
            order(id=99, signal="HOLD", capital="7826")
        ])


async def test_invalid_cash_values_fail_closed():
    with pytest.raises(ValueError):
        await read([order(capital="NaN")])


async def test_missing_owner_rejected():
    session = FakeSession([])
    with pytest.raises(ValueError):
        await calculate_cash_in_session(
            session=session,
            user_id=" ",
        )
    assert session.statements == []


async def test_missing_session_rejected():
    with pytest.raises(ValueError):
        await calculate_cash_in_session(
            session=None,
            user_id="owner-1",
        )

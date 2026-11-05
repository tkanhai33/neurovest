from __future__ import annotations

from decimal import Decimal
from types import SimpleNamespace

import pytest

from backend.app.stacks.journal_ledger.ledger import (
    read_inventory_in_session,
)


class Result:
    def __init__(self, values):
        self.values = values

    def scalars(self):
        return self

    def all(self):
        return self.values


class Session:
    def __init__(self, values):
        self.values = values
        self.queries = []

    async def execute(self, statement):
        self.queries.append(str(statement))
        return Result(self.values)


def position(
    symbol="AAPL",
    quantity="2",
    cost="200",
    entry="100",
):
    return SimpleNamespace(
        symbol=symbol,
        shares_quantity=quantity,
        total_cost_basis=cost,
        average_entry_price=entry,
    )


async def read(values, owner="owner-1"):
    session = Session(values)
    output = await read_inventory_in_session(
        session=session,
        user_id=owner,
    )
    return output, session


async def test_empty_inventory():
    output, session = await read([])
    assert output == []
    assert len(session.queries) == 1
    assert "portfolio_inventory.user_id" in session.queries[0]


async def test_valid_inventory():
    output, _ = await read([position()])
    assert output == [{
        "symbol": "AAPL",
        "shares_quantity": "2",
        "total_cost_basis": "200",
        "average_entry_price": "100",
    }]


async def test_symbol_normalization():
    output, _ = await read([position(symbol=" aapl ")])
    assert output[0]["symbol"] == "AAPL"


async def test_closed_zero_position_excluded():
    output, _ = await read([
        position(quantity="0", cost="0", entry="100")
    ])
    assert output == []


async def test_duplicate_symbol_fails_closed():
    with pytest.raises(ValueError, match="duplicate"):
        await read([
            position(symbol="AAPL"),
            position(symbol="aapl"),
        ])


@pytest.mark.parametrize(
    "quantity",
    ["NaN", "Infinity", "-1", "bad"],
)
async def test_invalid_quantity_fails_closed(quantity):
    with pytest.raises(ValueError):
        await read([position(quantity=quantity)])


async def test_missing_entry_fails_closed():
    with pytest.raises(ValueError):
        await read([position(entry="0")])


async def test_invalid_cost_fails_closed():
    with pytest.raises(ValueError):
        await read([position(cost="-2")])


async def test_zero_quantity_with_cost_fails_closed():
    with pytest.raises(ValueError):
        await read([position(quantity="0", cost="100")])


async def test_missing_owner_fails_before_query():
    session = Session([position()])
    with pytest.raises(ValueError):
        await read_inventory_in_session(
            session=session,
            user_id=" ",
        )
    assert session.queries == []


async def test_missing_session_fails():
    with pytest.raises(ValueError):
        await read_inventory_in_session(
            session=None,
            user_id="owner-1",
        )

from __future__ import annotations

from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from backend.app.stacks.risk.high_water_repository import (
    advance_persisted_high_water,
)
from backend.app.stacks.risk.equity_high_water import (
    HighWaterStateUnavailable,
)


EQUITY = {
    "status": "verified",
    "cash": "4000",
    "gross_long_exposure": "6000",
    "net_liquidation_value": "10000",
    "risk_limits_enforced": False,
}


class FakeResult:
    def __init__(self, row):
        self.row = row

    def mappings(self):
        return self

    def one_or_none(self):
        return self.row


class FakeSession:
    def __init__(
        self,
        *,
        row=None,
        transaction=True,
        changed=None,
    ):
        self.transaction = transaction
        self.row = row
        self.changed = changed
        self.statements = []

    def in_transaction(self):
        return self.transaction

    async def execute(self, statement, params):
        statement_text = str(statement)
        self.statements.append((statement_text, params))

        if "FOR UPDATE" in statement_text:
            return FakeResult(self.row)

        if "UPDATE paper_equity_high_water" in statement_text:
            return FakeResult(self.changed)

        raise AssertionError("unexpected statement")


def state(*, peak=Decimal("10000"), revision=1):
    return {
        "user_id": "owner-1",
        "currency": "USD",
        "peak_equity": peak,
        "revision": revision,
    }


async def evaluate(session, **kwargs):
    return await advance_persisted_high_water(
        session=session,
        owner=kwargs.get("owner", "owner-1"),
        currency=kwargs.get("currency", "USD"),
        verified_equity=kwargs.get("equity", EQUITY),
    )


async def test_same_peak_reads_under_lock_without_update():
    session = FakeSession(row=state())
    result = await evaluate(session)

    assert result["new_peak"] == "10000"
    assert result["pending_transaction_commit"] is False
    assert result["execution_authorized"] is False
    assert len(session.statements) == 1
    assert "FOR UPDATE" in session.statements[0][0]


async def test_higher_equity_updates_inside_transaction():
    session = FakeSession(
        row=state(peak=Decimal("9000")),
        changed={
            "user_id": "owner-1",
            "revision": 2,
            "peak_equity": Decimal("10000"),
        },
    )

    result = await evaluate(session)

    assert result["new_peak"] == "10000"
    assert result["new_revision"] == 2
    assert result["pending_transaction_commit"] is True
    assert result["persisted"] is False
    assert len(session.statements) == 2
    assert "UPDATE paper_equity_high_water" in session.statements[1][0]


async def test_missing_owner_row_fails_closed():
    session = FakeSession(row=None)

    with pytest.raises(
        HighWaterStateUnavailable,
        match="persistent_high_water_missing",
    ):
        await evaluate(session)


async def test_no_transaction_fails_before_query():
    session = FakeSession(
        row=state(),
        transaction=False,
    )

    with pytest.raises(
        HighWaterStateUnavailable,
        match="transaction_required",
    ):
        await evaluate(session)

    assert session.statements == []


async def test_owner_mismatch_rejected():
    row = state()
    row["user_id"] = "other-owner"
    session = FakeSession(row=row)

    with pytest.raises(
        HighWaterStateUnavailable,
        match="persistent_owner_mismatch",
    ):
        await evaluate(session)


async def test_currency_mismatch_rejected():
    row = state()
    row["currency"] = "CAD"
    session = FakeSession(row=row)

    with pytest.raises(
        HighWaterStateUnavailable,
        match="persistent_currency_mismatch",
    ):
        await evaluate(session)


async def test_revision_conflict_fails_closed():
    session = FakeSession(
        row=state(peak=Decimal("9000")),
        changed=None,
    )

    with pytest.raises(
        HighWaterStateUnavailable,
        match="persistent_high_water_conflict",
    ):
        await evaluate(session)


async def test_unverified_equity_fails_closed():
    session = FakeSession(row=state())

    with pytest.raises(HighWaterStateUnavailable):
        await evaluate(
            session,
            equity={
                **EQUITY,
                "status": "unavailable",
            },
        )


async def test_no_database_commit_issued():
    session = FakeSession(row=state())
    await evaluate(session)

    assert not hasattr(session, "commit")
    assert len(session.statements) == 1


async def test_blank_owner_rejected_before_query():
    session = FakeSession(row=state())

    with pytest.raises(HighWaterStateUnavailable):
        await evaluate(session, owner=" ")

    assert session.statements == []


async def test_invalid_currency_rejected_before_query():
    session = FakeSession(row=state())

    with pytest.raises(HighWaterStateUnavailable):
        await evaluate(session, currency="")

    assert session.statements == []

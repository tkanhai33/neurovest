from __future__ import annotations

import asyncio

import pytest

from backend.app.stacks.execution.commit_outcome_reconciliation import (
    CommitOutcome,
    reconcile_commit_outcome,
)


REQUEST = "45000000-0000-4000-8000-000000000045"
FINGERPRINT = "d" * 64
OWNER = "r45-test-owner"


class FakeResult:
    def __init__(self, rows):
        self.rows = rows

    def mappings(self):
        return self

    def all(self):
        return self.rows


class FakeSession:
    def __init__(self, rows=None, error=None):
        self.rows = [] if rows is None else rows
        self.error = error
        self.calls = 0

    async def execute(self, statement, params):
        self.calls += 1

        assert params == {
            "owner": OWNER,
            "request_id": REQUEST,
        }

        assert "FROM order_history" in str(statement)

        if self.error is not None:
            raise self.error

        return FakeResult(self.rows)


def run(session, **overrides):
    kwargs = {
        "user_id": OWNER,
        "request_id": REQUEST,
        "request_fingerprint": FINGERPRINT,
    }
    kwargs.update(overrides)

    return asyncio.run(
        reconcile_commit_outcome(session, **kwargs)
    )


def test_confirmed_commit_never_authorizes_retry():
    result = run(FakeSession([
        {
            "id": 45,
            "request_fingerprint": FINGERPRINT,
        },
    ]))

    assert result.outcome == CommitOutcome.CONFIRMED_COMMITTED
    assert result.order_id == 45
    assert result.retry_authorized is False


def test_missing_row_remains_uncertain():
    result = run(FakeSession([]))

    assert result.outcome == CommitOutcome.NOT_OBSERVED_UNCERTAIN
    assert result.order_id is None
    assert result.retry_authorized is False


def test_database_unavailable_remains_uncertain():
    result = run(
        FakeSession(error=ConnectionError("private test failure"))
    )

    assert result.outcome == CommitOutcome.UNAVAILABLE_UNCERTAIN
    assert result.retry_authorized is False


def test_conflicting_fingerprint_is_blocked():
    result = run(FakeSession([
        {
            "id": 45,
            "request_fingerprint": "e" * 64,
        },
    ]))

    assert result.outcome == CommitOutcome.CONFLICT
    assert result.retry_authorized is False


def test_duplicate_identity_is_conflict():
    result = run(FakeSession([
        {"id": 45, "request_fingerprint": FINGERPRINT},
        {"id": 46, "request_fingerprint": FINGERPRINT},
    ]))

    assert result.outcome == CommitOutcome.CONFLICT
    assert result.retry_authorized is False


def test_invalid_uuid_rejected_before_database_access():
    session = FakeSession()

    with pytest.raises(ValueError):
        run(session, request_id="not-a-uuid")

    assert session.calls == 0


def test_invalid_fingerprint_rejected():
    session = FakeSession()

    with pytest.raises(ValueError):
        run(session, request_fingerprint="INVALID")

    assert session.calls == 0


def test_invalid_record_identifier_is_conflict():
    result = run(FakeSession([
        {
            "id": None,
            "request_fingerprint": FINGERPRINT,
        },
    ]))

    assert result.outcome == CommitOutcome.CONFLICT
    assert result.retry_authorized is False

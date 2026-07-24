#!/usr/bin/env python3

"""
NeuroVest Workstream 3 — Stage 5D

Concurrent Append, Idempotency, Sequence,
and Hash-Chain Qualification.

This qualification:

- uses the canonical DecisionEventRepository
- creates one AsyncSession per concurrent append
- verifies concurrent sequence allocation
- verifies the persisted hash chain
- verifies event IDs and idempotency keys
- verifies duplicate idempotency behavior
- removes only Stage 5D qualification rows afterward
- does not change runtime wiring or API composition
"""

from __future__ import annotations

import asyncio
import json
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import select, text

from backend.app.stacks.db_runtime.database import (
    async_session,
    engine,
)
from backend.app.stacks.journal_ledger.decision_event_contract import (
    DecisionEventDraft,
    DecisionEventType,
    DecisionOutcome,
    PersistedDecisionEvent,
)
from backend.app.stacks.journal_ledger.decision_event_model import (
    DecisionEventRecord,
)
from backend.app.stacks.journal_ledger.decision_event_repository import (
    DecisionEventRepository,
)


ROOT = Path(".").resolve()

STAGE_DIR = (
    ROOT
    / "runtime"
    / "hardening"
    / "workstream3"
    / "stage5"
)

OUTPUT_JSON = (
    STAGE_DIR
    / "stage5d_concurrent_append_qualification_latest.json"
)

OUTPUT_TEXT = (
    STAGE_DIR
    / "stage5d_concurrent_append_qualification_latest.txt"
)

CONCURRENCY = 25
QUALIFICATION_ACTOR = "stage5d-qualifier"
QUALIFICATION_SOURCE = "stage5d-concurrent-qualification"


def first_enum_member(
    enum_type: type[Any],
) -> Any:
    members = list(
        enum_type
    )

    if not members:
        raise AssertionError(
            f"{enum_type.__name__} contains no members"
        )

    return members[0]


EVENT_TYPE = first_enum_member(
    DecisionEventType
)

OUTCOME = first_enum_member(
    DecisionOutcome
)


def make_draft(
    *,
    index: int,
    event_id: UUID | None = None,
    idempotency_key: str | None = None,
    correlation_id: UUID | None = None,
) -> DecisionEventDraft:
    occurred_at = datetime(
        2026,
        7,
        10,
        21,
        0,
        0,
        tzinfo=UTC,
    ) + timedelta(
        microseconds=index
    )

    return DecisionEventDraft(
        event_id=(
            event_id
            or uuid4()
        ),
        idempotency_key=(
            idempotency_key
            or (
                "stage5d-concurrent-"
                f"{index:04d}-"
                f"{uuid4()}"
            )
        ),
        event_type=EVENT_TYPE,
        outcome=OUTCOME,
        occurred_at=occurred_at,
        actor=QUALIFICATION_ACTOR,
        source=QUALIFICATION_SOURCE,
        correlation_id=(
            correlation_id
            or uuid4()
        ),
        causation_id=None,
        symbol="AAPL",
        confidence=0.75,
        reason=(
            "Workstream 3 Stage 5D "
            "concurrent append qualification"
        ),
        payload={
            "workstream": 3,
            "stage": "5D",
            "index": index,
            "qualification": True,
        },
    )


async def append_draft(
    draft: DecisionEventDraft,
    *,
    recorded_at: datetime,
) -> dict[str, Any]:
    started = time.perf_counter()

    try:
        async with async_session() as session:
            repository = DecisionEventRepository(
                session
            )

            persisted = await repository.append(
                draft,
                recorded_at=recorded_at,
            )

        assert isinstance(
            persisted,
            PersistedDecisionEvent,
        )

        return {
            "status": "success",
            "duration_ms": round(
                (
                    time.perf_counter()
                    - started
                )
                * 1000,
                3,
            ),
            "event_id": str(
                persisted.draft.event_id
            ),
            "idempotency_key": (
                persisted.draft.idempotency_key
            ),
            "sequence_number": (
                persisted.sequence_number
            ),
            "previous_hash": (
                persisted.previous_hash
            ),
            "content_hash": (
                persisted.content_hash
            ),
        }

    except Exception as exc:
        return {
            "status": "error",
            "duration_ms": round(
                (
                    time.perf_counter()
                    - started
                )
                * 1000,
                3,
            ),
            "event_id": str(
                draft.event_id
            ),
            "idempotency_key": (
                draft.idempotency_key
            ),
            "exception_type": (
                type(exc).__name__
            ),
            "exception": str(
                exc
            ),
        }


async def database_row_count() -> int:
    async with engine.connect() as connection:
        count = (
            await connection.execute(
                text(
                    "SELECT COUNT(*) "
                    "FROM decision_events"
                )
            )
        ).scalar_one()

    return int(
        count
    )


async def current_revision() -> str:
    async with engine.connect() as connection:
        revision = (
            await connection.execute(
                text(
                    "SELECT version_num "
                    "FROM alembic_version"
                )
            )
        ).scalar_one()

    return str(
        revision
    )


async def load_qualification_records() -> list[
    DecisionEventRecord
]:
    async with async_session() as session:
        result = await session.execute(
            select(
                DecisionEventRecord
            )
            .where(
                DecisionEventRecord.actor
                == QUALIFICATION_ACTOR
            )
            .where(
                DecisionEventRecord.source
                == QUALIFICATION_SOURCE
            )
            .order_by(
                DecisionEventRecord.sequence_number
            )
        )

        return list(
            result.scalars().all()
        )


async def remove_qualification_records() -> int:
    """
    Remove only Stage 5D qualification fixtures.

    This direct cleanup is isolated to the qualification script.
    The application repository remains append-only and exposes no
    update or delete method.
    """

    async with engine.begin() as connection:
        result = await connection.execute(
            text(
                """
                DELETE FROM decision_events
                WHERE actor = :actor
                  AND source = :source
                """
            ),
            {
                "actor": QUALIFICATION_ACTOR,
                "source": QUALIFICATION_SOURCE,
            },
        )

        return int(
            result.rowcount
            or 0
        )


def validate_hash_chain(
    records: list[
        DecisionEventRecord
    ],
) -> None:
    assert records, (
        "No Stage 5D records were persisted"
    )

    expected_sequences = list(
        range(
            1,
            len(records) + 1,
        )
    )

    actual_sequences = [
        record.sequence_number
        for record in records
    ]

    assert actual_sequences == expected_sequences, (
        "Sequence numbers are not contiguous. "
        f"Expected {expected_sequences}; "
        f"found {actual_sequences}"
    )

    assert records[0].previous_hash is None, (
        "Genesis event must have no previous hash"
    )

    # Adjacent-pair comparison intentionally uses sequences
    # with lengths N and N-1. strict=True is invalid here because
    # the unequal lengths are expected.
    for previous, current in zip(
        records,
        records[1:],
    ):
        assert (
            current.previous_hash
            == previous.content_hash
        ), (
            "Hash chain is broken between "
            f"sequence {previous.sequence_number} "
            f"and {current.sequence_number}"
        )

    content_hashes = [
        record.content_hash
        for record in records
    ]

    event_ids = [
        record.event_id
        for record in records
    ]

    idempotency_keys = [
        record.idempotency_key
        for record in records
    ]

    assert len(
        content_hashes
    ) == len(
        set(
            content_hashes
        )
    ), "Duplicate content hashes were persisted"

    assert len(
        event_ids
    ) == len(
        set(
            event_ids
        )
    ), "Duplicate event IDs were persisted"

    assert len(
        idempotency_keys
    ) == len(
        set(
            idempotency_keys
        )
    ), "Duplicate idempotency keys were persisted"


async def main() -> int:
    STAGE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    revision_before = await current_revision()

    assert revision_before == (
        "ws3_stage5_decision_events"
    )

    rows_before = await database_row_count()

    assert rows_before == 0, (
        "Stage 5D requires decision_events to be empty "
        f"before qualification; found {rows_before} rows"
    )

    started_at = datetime.now(
        UTC
    )

    batch_results: list[
        dict[
            str,
            Any,
        ]
    ] = []

    duplicate_results: list[
        dict[
            str,
            Any,
        ]
    ] = []

    cleanup_count = 0
    rows_after_cleanup = -1

    try:
        print(
            "Starting concurrent append batch:",
            CONCURRENCY,
        )

        drafts = [
            make_draft(
                index=index
            )
            for index in range(
                CONCURRENCY
            )
        ]

        recorded_base = datetime(
            2026,
            7,
            10,
            21,
            30,
            0,
            tzinfo=UTC,
        )

        batch_started = time.perf_counter()

        batch_results = list(
            await asyncio.gather(
                *[
                    append_draft(
                        draft,
                        recorded_at=(
                            recorded_base
                            + timedelta(
                                microseconds=index
                            )
                        ),
                    )
                    for index, draft
                    in enumerate(
                        drafts
                    )
                ]
            )
        )

        batch_duration_ms = round(
            (
                time.perf_counter()
                - batch_started
            )
            * 1000,
            3,
        )

        batch_successes = [
            result
            for result in batch_results
            if result[
                "status"
            ] == "success"
        ]

        batch_errors = [
            result
            for result in batch_results
            if result[
                "status"
            ] == "error"
        ]

        print(
            "Concurrent successes:",
            len(
                batch_successes
            ),
        )

        print(
            "Concurrent errors:",
            len(
                batch_errors
            ),
        )

        if batch_errors:
            print(
                json.dumps(
                    batch_errors,
                    indent=2,
                    sort_keys=True,
                )
            )

        assert len(
            batch_successes
        ) == CONCURRENCY, (
            "Not every concurrent append succeeded"
        )

        assert not batch_errors

        persisted_after_batch = (
            await load_qualification_records()
        )

        assert len(
            persisted_after_batch
        ) == CONCURRENCY

        validate_hash_chain(
            persisted_after_batch
        )

        print(
            "PASS: concurrent sequence allocation"
        )
        print(
            "PASS: contiguous sequence numbers"
        )
        print(
            "PASS: hash chain is continuous"
        )
        print(
            "PASS: content hashes are unique"
        )

        duplicate_event_id = uuid4()
        duplicate_key = (
            "stage5d-duplicate-race-"
            f"{uuid4()}"
        )
        duplicate_correlation = uuid4()

        duplicate_draft = make_draft(
            index=CONCURRENCY + 1,
            event_id=duplicate_event_id,
            idempotency_key=duplicate_key,
            correlation_id=(
                duplicate_correlation
            ),
        )

        duplicate_recorded_at = datetime(
            2026,
            7,
            10,
            22,
            0,
            0,
            tzinfo=UTC,
        )

        duplicate_results = list(
            await asyncio.gather(
                append_draft(
                    duplicate_draft,
                    recorded_at=(
                        duplicate_recorded_at
                    ),
                ),
                append_draft(
                    duplicate_draft,
                    recorded_at=(
                        duplicate_recorded_at
                        + timedelta(
                            microseconds=1
                        )
                    ),
                ),
            )
        )

        duplicate_successes = [
            result
            for result in duplicate_results
            if result[
                "status"
            ] == "success"
        ]

        duplicate_errors = [
            result
            for result in duplicate_results
            if result[
                "status"
            ] == "error"
        ]

        assert len(
            duplicate_successes
        ) == 1, (
            "Duplicate race must persist exactly one event"
        )

        assert len(
            duplicate_errors
        ) == 1, (
            "Duplicate race must reject exactly one event"
        )

        print(
            "PASS: duplicate race persisted exactly once"
        )
        print(
            "PASS: duplicate idempotency was rejected"
        )

        final_records = (
            await load_qualification_records()
        )

        assert len(
            final_records
        ) == CONCURRENCY + 1

        validate_hash_chain(
            final_records
        )

        final_sequences = [
            record.sequence_number
            for record in final_records
        ]

        final_hashes = [
            record.content_hash
            for record in final_records
        ]

        completed_at = datetime.now(
            UTC
        )

        report = {
            "workstream": 3,
            "stage": "5D",
            "stage_name": (
                "Concurrent Append, Idempotency, "
                "Sequence, and Hash-Chain Qualification"
            ),
            "status": "completed",
            "started_at": (
                started_at.isoformat()
            ),
            "completed_at": (
                completed_at.isoformat()
            ),
            "revision": revision_before,
            "concurrency": CONCURRENCY,
            "concurrent_attempts": CONCURRENCY,
            "concurrent_successes": len(
                batch_successes
            ),
            "concurrent_errors": len(
                batch_errors
            ),
            "batch_duration_ms": (
                batch_duration_ms
            ),
            "duplicate_race_attempts": 2,
            "duplicate_race_successes": len(
                duplicate_successes
            ),
            "duplicate_race_rejections": len(
                duplicate_errors
            ),
            "persisted_before_cleanup": len(
                final_records
            ),
            "sequence_numbers": (
                final_sequences
            ),
            "sequence_contiguous": True,
            "duplicate_sequence_numbers": False,
            "hash_chain_continuous": True,
            "genesis_previous_hash_null": True,
            "content_hashes_unique": (
                len(
                    final_hashes
                )
                == len(
                    set(
                        final_hashes
                    )
                )
            ),
            "event_ids_unique": True,
            "idempotency_keys_unique": True,
            "duplicate_idempotency_rejected": True,
            "duplicate_event_persisted_once": True,
            "repository_append_used": True,
            "canonical_transaction_manager_used": True,
            "runtime_wiring_changed": False,
            "api_routes_added": False,
            "migration_rerun": False,
            "downgrade_performed": False,
            "broker_execution_enabled": False,
            "live_trading_enabled": False,
            "batch_results": batch_results,
            "duplicate_results": (
                duplicate_results
            ),
        }

        OUTPUT_JSON.write_text(
            json.dumps(
                report,
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )

    finally:
        cleanup_count = (
            await remove_qualification_records()
        )

        rows_after_cleanup = (
            await database_row_count()
        )

        print(
            "Qualification rows removed:",
            cleanup_count,
        )

        print(
            "Database rows after cleanup:",
            rows_after_cleanup,
        )

    assert rows_after_cleanup == 0, (
        "Stage 5D cleanup did not restore "
        "decision_events to zero rows"
    )

    revision_after = await current_revision()

    assert revision_after == revision_before

    report = json.loads(
        OUTPUT_JSON.read_text(
            encoding="utf-8"
        )
    )

    report[
        "qualification_rows_removed"
    ] = cleanup_count

    report[
        "rows_after_cleanup"
    ] = rows_after_cleanup

    report[
        "database_restored_to_empty"
    ] = True

    report[
        "revision_unchanged"
    ] = True

    OUTPUT_JSON.write_text(
        json.dumps(
            report,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    lines = [
        "=" * 80,
        "NEUROVEST WORKSTREAM 3",
        (
            "STAGE 5D — CONCURRENT APPEND, "
            "IDEMPOTENCY, SEQUENCE, AND HASH CHAIN"
        ),
        "=" * 80,
        "",
        "STATUS",
        "COMPLETE AND VERIFIED",
        "",
        "CONCURRENT APPEND",
        (
            "Concurrent attempts:              "
            f"{CONCURRENCY}"
        ),
        (
            "Successful appends:               "
            f"{report['concurrent_successes']}"
        ),
        (
            "Append errors:                    "
            f"{report['concurrent_errors']}"
        ),
        (
            "Batch duration:                   "
            f"{report['batch_duration_ms']} ms"
        ),
        "",
        "SEQUENCE",
        "Contiguous sequence numbers:       PASS",
        "Duplicate sequence numbers:        NONE",
        "",
        "HASH CHAIN",
        "Genesis previous hash:             NULL",
        "Previous-hash continuity:          PASS",
        "Unique content hashes:             PASS",
        "",
        "IDEMPOTENCY",
        "Duplicate race attempts:           2",
        "Rows persisted from duplicate:     1",
        "Duplicate attempts rejected:       1",
        "Idempotency enforcement:           PASS",
        "",
        "CLEANUP",
        (
            "Qualification rows removed:       "
            f"{cleanup_count}"
        ),
        "Rows remaining:                    0",
        "Database restored to empty:        YES",
        "",
        "SAFETY",
        "Migration rerun:                   NO",
        "Downgrade performed:               NO",
        "Runtime wiring changed:            NO",
        "API routes added:                  NO",
        "Broker execution enabled:          NO",
        "Live trading enabled:              NO",
        "",
        "NEXT",
        (
            "Workstream 3 Stage 6 — Append-Only "
            "Decision Audit Service Integration"
        ),
        "",
        "=" * 80,
    ]

    rendered = (
        "\n".join(
            lines
        )
        + "\n"
    )

    OUTPUT_TEXT.write_text(
        rendered,
        encoding="utf-8",
    )

    print(
        rendered
    )

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(
            asyncio.run(
                main()
            )
        )

    except Exception as exc:
        print("=" * 80)
        print("WORKSTREAM 3 STAGE 5D FAILED")
        print("=" * 80)
        print()
        print(
            f"{type(exc).__name__}: {exc}"
        )
        print()
        print(
            "Any Stage 5D qualification rows were "
            "targeted for cleanup."
        )
        print(
            "The migration was not rerun."
        )
        print(
            "No downgrade was performed."
        )
        print("=" * 80)

        raise SystemExit(1)

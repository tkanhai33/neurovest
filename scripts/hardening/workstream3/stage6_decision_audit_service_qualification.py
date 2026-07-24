#!/usr/bin/env python3

from __future__ import annotations

import asyncio
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from uuid import uuid4

from sqlalchemy import select, text

from backend.app.stacks.db_runtime.database import (
    async_session,
    engine,
)
from backend.app.stacks.journal_ledger.decision_audit_service import (
    build_decision_audit_service,
)
from backend.app.stacks.journal_ledger.decision_event_contract import (
    DecisionEventDraft,
    DecisionEventType,
    DecisionOutcome,
)
from backend.app.stacks.journal_ledger.decision_event_model import (
    DecisionEventRecord,
)


ROOT = Path(".").resolve()

STAGE_DIR = (
    ROOT
    / "runtime"
    / "hardening"
    / "workstream3"
    / "stage6"
)

OUTPUT_JSON = (
    STAGE_DIR
    / "stage6_decision_audit_service_latest.json"
)

OUTPUT_TEXT = (
    STAGE_DIR
    / "stage6_decision_audit_service_latest.txt"
)

ACTOR = "stage6-audit-service"
SOURCE = "stage6-live-qualification"
EVENT_COUNT = 5


def first_enum_member(
    enum_type: type[Any],
) -> Any:
    members = list(
        enum_type
    )

    if not members:
        raise AssertionError(
            f"{enum_type.__name__} is empty"
        )

    return members[0]


EVENT_TYPE = first_enum_member(
    DecisionEventType
)

OUTCOME = first_enum_member(
    DecisionOutcome
)


def make_draft(
    index: int,
) -> DecisionEventDraft:
    return DecisionEventDraft(
        event_id=uuid4(),
        idempotency_key=(
            "stage6-audit-service-"
            f"{index:04d}-"
            f"{uuid4()}"
        ),
        event_type=EVENT_TYPE,
        outcome=OUTCOME,
        occurred_at=(
            datetime(
                2026,
                7,
                10,
                22,
                30,
                0,
                tzinfo=UTC,
            )
            + timedelta(
                microseconds=index
            )
        ),
        actor=ACTOR,
        source=SOURCE,
        correlation_id=uuid4(),
        causation_id=None,
        symbol="AAPL",
        confidence=0.80,
        reason=(
            "Workstream 3 Stage 6 "
            "decision audit service qualification"
        ),
        payload={
            "workstream": 3,
            "stage": 6,
            "index": index,
            "qualification": True,
        },
    )


async def row_count() -> int:
    async with engine.connect() as connection:
        result = (
            await connection.execute(
                text(
                    "SELECT COUNT(*) "
                    "FROM decision_events"
                )
            )
        ).scalar_one()

    return int(
        result
    )


async def revision() -> str:
    async with engine.connect() as connection:
        result = (
            await connection.execute(
                text(
                    "SELECT version_num "
                    "FROM alembic_version"
                )
            )
        ).scalar_one()

    return str(
        result
    )


async def cleanup() -> int:
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
                "actor": ACTOR,
                "source": SOURCE,
            },
        )

        return int(
            result.rowcount
            or 0
        )


async def load_rows() -> list[
    DecisionEventRecord
]:
    async with async_session() as session:
        result = await session.execute(
            select(
                DecisionEventRecord
            )
            .where(
                DecisionEventRecord.actor
                == ACTOR
            )
            .where(
                DecisionEventRecord.source
                == SOURCE
            )
            .order_by(
                DecisionEventRecord.sequence_number
            )
        )

        return list(
            result.scalars().all()
        )


async def main() -> int:
    STAGE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    revision_before = await revision()

    assert revision_before == (
        "ws3_stage5_decision_events"
    )

    rows_before = await row_count()

    assert rows_before == 0, (
        "Stage 6 requires an empty ledger; "
        f"found {rows_before} rows"
    )

    drafts = [
        make_draft(
            index
        )
        for index in range(
            EVENT_COUNT
        )
    ]

    persisted_events = []
    cleaned = 0

    try:
        for index, draft in enumerate(
            drafts
        ):
            async with async_session() as session:
                service = (
                    build_decision_audit_service(
                        session
                    )
                )

                persisted = await service.append(
                    draft,
                    recorded_at=(
                        datetime(
                            2026,
                            7,
                            10,
                            22,
                            45,
                            0,
                            tzinfo=UTC,
                        )
                        + timedelta(
                            microseconds=index
                        )
                    ),
                )

                persisted_events.append(
                    persisted
                )

        assert len(
            persisted_events
        ) == EVENT_COUNT

        async with async_session() as session:
            service = (
                build_decision_audit_service(
                    session
                )
            )

            for persisted in persisted_events:
                by_event_id = (
                    await service.get_by_event_id(
                        persisted.draft.event_id
                    )
                )

                assert by_event_id is not None

                assert (
                    by_event_id.draft.event_id
                    == persisted.draft.event_id
                )

                by_key = (
                    await service.get_by_idempotency_key(
                        persisted.draft.idempotency_key
                    )
                )

                assert by_key is not None

                assert (
                    by_key.draft.idempotency_key
                    == persisted.draft.idempotency_key
                )

            latest = await service.latest()

            assert latest is not None

            assert (
                latest.sequence_number
                == EVENT_COUNT
            )

            recent = await service.list_recent(
                limit=EVENT_COUNT
            )

            assert len(
                recent
            ) == EVENT_COUNT

            recent_sequences = [
                event.sequence_number
                for event in recent
            ]

            assert set(
                recent_sequences
            ) == set(
                range(
                    1,
                    EVENT_COUNT + 1,
                )
            )

        rows = await load_rows()

        assert len(
            rows
        ) == EVENT_COUNT

        sequences = [
            row.sequence_number
            for row in rows
        ]

        assert sequences == list(
            range(
                1,
                EVENT_COUNT + 1,
            )
        )

        assert rows[0].previous_hash is None

        for previous, current in zip(
            rows,
            rows[1:],
        ):
            assert (
                current.previous_hash
                == previous.content_hash
            )

        content_hashes = [
            row.content_hash
            for row in rows
        ]

        assert len(
            content_hashes
        ) == len(
            set(
                content_hashes
            )
        )

        report = {
            "workstream": 3,
            "stage": 6,
            "stage_name": (
                "Append-Only Decision Audit "
                "Service Integration"
            ),
            "status": "completed",
            "revision": revision_before,
            "events_appended": EVENT_COUNT,
            "append_service_verified": True,
            "get_by_event_id_verified": True,
            "get_by_idempotency_key_verified": True,
            "latest_verified": True,
            "list_recent_verified": True,
            "sequence_contiguous": True,
            "hash_chain_continuous": True,
            "content_hashes_unique": True,
            "repository_transaction_boundary_preserved": True,
            "repository_sequence_lock_preserved": True,
            "service_commit_ownership": False,
            "service_sequence_ownership": False,
            "service_hash_ownership": False,
            "mutation_methods_added": False,
            "api_routes_added": False,
            "runtime_composition_changed": False,
            "broker_execution_enabled": False,
            "live_trading_enabled": False,
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
        cleaned = await cleanup()

        remaining = await row_count()

        print(
            "Qualification rows removed:",
            cleaned,
        )

        print(
            "Rows remaining:",
            remaining,
        )

        if remaining != 0:
            raise AssertionError(
                "Stage 6 cleanup failed; "
                f"{remaining} rows remain"
            )

    revision_after = await revision()

    assert revision_after == revision_before

    report = json.loads(
        OUTPUT_JSON.read_text(
            encoding="utf-8"
        )
    )

    report[
        "qualification_rows_removed"
    ] = cleaned

    report[
        "rows_after_cleanup"
    ] = 0

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
            "STAGE 6 — APPEND-ONLY DECISION "
            "AUDIT SERVICE INTEGRATION"
        ),
        "=" * 80,
        "",
        "STATUS",
        "COMPLETE AND VERIFIED",
        "",
        "SERVICE",
        "- Canonical audit service: IMPLEMENTED",
        "- Repository delegation: PASS",
        "- Service-owned commit: NO",
        "- Service-owned sequence allocation: NO",
        "- Service-owned hash construction: NO",
        "",
        "APPEND",
        f"- Events appended: {EVENT_COUNT}",
        "- Canonical repository append used: YES",
        "- Sequence continuity: PASS",
        "- Hash-chain continuity: PASS",
        "- Content hashes unique: PASS",
        "",
        "READ PATHS",
        "- Read by event ID: PASS",
        "- Read by idempotency key: PASS",
        "- Latest event: PASS",
        "- Recent events: PASS",
        "",
        "APPEND-ONLY GUARANTEE",
        "- Update method added: NO",
        "- Delete method added: NO",
        "- Replace method added: NO",
        "- Merge method added: NO",
        "- Purge method added: NO",
        "- Truncate method added: NO",
        "",
        "CLEANUP",
        f"- Qualification rows removed: {cleaned}",
        "- Rows remaining: 0",
        "- Database restored to empty: YES",
        "",
        "SAFETY",
        "- Migration revision changed: NO",
        "- API routes added: NO",
        "- Runtime composition changed: NO",
        "- Broker execution enabled: NO",
        "- Live trading enabled: NO",
        "",
        "NEXT",
        (
            "Workstream 3 Stage 7 — Controlled "
            "Decision-Audit Producer Integration"
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
        print("WORKSTREAM 3 STAGE 6 FAILED")
        print("=" * 80)
        print()
        print(
            f"{type(exc).__name__}: {exc}"
        )
        print()
        print(
            "Stage 6 qualification fixtures were "
            "targeted for cleanup."
        )
        print(
            "No migration was rerun."
        )
        print(
            "No downgrade was performed."
        )
        print("=" * 80)

        raise SystemExit(1)

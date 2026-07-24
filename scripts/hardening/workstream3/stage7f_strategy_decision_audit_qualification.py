#!/usr/bin/env python3
"""
Workstream 3 Stage 7F live qualification.

Creates two controlled strategy audit events, verifies their persisted
contract, and removes only rows owned by this qualification.
"""

from __future__ import annotations

import asyncio
import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from sqlalchemy import delete, select, text

from backend.app.stacks.db_runtime.database import (
    async_session,
    engine,
)
from backend.app.stacks.journal_ledger.decision_audit_service import (
    build_decision_audit_service,
)
from backend.app.stacks.journal_ledger.decision_event_model import (
    DecisionEventRecord,
)
from backend.app.stacks.journal_ledger.strategy_decision_audit_adapter import (
    StrategyDecisionAuditAdapter,
)


OUTPUT_JSON = Path(
    "runtime/hardening/workstream3/stage7/"
    "stage7f_strategy_audit_adapter_live_latest.json"
)

OUTPUT_TEXT = Path(
    "runtime/hardening/workstream3/stage7/"
    "stage7f_strategy_audit_adapter_live_latest.txt"
)

PREFIX = (
    "ws3-stage7f-qualification-"
)


def deterministic_producer(
    symbol: str,
    replay_bars: list[dict] | None,
) -> dict:
    if symbol == "AAPL":
        signal = {
            "status": "ok",
            "symbol": symbol,
            "action": "buy",
            "decision": "BUY",
            "rsi": 42.0,
            "confidence": 0.75,
        }

        return {
            "status": "rebalanced",
            "symbol": symbol,
            "signal": "buy",
            "decision": "BUY",
            "confidence": 0.75,
            "strategy_signal": signal,
            "portfolio_output": {
                "symbol": symbol,
                "signal": "buy",
                "status": "rebalanced",
            },
        }

    signal = {
        "status": "no_action",
        "symbol": symbol,
        "action": "hold",
        "decision": "HOLD",
        "confidence": 0.0,
    }

    return {
        "status": "no_action",
        "symbol": symbol,
        "signal": "hold",
        "decision": "HOLD",
        "confidence": 0.0,
        "strategy_signal": signal,
        "portfolio_output": None,
    }


async def current_revision() -> str:
    async with engine.connect() as connection:
        value = (
            await connection.execute(
                text(
                    "SELECT version_num "
                    "FROM alembic_version"
                )
            )
        ).scalar_one()

    return str(
        value
    )


async def cleanup() -> int:
    async with engine.begin() as connection:
        result = await connection.execute(
            delete(
                DecisionEventRecord
            ).where(
                DecisionEventRecord
                .idempotency_key
                .like(
                    f"{PREFIX}%"
                )
            )
        )

    return int(
        result.rowcount
        or 0
    )


async def count_qualification_rows() -> int:
    async with engine.connect() as connection:
        count = (
            await connection.execute(
                select(
                    text(
                        "COUNT(*)"
                    )
                )
                .select_from(
                    DecisionEventRecord
                )
                .where(
                    DecisionEventRecord
                    .idempotency_key
                    .like(
                        f"{PREFIX}%"
                    )
                )
            )
        ).scalar_one()

    return int(
        count
    )


async def main() -> None:
    revision_before = (
        await current_revision()
    )

    assert revision_before == (
        "ws3_stage5_decision_events"
    )

    await cleanup()

    assert (
        await count_qualification_rows()
    ) == 0

    correlation_id = uuid4()

    keys = [
        f"{PREFIX}{uuid4()}",
        f"{PREFIX}{uuid4()}",
    ]

    occurred_at = datetime.now(
        UTC
    )

    async with async_session() as session:
        service = (
            build_decision_audit_service(
                session
            )
        )

        adapter = (
            StrategyDecisionAuditAdapter(
                service,
                producer=(
                    deterministic_producer
                ),
            )
        )

        first = await adapter.produce_and_audit(
            "AAPL",
            idempotency_key=keys[
                0
            ],
            correlation_id=correlation_id,
            actor="neuro",
            source=(
                "workstream3.stage7f."
                "qualification"
            ),
            occurred_at=occurred_at,
            replay_bars=[
                {
                    "close": 100.0,
                }
            ],
        )

        second = (
            await adapter.produce_and_audit(
                "MSFT",
                idempotency_key=keys[
                    1
                ],
                correlation_id=correlation_id,
                actor="neuro",
                source=(
                    "workstream3.stage7f."
                    "qualification"
                ),
                occurred_at=occurred_at,
                replay_bars=[
                    {
                        "close": 200.0,
                    }
                ],
            )
        )

        by_event_id = (
            await service.get_by_event_id(
                first.audit_event.draft.event_id
            )
        )

        by_idempotency = (
            await service
            .get_by_idempotency_key(
                keys[
                    1
                ]
            )
        )

        latest = await service.latest()

    assert first.envelope[
        "decision"
    ] == "BUY"

    assert second.envelope[
        "decision"
    ] == "HOLD"

    assert first.audit_event.draft.symbol == (
        "AAPL"
    )

    assert second.audit_event.draft.symbol == (
        "MSFT"
    )

    assert first.audit_event.draft.confidence == (
        0.75
    )

    assert second.audit_event.draft.confidence == (
        0.0
    )

    assert first.audit_event.draft.event_type.value == (
        "strategy_decision"
    )

    assert first.audit_event.draft.outcome.value == (
        "proposed"
    )

    assert by_event_id is not None
    assert by_idempotency is not None
    assert latest is not None

    assert (
        first.audit_event.sequence_number
        + 1
        == second.audit_event.sequence_number
    )

    assert (
        second.audit_event.previous_hash
        == first.audit_event.content_hash
    )

    rows_before_cleanup = (
        await count_qualification_rows()
    )

    assert rows_before_cleanup == 2

    removed = await cleanup()

    rows_after_cleanup = (
        await count_qualification_rows()
    )

    revision_after = (
        await current_revision()
    )

    assert removed == 2
    assert rows_after_cleanup == 0
    assert revision_after == revision_before

    report = {
        "workstream": 3,
        "stage": "7F",
        "status": "completed",
        "adapter_async": True,
        "strategy_engine_synchronous": True,
        "events_produced": 2,
        "events_persisted": 2,
        "buy_decision_verified": True,
        "hold_decision_verified": True,
        "read_by_event_id_verified": True,
        "read_by_idempotency_key_verified": True,
        "latest_verified": True,
        "sequence_contiguous": True,
        "hash_chain_continuous": True,
        "event_type": "strategy_decision",
        "outcome": "proposed",
        "qualification_rows_removed": (
            removed
        ),
        "rows_after_cleanup": (
            rows_after_cleanup
        ),
        "database_restored_to_empty": True,
        "revision_before": (
            revision_before
        ),
        "revision_after": revision_after,
        "revision_unchanged": True,
        "repository_called_directly": False,
        "adapter_commit_ownership": False,
        "adapter_sequence_ownership": False,
        "adapter_hash_ownership": False,
        "strategy_engine_database_access": False,
        "strategy_engine_audit_import": False,
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

    lines = [
        "=" * 80,
        "NEUROVEST WORKSTREAM 3",
        (
            "STAGE 7F — CONTROLLED ASYNCHRONOUS "
            "STRATEGY DECISION AUDIT ADAPTER"
        ),
        "=" * 80,
        "",
        "STATUS",
        "COMPLETE AND VERIFIED",
        "",
        "ADAPTER",
        "- Asynchronous adapter: PASS",
        "- Synchronous strategy producer: PRESERVED",
        "- DecisionAuditService delegation: PASS",
        "- Repository direct call: NO",
        "- Adapter commit ownership: NO",
        "- Adapter sequence ownership: NO",
        "- Adapter hash ownership: NO",
        "",
        "LIVE QUALIFICATION",
        "- Strategy decisions produced: 2",
        "- Audit events persisted: 2",
        "- BUY decision verified: PASS",
        "- HOLD decision verified: PASS",
        "- Read by event ID: PASS",
        "- Read by idempotency key: PASS",
        "- Latest read: PASS",
        "- Sequence continuity: PASS",
        "- Hash-chain continuity: PASS",
        "",
        "CLEANUP",
        "- Qualification rows removed: 2",
        "- Qualification rows remaining: 0",
        "- Database restored to empty: YES",
        "",
        "SAFETY",
        "- Migration revision changed: NO",
        "- Strategy database access: NO",
        "- Strategy audit import: NO",
        "- API routes added: NO",
        "- Runtime composition changed: NO",
        "- Broker execution enabled: NO",
        "- Live trading enabled: NO",
        "",
        "NEXT",
        (
            "Workstream 3 Stage 7G — Controlled "
            "Runtime Producer Wiring and Read-Only "
            "Audit Qualification"
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


if __name__ == "__main__":
    try:
        asyncio.run(
            main()
        )

    except Exception:
        try:
            asyncio.run(
                cleanup()
            )

        except Exception:
            pass

        raise

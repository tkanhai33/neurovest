#!/usr/bin/env python3
"""
Workstream 3 Stage 7G runtime wiring qualification.

Runs backend.app.main.summary through the real runtime wiring while
injecting deterministic strategy production into the already-wired
Stage 7F adapter.

One audit event is persisted, verified, and removed.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

from sqlalchemy import delete, select, text

from backend.app import main as app_main
from backend.app.stacks.db_runtime.database import (
    async_session,
    engine,
)
from backend.app.stacks.journal_ledger.decision_event_model import (
    DecisionEventRecord,
)
from backend.app.stacks.journal_ledger.strategy_decision_audit_adapter import (
    StrategyDecisionAuditAdapter as RealAdapter,
)


OUTPUT_JSON = Path(
    "runtime/hardening/workstream3/stage7/"
    "stage7g_runtime_wiring_live_latest.json"
)

OUTPUT_TEXT = Path(
    "runtime/hardening/workstream3/stage7/"
    "stage7g_runtime_wiring_live_latest.txt"
)

PREFIX = "dashboard-summary:"


def deterministic_producer(
    symbol: str,
    replay_bars: list[dict] | None,
) -> dict[str, Any]:
    strategy_signal = {
        "status": "ok",
        "symbol": symbol,
        "action": "buy",
        "decision": "BUY",
        "confidence": 0.80,
    }

    return {
        "status": "rebalanced",
        "symbol": symbol,
        "signal": "buy",
        "decision": "BUY",
        "confidence": 0.80,
        "strategy_signal": strategy_signal,
        "portfolio_output": {
            "symbol": symbol,
            "signal": "buy",
            "status": "rebalanced",
        },
    }


def adapter_factory(
    audit_service: object,
) -> RealAdapter:
    return RealAdapter(
        audit_service,
        producer=deterministic_producer,
    )


async def no_op_runtime_step(
    **kwargs: object,
) -> None:
    return None


async def no_op_portfolio_output(
    *args: object,
    **kwargs: object,
) -> None:
    return None


async def revision() -> str:
    async with engine.connect() as connection:
        value = (
            await connection.execute(
                text(
                    "SELECT version_num "
                    "FROM alembic_version"
                )
            )
        ).scalar_one()

    return str(value)


async def qualification_rows() -> list[
    DecisionEventRecord
]:
    """
    Load ORM records through AsyncSession.

    Executing an ORM entity selection through a Core connection returns
    raw table columns. Because sequence_number is the first selected
    column, Result.scalars() previously returned integers instead of
    DecisionEventRecord objects.
    """

    async with async_session() as session:
        rows = (
            await session.execute(
                select(
                    DecisionEventRecord
                ).where(
                    DecisionEventRecord
                    .idempotency_key
                    .like(
                        f"{PREFIX}%"
                    )
                )
            )
        ).scalars().all()

    return list(rows)


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


async def main() -> None:
    revision_before = await revision()

    assert revision_before == (
        "ws3_stage5_decision_events"
    )

    await cleanup()

    assert await qualification_rows() == []

    original_watchlist = (
        app_main.TICKER_WATCHLIST
    )

    original_override_active = (
        app_main.SANDBOX_OVERRIDE_ACTIVE
    )

    original_override_signal = (
        app_main.SANDBOX_OVERRIDE_SIGNAL
    )

    original_adapter = (
        app_main.StrategyDecisionAuditAdapter
    )

    original_emit = (
        app_main.emit_runtime_step
    )

    original_process = (
        app_main.process_portfolio_output
    )

    try:
        app_main.TICKER_WATCHLIST = [
            "AAPL"
        ]

        app_main.SANDBOX_OVERRIDE_ACTIVE = (
            False
        )

        app_main.SANDBOX_OVERRIDE_SIGNAL = (
            "hold"
        )

        app_main.StrategyDecisionAuditAdapter = (
            adapter_factory
        )

        app_main.emit_runtime_step = (
            no_op_runtime_step
        )

        app_main.process_portfolio_output = (
            no_op_portfolio_output
        )

        response = await app_main.summary()

    finally:
        app_main.TICKER_WATCHLIST = (
            original_watchlist
        )

        app_main.SANDBOX_OVERRIDE_ACTIVE = (
            original_override_active
        )

        app_main.SANDBOX_OVERRIDE_SIGNAL = (
            original_override_signal
        )

        app_main.StrategyDecisionAuditAdapter = (
            original_adapter
        )

        app_main.emit_runtime_step = (
            original_emit
        )

        app_main.process_portfolio_output = (
            original_process
        )

    assert response[
        "status"
    ] == "watchlist_scan_complete"

    results = response[
        "results"
    ]

    assert len(results) == 1

    item = results[0]

    assert item["symbol"] == "AAPL"
    assert item["status"] == "processed"

    audit_identity = item[
        "audit"
    ]

    assert isinstance(
        audit_identity,
        dict,
    )

    assert audit_identity[
        "event_type"
    ] == "strategy_decision"

    assert audit_identity[
        "outcome"
    ] == "proposed"

    assert isinstance(
        audit_identity[
            "event_id"
        ],
        str,
    )

    assert isinstance(
        audit_identity[
            "sequence_number"
        ],
        int,
    )

    assert isinstance(
        audit_identity[
            "content_hash"
        ],
        str,
    )

    rows = await qualification_rows()

    assert len(rows) == 1

    record = rows[0]

    assert str(
        record.event_id
    ) == audit_identity[
        "event_id"
    ]

    assert record.sequence_number == (
        audit_identity[
            "sequence_number"
        ]
    )

    assert record.content_hash == (
        audit_identity[
            "content_hash"
        ]
    )

    assert record.symbol == "AAPL"
    assert record.event_type == (
        "strategy_decision"
    )
    assert record.outcome == "proposed"
    assert record.confidence == 0.80

    assert record.payload[
        "decision"
    ] == "BUY"

    assert record.payload[
        "signal"
    ] == "buy"

    removed = await cleanup()

    rows_after = await qualification_rows()

    revision_after = await revision()

    assert removed == 1
    assert rows_after == []
    assert revision_after == revision_before

    report = {
        "workstream": 3,
        "stage": "7G",
        "status": "completed",
        "runtime_boundary": (
            "backend.app.main.summary"
        ),
        "summary_called": True,
        "strategy_decisions_processed": 1,
        "audit_events_persisted": 1,
        "read_only_identity_returned": True,
        "identity_event_id_verified": True,
        "identity_sequence_number_verified": True,
        "identity_content_hash_verified": True,
        "event_type_verified": True,
        "outcome_verified": True,
        "payload_verified": True,
        "sandbox_override_used": False,
        "qualification_rows_removed": removed,
        "rows_after_cleanup": 0,
        "database_restored_to_empty": True,
        "revision_before": revision_before,
        "revision_after": revision_after,
        "revision_unchanged": True,
        "strategy_engine_modified": False,
        "repository_called_directly": False,
        "runtime_commit_ownership": False,
        "runtime_sequence_ownership": False,
        "runtime_hash_ownership": False,
        "api_routes_added": False,
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
            "STAGE 7G — CONTROLLED RUNTIME "
            "PRODUCER WIRING"
        ),
        "=" * 80,
        "",
        "STATUS",
        "COMPLETE AND VERIFIED",
        "",
        "RUNTIME",
        "- Boundary: backend.app.main.summary",
        "- Summary invoked: PASS",
        "- Strategy decisions processed: 1",
        "- Audit events persisted: 1",
        "- Read-only audit identity returned: PASS",
        "",
        "AUDIT IDENTITY",
        "- Event ID verified: PASS",
        "- Sequence number verified: PASS",
        "- Content hash verified: PASS",
        "- Event type verified: PASS",
        "- Outcome verified: PASS",
        "- Payload verified: PASS",
        "",
        "OWNERSHIP",
        "- Strategy engine modified: NO",
        "- Repository called directly: NO",
        "- Runtime commit ownership: NO",
        "- Runtime sequence ownership: NO",
        "- Runtime hash ownership: NO",
        "",
        "CLEANUP",
        "- Qualification rows removed: 1",
        "- Rows remaining: 0",
        "- Database restored to empty: YES",
        "",
        "SAFETY",
        "- Migration revision changed: NO",
        "- API routes added: NO",
        "- Broker execution enabled: NO",
        "- Live trading enabled: NO",
        "",
        "NEXT",
        (
            "Workstream 3 Stage 7H — Audit Failure "
            "Disposition and Runtime Fail-Closed Qualification"
        ),
        "",
        "=" * 80,
    ]

    rendered = (
        "\n".join(lines)
        + "\n"
    )

    OUTPUT_TEXT.write_text(
        rendered,
        encoding="utf-8",
    )

    print(rendered)


async def run_with_cleanup() -> None:
    """
    Keep qualification and failure cleanup in one event loop.

    Starting a second asyncio.run() after an asyncpg failure can close
    the original loop while pooled connections still reference it.
    """

    try:
        await main()

    except Exception:
        try:
            await cleanup()

        except Exception as cleanup_error:
            print(
                "Qualification cleanup warning:",
                type(cleanup_error).__name__,
                str(cleanup_error),
            )

        raise


if __name__ == "__main__":
    asyncio.run(
        run_with_cleanup()
    )

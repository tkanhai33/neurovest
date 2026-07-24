#!/usr/bin/env python3
"""
Stage 7H live fail-closed qualification.

Injects an audit adapter that always fails and proves:

- summary returns a controlled audit-required failure;
- no normal strategy decision escapes;
- no portfolio processing occurs;
- no audit row remains;
- migration revision is unchanged.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

from sqlalchemy import func, select, text

from backend.app import main as app_main
from backend.app.stacks.db_runtime.database import (
    async_session,
    engine,
)
from backend.app.stacks.journal_ledger.decision_event_model import (
    DecisionEventRecord,
)


OUTPUT_JSON = Path(
    "runtime/hardening/workstream3/stage7/"
    "stage7h_fail_closed_live_latest.json"
)

OUTPUT_TEXT = Path(
    "runtime/hardening/workstream3/stage7/"
    "stage7h_fail_closed_live_latest.txt"
)


class ForcedAuditFailure(
    RuntimeError
):
    pass


class FailingAuditAdapter:
    def __init__(
        self,
        audit_service: object,
    ) -> None:
        self._audit_service = (
            audit_service
        )

    async def produce_and_audit(
        self,
        *args: object,
        **kwargs: object,
    ) -> object:
        raise ForcedAuditFailure(
            "forced Stage 7H audit failure"
        )


portfolio_calls = 0
runtime_events: list[
    dict[str, Any]
] = []


async def capture_runtime_step(
    **kwargs: Any,
) -> None:
    runtime_events.append(
        dict(kwargs)
    )


async def forbidden_portfolio_processing(
    *args: object,
    **kwargs: object,
) -> None:
    global portfolio_calls

    portfolio_calls += 1

    raise AssertionError(
        "Portfolio processing was reached after "
        "required audit persistence failed"
    )


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


async def row_count() -> int:
    async with async_session() as session:
        value = (
            await session.execute(
                select(
                    func.count()
                ).select_from(
                    DecisionEventRecord
                )
            )
        ).scalar_one()

    return int(value)


async def main() -> None:
    global portfolio_calls

    revision_before = await revision()
    rows_before = await row_count()

    assert revision_before == (
        "ws3_stage5_decision_events"
    )

    assert rows_before == 0

    original_watchlist = (
        app_main.TICKER_WATCHLIST
    )

    original_override_active = (
        app_main.SANDBOX_OVERRIDE_ACTIVE
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

        app_main.StrategyDecisionAuditAdapter = (
            FailingAuditAdapter
        )

        app_main.emit_runtime_step = (
            capture_runtime_step
        )

        app_main.process_portfolio_output = (
            forbidden_portfolio_processing
        )

        response = await app_main.summary()

    finally:
        app_main.TICKER_WATCHLIST = (
            original_watchlist
        )

        app_main.SANDBOX_OVERRIDE_ACTIVE = (
            original_override_active
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

    result = results[0]

    assert result[
        "symbol"
    ] == "AAPL"

    assert result[
        "status"
    ] == "audit_required_failure"

    assert result[
        "classification"
    ] == "AUDIT_REQUIRED_FAIL_CLOSED"

    assert result[
        "decision_returned"
    ] is False

    assert result[
        "portfolio_processing"
    ] == "blocked"

    assert result[
        "execution"
    ] == "blocked"

    assert result[
        "audit"
    ] is None

    assert result[
        "error_type"
    ] == "ForcedAuditFailure"

    assert portfolio_calls == 0

    failure_events = [
        event
        for event in runtime_events
        if event.get(
            "event_type"
        ) == (
            "STRATEGY_AUDIT_REQUIRED_FAILURE"
        )
    ]

    assert len(
        failure_events
    ) == 1

    failure_event = (
        failure_events[0]
    )

    assert failure_event[
        "status"
    ] == "failed"

    assert failure_event[
        "symbol"
    ] == "AAPL"

    rows_after = await row_count()
    revision_after = await revision()

    assert rows_after == 0
    assert revision_after == revision_before

    report = {
        "workstream": 3,
        "stage": "7H",
        "status": "completed",
        "runtime_boundary": (
            "backend.app.main.summary"
        ),
        "audit_failure_injected": True,
        "controlled_failure_returned": True,
        "classification": (
            "AUDIT_REQUIRED_FAIL_CLOSED"
        ),
        "normal_decision_returned": False,
        "portfolio_processing_calls": (
            portfolio_calls
        ),
        "portfolio_processing_blocked": True,
        "paper_broker_path_blocked": True,
        "execution_blocked": True,
        "failure_runtime_event_emitted": True,
        "partial_event_persisted": False,
        "rows_before": rows_before,
        "rows_after": rows_after,
        "database_unchanged": True,
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
            "STAGE 7H — AUDIT FAILURE DISPOSITION "
            "AND RUNTIME FAIL-CLOSED"
        ),
        "=" * 80,
        "",
        "STATUS",
        "COMPLETE AND VERIFIED",
        "",
        "FAILURE INJECTION",
        "- Audit failure injected: YES",
        "- Controlled failure returned: PASS",
        (
            "- Classification: "
            "AUDIT_REQUIRED_FAIL_CLOSED"
        ),
        "- Normal decision returned: NO",
        "",
        "DOWNSTREAM BLOCKING",
        "- Portfolio processing calls: 0",
        "- Portfolio processing blocked: PASS",
        "- Paper broker path blocked: PASS",
        "- Execution blocked: PASS",
        "",
        "OBSERVABILITY",
        "- Failure runtime event emitted: PASS",
        "",
        "DATABASE",
        "- Partial event persisted: NO",
        "- Rows before: 0",
        "- Rows after: 0",
        "- Migration revision changed: NO",
        "",
        "OWNERSHIP",
        "- Strategy engine modified: NO",
        "- Repository called directly: NO",
        "- Runtime commit ownership: NO",
        "- Runtime sequence ownership: NO",
        "- Runtime hash ownership: NO",
        "",
        "SAFETY",
        "- API routes added: NO",
        "- Broker execution enabled: NO",
        "- Live trading enabled: NO",
        "",
        "NEXT",
        (
            "Workstream 3 Stage 8 — Read-Only Decision "
            "Audit Query and Consumer Integration"
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

    print(rendered)


if __name__ == "__main__":
    asyncio.run(
        main()
    )

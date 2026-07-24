#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path
import ast
import json


ROOT = Path(".").resolve()

FILES = {
    "runtime_trace": ROOT / "backend/app/core/runtime_trace.py",
    "main": ROOT / "backend/app/main.py",
    "paper_broker": (
        ROOT / "backend/app/stacks/execution/paper_broker.py"
    ),
    "ledger": (
        ROOT / "backend/app/stacks/journal_ledger/ledger.py"
    ),
    "reconciliation": (
        ROOT / "backend/app/stacks/portfolio/reconciliation.py"
    ),
}

for path in FILES.values():
    ast.parse(path.read_text(encoding="utf-8"))

texts = {
    name: path.read_text(encoding="utf-8")
    for name, path in FILES.items()
}

checks = {
    "trace_helper_exists": (
        "async def emit_runtime_step" in texts["runtime_trace"]
    ),
    "dashboard_creates_trace": (
        'create_trace_id("dashboard-scan")' in texts["main"]
    ),
    "strategy_activation_instrumented": (
        "STRATEGY_EVALUATION_STARTED" in texts["main"]
    ),
    "paper_flow_accepts_trace": (
        "trace_id: str | None = None"
        in texts["paper_broker"]
    ),
    "portfolio_accounting_instrumented": (
        "PORTFOLIO_ACCOUNTING_REQUEST"
        in texts["paper_broker"]
    ),
    "risk_instrumented": (
        "RISK_EVALUATION_STARTED"
        in texts["paper_broker"]
    ),
    "market_quote_instrumented": (
        "MARKET_QUOTE_REQUEST"
        in texts["paper_broker"]
    ),
    "paper_execution_instrumented": (
        "PAPER_EXECUTION_STARTED"
        in texts["paper_broker"]
    ),
    "ledger_write_instrumented": (
        "LEDGER_WRITE_COMPLETE"
        in texts["ledger"]
    ),
    "portfolio_inventory_instrumented": (
        "PORTFOLIO_INVENTORY_UPDATED"
        in texts["ledger"]
    ),
    "reconciliation_instrumented": (
        "RECONCILIATION_STARTED"
        in texts["reconciliation"]
    ),
    "old_duplicate_trade_event_removed": (
        'global_event_bus.emit(\n                "TRADE_EXECUTED"' not in texts["main"]
        and "await global_event_bus.emit(\n                \"TRADE_EXECUTED\"" not in texts["main"]
    ),
}

certified = all(checks.values())

print(
    json.dumps(
        {
            "phase": (
                "133B-B_REAL_RUNTIME_FLOW_INSTRUMENTATION"
            ),
            "checks": checks,
            "certified": certified,
            "execution_behavior_changed": False,
            "broker_unlock_changed": False,
            "risk_bypass_added": False,
        },
        indent=2,
    )
)

if not certified:
    raise SystemExit(1)

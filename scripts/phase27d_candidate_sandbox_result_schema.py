#!/usr/bin/env python3
import json
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
SANDBOX = ROOT / "runtime/strategy_candidate_sandbox"
OUT = SANDBOX / "candidate_sandbox_result_schema_v1.json"
EXAMPLE = SANDBOX / "candidate_sandbox_result_example_latest.json"

SANDBOX.mkdir(parents=True, exist_ok=True)

schema = {
    "schema_id": "candidate_sandbox_result_v1",
    "generated_at": datetime.now(UTC).isoformat(),
    "description": "Result contract for future strategy candidate sandbox tests. Schema only; no backtest execution.",
    "required_fields": [
        "candidate_id",
        "symbol",
        "simulation_status",
        "trade_count",
        "win_rate",
        "profit_factor",
        "max_drawdown",
        "average_return",
        "confidence_score",
        "promotion_recommendation",
        "approval_required",
        "live_execution_allowed",
        "broker_execution_allowed",
        "writes_to_strategy_registry",
    ],
    "fields": {
        "candidate_id": "string",
        "symbol": "string|null",
        "simulation_status": "pending|completed|failed",
        "trade_count": "integer",
        "win_rate": "number|null",
        "profit_factor": "number|null",
        "max_drawdown": "number|null",
        "average_return": "number|null",
        "confidence_score": "number|null",
        "promotion_recommendation": "reject|review|promote_candidate|null",
        "approval_required": "boolean",
        "live_execution_allowed": "boolean",
        "broker_execution_allowed": "boolean",
        "writes_to_strategy_registry": "boolean",
    },
    "hard_locks": {
        "live_execution_allowed": False,
        "broker_execution_allowed": False,
        "writes_to_strategy_registry": False,
        "approval_required": True,
    },
}

example = {
    "candidate_id": "candidate_example",
    "symbol": "RY.TO",
    "simulation_status": "pending",
    "trade_count": 0,
    "win_rate": None,
    "profit_factor": None,
    "max_drawdown": None,
    "average_return": None,
    "confidence_score": None,
    "promotion_recommendation": None,
    "approval_required": True,
    "live_execution_allowed": False,
    "broker_execution_allowed": False,
    "writes_to_strategy_registry": False,
    "notes": [
        "Example only.",
        "No sandbox execution performed.",
        "No live trading path enabled.",
    ],
}

OUT.write_text(json.dumps(schema, indent=2))
EXAMPLE.write_text(json.dumps(example, indent=2))

print(json.dumps({
    "status": "ok",
    "schema": str(OUT),
    "example": str(EXAMPLE),
}, indent=2))

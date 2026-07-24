#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()

OUT_DIR = ROOT / "runtime/replay_runtime_architecture/strategy_tuning"
OUT_DIR.mkdir(parents=True, exist_ok=True)

TARGET = ROOT / "backend/app/stacks/strategy_candidate_sandbox/symbol_weights.py"

PHASE = "130I_UNIVERSE_WEIGHTING_PLAN"

SOURCE = '''"""
130I_UNIVERSE_WEIGHTING_PLAN

Replay/training symbol weights.

Does not execute trades.
Does not touch broker.
Does not change live portfolio.
"""

from __future__ import annotations

SYMBOL_WEIGHTS = {
    "CNR.TO": 4.0,
    "ENB.TO": 1.5,
    "VUN.TO": 1.0,
    "VFV.TO": 1.0,
}

def get_symbol_weight(symbol: str) -> float:
    return float(SYMBOL_WEIGHTS.get(symbol.upper(), 0.0))

def weighted_symbols() -> dict[str, float]:
    return dict(SYMBOL_WEIGHTS)

def preferred_weighted_order() -> list[str]:
    return [
        symbol
        for symbol, _weight in sorted(
            SYMBOL_WEIGHTS.items(),
            key=lambda item: item[1],
            reverse=True,
        )
    ]
'''

TARGET.write_text(SOURCE, encoding="utf-8")

result = {
    "phase": PHASE,
    "created_at": datetime.now().astimezone().isoformat(),
    "target": str(TARGET),
    "weights": {
        "CNR.TO": 4.0,
        "ENB.TO": 1.5,
        "VUN.TO": 1.0,
        "VFV.TO": 1.0,
    },
    "policy": {
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
        "portfolio_mutation_enabled": False,
    },
    "recommended_next_phase": "130J_WEIGHTED_REPLAY_RUNNER",
    "certified": TARGET.exists(),
}

OUT_JSON = OUT_DIR / "130I_universe_weighting_plan_latest.json"
OUT_TXT = OUT_DIR / "130I_universe_weighting_plan_latest.txt"

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

OUT_TXT.write_text(
"""130I_UNIVERSE_WEIGHTING_PLAN

certified: True

WEIGHTS
CNR.TO  4.0
ENB.TO  1.5
VUN.TO  1.0
VFV.TO  1.0

No broker.
No live execution.
No portfolio mutation.

Next:
130J_WEIGHTED_REPLAY_RUNNER
""",
encoding="utf-8",
)

print(OUT_TXT.read_text())

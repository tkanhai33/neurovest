#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime, UTC
import json
import py_compile

ROOT = Path(".").resolve()

OUT_DIR = ROOT / "runtime/replay_runtime_architecture/strategy_tuning"
OUT_DIR.mkdir(parents=True, exist_ok=True)

TARGET = ROOT / "backend/app/stacks/strategy_candidate_sandbox/symbol_universe.py"

PHASE = "130G_SYMBOL_UNIVERSE_LOCK"

SOURCE = '''"""
130G_SYMBOL_UNIVERSE_LOCK

Replay-only symbol universe classification.

Does NOT block symbols globally.
Provides recommendations for replay/training.
"""

from __future__ import annotations

TRAIN_MORE = {
    "CNR.TO",
}

WATCHLIST = {
    "ENB.TO",
    "VFV.TO",
    "VUN.TO",
}

WEAK = {
    "BAM.TO",
    "RY.TO",
    "TD.TO",
}

EXCLUDED = {
    "SHOP.TO",
    "ATZ.TO",
    "BNS.TO",
}


def classify_symbol(symbol: str) -> str:

    symbol = symbol.upper()

    if symbol in TRAIN_MORE:
        return "TRAIN_MORE"

    if symbol in WATCHLIST:
        return "WATCHLIST"

    if symbol in WEAK:
        return "WEAK"

    if symbol in EXCLUDED:
        return "EXCLUDED"

    return "UNKNOWN"


def replay_allowed(symbol: str) -> bool:

    return classify_symbol(symbol) != "EXCLUDED"


def preferred_training_symbols():

    return sorted(TRAIN_MORE | WATCHLIST)


def excluded_symbols():

    return sorted(EXCLUDED)


def universe_summary():

    return {

        "train_more": sorted(TRAIN_MORE),

        "watchlist": sorted(WATCHLIST),

        "weak": sorted(WEAK),

        "excluded": sorted(EXCLUDED),

    }
'''

TARGET.write_text(SOURCE, encoding="utf-8")

compile_ok = False

try:
    py_compile.compile(str(TARGET), doraise=True)
    compile_ok = True
except Exception as exc:
    compile_error = str(exc)
else:
    compile_error = None

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "target": str(TARGET),
    "compile_ok": compile_ok,
    "compile_error": compile_error,
    "train_more": ["CNR.TO"],
    "watchlist": ["ENB.TO", "VFV.TO", "VUN.TO"],
    "weak": ["BAM.TO", "RY.TO", "TD.TO"],
    "excluded": ["SHOP.TO", "ATZ.TO", "BNS.TO"],
    "certified": compile_ok,
    "recommended_next_phase": "130H_REPLAY_UNIVERSE_FILTER",
}

OUT_JSON = OUT_DIR / "130G_symbol_universe_lock_latest.json"
OUT_TXT = OUT_DIR / "130G_symbol_universe_lock_latest.txt"

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

OUT_TXT.write_text(
f"""130G_SYMBOL_UNIVERSE_LOCK

certified: {compile_ok}

TRAIN_MORE
- CNR.TO

WATCHLIST
- ENB.TO
- VFV.TO
- VUN.TO

WEAK
- BAM.TO
- RY.TO
- TD.TO

EXCLUDED
- SHOP.TO
- ATZ.TO
- BNS.TO

Next:
130H_REPLAY_UNIVERSE_FILTER
""",
encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": compile_ok,
    "compile_ok": compile_ok,
    "target": str(TARGET),
    "recommended_next_phase": "130H_REPLAY_UNIVERSE_FILTER",
}, indent=2))

print()
print(OUT_TXT.read_text())

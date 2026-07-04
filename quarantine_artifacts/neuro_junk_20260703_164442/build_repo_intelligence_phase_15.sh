#!/bin/bash
set -e

echo "🧠 Phase 15 — Active Signal Generation Layer"

mkdir -p backend/app/spine/L4_runtime/signals
mkdir -p backend/app/spine/L5_api
mkdir -p backend/app/spine/L7_tests


# =========================================================
# FILE 1 — SIGNAL GENERATOR
# =========================================================
cat > backend/app/spine/L4_runtime/signals/signal_generator.py <<'PY'
from __future__ import annotations

from spine.L4_runtime.stack_gap_analyzer import analyze_stack_gaps
from spine.L4_runtime.dependency_graph_engine import build_dependency_graph

def generate_signals(limit: int = 1000) -> list[dict]:
    gaps = analyze_stack_gaps(limit=limit)
    deps = build_dependency_graph(limit=limit)

    signals = []

    # 1. Missing components → proposals
    for stack, items in gaps["gaps"].items():
        for item in items:
            signals.append({
                "stack": stack,
                "target": item,
                "type": "MISSING_COMPONENT_SIGNAL"
            })

    # 2. Broken dependency signals
    for stack, missing in deps["missing_links"].items():
        for dep in missing:
            signals.append({
                "stack": stack,
                "target": dep,
                "type": "DEPENDENCY_BREAK_SIGNAL"
            })

    # 3. Orphan detection signal
    for orphan in deps.get("missing_links", {}):
        signals.append({
            "stack": orphan,
            "target": None,
            "type": "ORPHAN_SIGNAL"
        })

    return signals
PY


# =========================================================
# FILE 2 — SIGNAL → PROPOSAL TRANSLATOR
# =========================================================
cat > backend/app/spine/L4_runtime/signals/signal_to_proposal.py <<'PY'
from __future__ import annotations

from spine.L4_runtime.signals.signal_generator import generate_signals

def translate_signals(limit: int = 1000) -> dict:
    signals = generate_signals(limit=limit)

    proposals = []

    for s in signals:
        proposals.append({
            "stack": s["stack"],
            "target": s["target"],
            "source": s["type"]
        })

    return {
        "signal_count": len(signals),
        "proposals": proposals
    }
PY


# =========================================================
# FILE 3 — SIGNAL-ACTIVATED CLI
# =========================================================
cat > backend/app/spine/L5_api/repo_intelligence_v15_cli.py <<'PY'
from __future__ import annotations

import json

from spine.L4_runtime.signals.signal_to_proposal import translate_signals
from spine.L4_runtime.governance.approval_state_machine import run_approval_flow
from spine.L4_runtime.memory.state_event_store import append_event
from spine.L4_runtime.memory.state_replay_engine import replay_state

def run(limit: int = 1000):
    bundle = translate_signals(limit=limit)

    results = []

    for p in bundle["proposals"]:
        decision = run_approval_flow(p)

        if decision["state"] == "APPROVED":
            append_event({
                "stack": p["stack"],
                "value": f"updated:{p['target']}",
                "type": "SIGNAL_EXECUTION"
            })

        results.append(decision)

    report = {
        "signal_count": bundle["signal_count"],
        "executed": sum(1 for r in results if r["state"] == "APPROVED"),
        "replay": replay_state()
    }

    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    run()
PY


# =========================================================
# FILE 4 — TESTS
# =========================================================
cat > backend/app/spine/L7_tests/test_phase15_signals.py <<'PY'
from spine.L4_runtime.signals.signal_generator import generate_signals

def test_signal_generation():
    s = generate_signals(limit=200)
    assert isinstance(s, list)
PY


# =========================================================
# EXECUTION
# =========================================================

echo "🧠 Running Phase 15 CLI..."
PYTHONPATH=backend/app python3 backend/app/spine/L5_api/repo_intelligence_v15_cli.py

echo "🧪 Running Phase 15 tests..."
PYTHONPATH=backend/app pytest -q backend/app/spine/L7_tests/test_phase15_signals.py

echo "✅ Phase 15 Complete"

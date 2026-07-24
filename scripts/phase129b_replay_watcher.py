#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime, UTC
import json
import time

ROOT = Path(".").resolve()

RUN_ROOT = ROOT / "runtime" / "replay_runtime_architecture" / "eight_hour_replay_training"

runs = sorted(
    [p for p in RUN_ROOT.iterdir() if p.is_dir()],
    key=lambda p: p.stat().st_mtime
)

assert runs, "No replay run found."

RUN = runs[-1]

manifest = json.loads((RUN / "manifest.json").read_text())

print("=" * 80)
print("NEURO REPLAY WATCHER")
print("=" * 80)
print("Run :", manifest["run_id"])
print("Mode:", manifest["mode"])
print()

decision_file = RUN / "decision_ledger.jsonl"
cycle_file = RUN / "cycle_ledger.jsonl"

last_decisions = 0
last_cycles = 0

while True:

    try:
        decisions = decision_file.read_text().splitlines()
    except Exception:
        decisions = []

    try:
        cycles = cycle_file.read_text().splitlines()
    except Exception:
        cycles = []

    if len(decisions) != last_decisions or len(cycles) != last_cycles:

        last_decisions = len(decisions)
        last_cycles = len(cycles)

        print(
            f"[{datetime.now(UTC).isoformat()}] "
            f"cycles={last_cycles} "
            f"decisions={last_decisions}"
        )

    summary = {
        "timestamp": datetime.now(UTC).isoformat(),
        "cycles_completed": last_cycles,
        "decisions_logged": last_decisions,
    }

    (RUN / "watcher_status.json").write_text(
        json.dumps(summary, indent=2)
    )

    time.sleep(5)

#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime, UTC
import importlib.util
import json
from collections import Counter

ROOT = Path(".").resolve()

PHASE = "129G_MULTI_SYMBOL_REPLAY_RUNNER"

FIXTURE_DIR = ROOT / "runtime/replay_runtime_architecture/historical_fixture_store/TRAINING_RUN_0001"

RUN_ROOT = ROOT / "runtime/replay_runtime_architecture/eight_hour_replay_training"

RUN_ID = "MULTI_SYMBOL_REPLAY_" + datetime.now(UTC).strftime("%Y%m%d_%H%M%S")

RUN = RUN_ROOT / RUN_ID
RUN.mkdir(parents=True, exist_ok=True)

manifest = {
    "phase": PHASE,
    "run_id": RUN_ID,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "REPLAY_ONLY_MULTI_SYMBOL",
    "database_writes_allowed": False,
    "broker_execution_enabled": False,
    "live_execution_enabled": False,
}

(RUN / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

(RUN / "decision_ledger.jsonl").write_text("", encoding="utf-8")
(RUN / "cycle_ledger.jsonl").write_text("", encoding="utf-8")
(RUN / "equity_curve.csv").write_text(
    "cycle,equity,drawdown,rolling_reward,rolling_win_rate,rolling_sharpe,rolling_sortino\n",
    encoding="utf-8",
)
(RUN / "drawdown_curve.csv").write_text("cycle,drawdown\n", encoding="utf-8")

for f in [
    "strategy_statistics.json",
    "indicator_statistics.json",
    "symbol_profiles.json",
    "training_health.json",
    "replay_health.json",
    "replay_summary.json",
    "knowledge_growth.json",
    "performance_metrics.json",
    "confidence_calibration.json",
]:
    (RUN / f).write_text("{}", encoding="utf-8")

spec = importlib.util.spec_from_file_location(
    "engine",
    ROOT / "backend/app/stacks/strategy_candidate_sandbox/L4_runtime_orchestration/replay_execution_engine.py",
)

module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

from backend.app.stacks.strategy_candidate_sandbox.symbol_universe import (
    replay_allowed,
    preferred_training_symbols,
)

preferred = set(preferred_training_symbols())

csvs = [
    p for p in sorted(FIXTURE_DIR.glob("*.csv"))
    if p.stem.replace("_TO", ".TO") in preferred
    and replay_allowed(p.stem.replace("_TO", ".TO"))
]

overall = {
    "phase": PHASE,
    "run_id": RUN_ID,
    "started_at": datetime.now(UTC).isoformat(),
    "symbols": [],
    "total_rows_processed": 0,
    "total_decisions": 0,
    "total_errors": 0,
    "decision_counts": {},
}

decision_counts = Counter()

for csv_file in csvs:
    symbol = csv_file.stem

    print(f"Running {symbol} -> {csv_file}")

    engine = module.ReplayExecutionEngine(RUN)
    summary = engine.execute(csv_file)

    symbol_report = {
        "symbol": symbol,
        "csv": str(csv_file.relative_to(ROOT)),
        "summary": summary,
    }

    overall["symbols"].append(symbol_report)
    overall["total_rows_processed"] += int(summary.get("rows_processed", 0))
    overall["total_decisions"] += int(summary.get("decisions", 0))
    overall["total_errors"] += int(summary.get("errors", 0))

ledger = RUN / "decision_ledger.jsonl"

if ledger.exists():
    for line in ledger.open(encoding="utf-8"):
        if line.strip():
            try:
                decision_counts[json.loads(line)["decision"]] += 1
            except Exception:
                pass

overall["decision_counts"] = dict(decision_counts)
overall["completed_at"] = datetime.now(UTC).isoformat()
overall["certified"] = overall["total_rows_processed"] > 0 and overall["total_errors"] == 0

(RUN / "multi_symbol_replay_summary.json").write_text(
    json.dumps(overall, indent=2),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "run_id": RUN_ID,
    "run_directory": str(RUN),
    "symbols_processed": len(csvs),
    "total_rows_processed": overall["total_rows_processed"],
    "total_decisions": overall["total_decisions"],
    "total_errors": overall["total_errors"],
    "decision_counts": overall["decision_counts"],
    "certified": overall["certified"],
}, indent=2))

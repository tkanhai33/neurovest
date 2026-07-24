#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
RUN_ROOT = ROOT / "runtime/replay_runtime_architecture/eight_hour_replay_training"
OUT_DIR = ROOT / "runtime/replay_runtime_architecture/strategy_tuning"
OUT_DIR.mkdir(parents=True, exist_ok=True)

PHASE = "130C_REPORT_COMPARE_AND_STRATEGY_TUNING"

runs = sorted([p for p in RUN_ROOT.glob("MULTI_SYMBOL_REPLAY_*") if p.is_dir()])
assert len(runs) >= 2, "Need at least two multi-symbol runs."

old_run = runs[-2]
new_run = runs[-1]

def load_report(run: Path):
    p = run / "129H_multi_symbol_replay_report.json"
    assert p.exists(), f"Missing report: {p}"
    return json.loads(p.read_text(encoding="utf-8"))

old = load_report(old_run)
new = load_report(new_run)

comparison = []

old_by_symbol = {s["symbol"]: s for s in old["symbols"]}
new_by_symbol = {s["symbol"]: s for s in new["symbols"]}

for symbol in sorted(set(old_by_symbol) | set(new_by_symbol)):
    o = old_by_symbol.get(symbol, {})
    n = new_by_symbol.get(symbol, {})

    old_reward = float(o.get("reward_total", 0.0))
    new_reward = float(n.get("reward_total", 0.0))

    comparison.append({
        "symbol": symbol,
        "old_reward_total": old_reward,
        "new_reward_total": new_reward,
        "delta": new_reward - old_reward,
        "old_decisions": o.get("decisions", {}),
        "new_decisions": n.get("decisions", {}),
    })

comparison.sort(key=lambda x: x["delta"], reverse=True)

old_total = sum(float(s["reward_total"]) for s in old["symbols"])
new_total = sum(float(s["reward_total"]) for s in new["symbols"])

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "old_run": str(old_run),
    "new_run": str(new_run),
    "old_total_reward": old_total,
    "new_total_reward": new_total,
    "delta_total_reward": new_total - old_total,
    "comparison": comparison,
    "recommendation": {
        "keep_multi_indicator": new_total > old_total,
        "reason": "new_total_reward greater than old_total_reward" if new_total > old_total else "multi-indicator version underperformed RSI-only baseline",
        "next_action": "revert_or_tune_multi_indicator_thresholds",
    },
    "certified": True,
}

out_json = OUT_DIR / "130C_report_compare_and_strategy_tuning_latest.json"
out_txt = OUT_DIR / "130C_report_compare_and_strategy_tuning_latest.txt"

out_json.write_text(json.dumps(result, indent=2), encoding="utf-8")

lines = [
    PHASE,
    "",
    f"certified: {result['certified']}",
    f"old_run: {old_run.name}",
    f"new_run: {new_run.name}",
    "",
    f"old_total_reward: {old_total:.6f}",
    f"new_total_reward: {new_total:.6f}",
    f"delta_total_reward: {new_total - old_total:.6f}",
    "",
    f"keep_multi_indicator: {result['recommendation']['keep_multi_indicator']}",
    f"reason: {result['recommendation']['reason']}",
    "",
    "SYMBOL DELTAS",
]

for row in comparison:
    lines.append(
        f"{row['symbol']:<10} "
        f"old={row['old_reward_total']:.6f} "
        f"new={row['new_reward_total']:.6f} "
        f"delta={row['delta']:.6f}"
    )

out_txt.write_text("\n".join(lines), encoding="utf-8")

print(json.dumps({
    "phase": PHASE,
    "certified": True,
    "old_run": old_run.name,
    "new_run": new_run.name,
    "old_total_reward": old_total,
    "new_total_reward": new_total,
    "delta_total_reward": new_total - old_total,
    "keep_multi_indicator": result["recommendation"]["keep_multi_indicator"],
    "out_json": str(out_json),
    "out_txt": str(out_txt),
}, indent=2))

print()
print(out_txt.read_text())

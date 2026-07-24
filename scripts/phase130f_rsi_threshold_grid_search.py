#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime, UTC
import csv
import json
import numpy as np
from collections import Counter, defaultdict

ROOT = Path(".").resolve()
FIXTURE_DIR = ROOT / "runtime/replay_runtime_architecture/historical_fixture_store/TRAINING_RUN_0001"
OUT_DIR = ROOT / "runtime/replay_runtime_architecture/strategy_tuning/rsi_grid_search"
OUT_DIR.mkdir(parents=True, exist_ok=True)

PHASE = "130F_RSI_THRESHOLD_GRID_SEARCH"

def read_rows(path: Path):
    with path.open(newline="", encoding="utf-8") as fp:
        return list(csv.DictReader(fp))

def rsi(closes, period=14):
    if len(closes) < period + 1:
        return None
    window = closes[-(period + 1):]
    diffs = np.diff(window)
    gains = np.where(diffs > 0, diffs, 0.0)
    losses = np.where(diffs < 0, -diffs, 0.0)
    avg_gain = float(np.mean(gains))
    avg_loss = float(np.mean(losses))
    if avg_loss == 0:
        return 100.0
    if avg_gain == 0:
        return 0.0
    rs = avg_gain / avg_loss
    return float(100.0 - (100.0 / (1.0 + rs)))

def reward(decision, cur, nxt):
    if cur <= 0:
        return 0.0
    ret = (nxt / cur) - 1.0
    if decision == "BUY":
        return ret
    if decision == "SELL":
        return -ret
    return -abs(ret) * 0.1

results = []

buy_thresholds = [25, 30, 35, 40, 45]
sell_thresholds = [55, 60, 65, 70, 75]

csvs = sorted(FIXTURE_DIR.glob("*.csv"))

for buy_t in buy_thresholds:
    for sell_t in sell_thresholds:
        if buy_t >= sell_t:
            continue

        total_reward = 0.0
        total_rows = 0
        decision_counts = Counter()
        symbol_rewards = defaultdict(float)

        for csv_file in csvs:
            rows = read_rows(csv_file)
            closes = [float(r.get("close") or r.get("Close") or 0.0) for r in rows]

            for i in range(1, len(rows) - 1):
                hist = closes[max(0, i - 50):i + 1]
                cur = closes[i]
                nxt = closes[i + 1]
                value = rsi(hist)

                if value is None:
                    decision = "HOLD"
                elif value <= buy_t:
                    decision = "BUY"
                elif value >= sell_t:
                    decision = "SELL"
                else:
                    decision = "HOLD"

                rw = reward(decision, cur, nxt)

                total_reward += rw
                symbol_rewards[csv_file.stem.replace("_TO", ".TO")] += rw
                decision_counts[decision] += 1
                total_rows += 1

        results.append({
            "buy_threshold": buy_t,
            "sell_threshold": sell_t,
            "total_reward": total_reward,
            "rows": total_rows,
            "avg_reward": total_reward / max(1, total_rows),
            "decision_counts": dict(decision_counts),
            "symbol_rewards": dict(symbol_rewards),
        })

results.sort(key=lambda x: x["total_reward"], reverse=True)

report = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "grid_size": len(results),
    "best": results[0],
    "top_10": results[:10],
    "all_results": results,
    "certified": bool(results),
}

OUT_JSON = OUT_DIR / "130F_rsi_threshold_grid_search_latest.json"
OUT_TXT = OUT_DIR / "130F_rsi_threshold_grid_search_latest.txt"

OUT_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")

lines = [
    PHASE,
    "",
    f"certified: {report['certified']}",
    f"grid_size: {report['grid_size']}",
    "",
    "TOP 10",
]

for r in results[:10]:
    lines.append(
        f"BUY<={r['buy_threshold']:<2} SELL>={r['sell_threshold']:<2} "
        f"reward={r['total_reward']:.6f} "
        f"avg={r['avg_reward']:.8f} "
        f"decisions={r['decision_counts']}"
    )

lines.append("")
lines.append("BEST SYMBOL REWARDS")
for symbol, value in sorted(results[0]["symbol_rewards"].items(), key=lambda x: x[1], reverse=True):
    lines.append(f"{symbol:<10} {value:.6f}")

OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

print(OUT_TXT.read_text())

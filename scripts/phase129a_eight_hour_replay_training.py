#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime, UTC
import json
import uuid

ROOT = Path(".").resolve()

ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "training_observability_certification/128C_training_observability_certification_latest.json"

OUT_DIR = ARCH / "eight_hour_replay_training"
OUT_DIR.mkdir(parents=True, exist_ok=True)

PHASE="129A_EIGHT_HOUR_REPLAY_TRAINING"

def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

source=read_json(SOURCE)

assert source.get("certified") is True

RUN_ID=f"REPLAY_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

RUN=OUT_DIR/RUN_ID
RUN.mkdir(parents=True,exist_ok=True)

(RUN/"decision_ledger.jsonl").touch()
(RUN/"cycle_ledger.jsonl").touch()
(RUN/"equity_curve.csv").write_text(
"cycle,equity,drawdown,rolling_reward,rolling_win_rate,rolling_sharpe,rolling_sortino\n"
)

(RUN/"drawdown_curve.csv").write_text(
"cycle,drawdown\n"
)

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
    (RUN/f).write_text("{}")

manifest={

"phase":PHASE,
"created_at":datetime.now(UTC).isoformat(),

"run_id":RUN_ID,

"mode":"REPLAY_ONLY",

"duration_hours":8,

"telemetry":{

"decision_ledger":str(RUN/"decision_ledger.jsonl"),
"cycle_ledger":str(RUN/"cycle_ledger.jsonl"),
"equity_curve":str(RUN/"equity_curve.csv"),
"drawdown_curve":str(RUN/"drawdown_curve.csv"),
"strategy_statistics":str(RUN/"strategy_statistics.json"),
"indicator_statistics":str(RUN/"indicator_statistics.json"),
"symbol_profiles":str(RUN/"symbol_profiles.json"),
"training_health":str(RUN/"training_health.json"),
"replay_health":str(RUN/"replay_health.json"),
"replay_summary":str(RUN/"replay_summary.json"),
"knowledge_growth":str(RUN/"knowledge_growth.json"),
"performance_metrics":str(RUN/"performance_metrics.json"),
"confidence_calibration":str(RUN/"confidence_calibration.json"),

},

"database_writes_allowed":False,
"broker_execution_enabled":False,
"live_execution_enabled":False,

"recommended_next_phase":"129B_REPLAY_WATCHER",

"certified":True,
}

(RUN/"manifest.json").write_text(json.dumps(manifest,indent=2))

print(json.dumps({
"phase":PHASE,
"certified":True,
"run_id":RUN_ID,
"run_directory":str(RUN),
"recommended_next_phase":"129B_REPLAY_WATCHER",
},indent=2))

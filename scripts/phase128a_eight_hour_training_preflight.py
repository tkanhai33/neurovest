#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json
import importlib.util

ROOT = Path(".").resolve()

ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "market_regime_certification/127C_market_regime_certification_latest.json"

OUT_DIR = ARCH / "eight_hour_training_preflight"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "128A_eight_hour_training_preflight_latest.json"
OUT_TXT  = OUT_DIR / "128A_eight_hour_training_preflight_latest.txt"

PHASE="128A_EIGHT_HOUR_TRAINING_PRE_FLIGHT"

def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

source=read_json(SOURCE)

required_files=[

ROOT/"backend/app/stacks/strategy_candidate_sandbox/learning_feature_extractor.py",
ROOT/"backend/app/stacks/strategy_candidate_sandbox/learning_reward_scorer.py",
ROOT/"backend/app/stacks/strategy_candidate_sandbox/learning_artifact_contract.py",
ROOT/"backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/learning_artifact_pipeline.py",
ROOT/"backend/app/stacks/strategy_candidate_sandbox/strategy_knowledge_object.py",
ROOT/"backend/app/stacks/strategy_candidate_sandbox/indicator_knowledge_graph.py",
ROOT/"backend/app/stacks/strategy_candidate_sandbox/symbol_intelligence_profile.py",
ROOT/"backend/app/stacks/strategy_candidate_sandbox/market_regime_library.py",
ROOT/"backend/app/stacks/strategy_candidate_sandbox/market_regime_classifier.py",

]

checks={}

for f in required_files:
    checks[str(f.relative_to(ROOT))]=f.exists()

training_policy={

    "database_writes_allowed":False,
    "strategy_db_write_allowed":False,
    "promotion_enabled":False,
    "broker_execution_enabled":False,
    "live_execution_enabled":False,

    "training_mode":"REPLAY_ONLY",
    "paper_trading_allowed":True,
    "historical_data_allowed":True,
}

summary={

    "phase":PHASE,
    "created_at":datetime.now(UTC).isoformat(),

    "previous_phase_certified":
        source.get("certified") is True,

    "required_files":checks,

    "training_policy":training_policy,

    "training_ready":
        (
            source.get("certified") is True
            and
            all(checks.values())
        ),

    "recommended_next_phase":
        "128B_EIGHT_HOUR_REPLAY_TRAINING",

    "certified":
        (
            source.get("certified") is True
            and
            all(checks.values())
        ),
}

OUT_JSON.write_text(
    json.dumps(summary,indent=2),
    encoding="utf-8",
)

lines=[]

lines.append(PHASE)
lines.append("")
lines.append(f"certified: {summary['certified']}")
lines.append(f"training_ready: {summary['training_ready']}")
lines.append("")

lines.append("Verified Components:")

for k,v in checks.items():
    lines.append(f"[{'OK' if v else 'FAIL'}] {k}")

lines.append("")
lines.append("Training Mode : REPLAY_ONLY")
lines.append("Historical Data : ENABLED")
lines.append("Paper Trading : ENABLED")
lines.append("Broker : DISABLED")
lines.append("Live Trading : DISABLED")
lines.append("Database Writes : DISABLED")
lines.append("")
lines.append("Next:")
lines.append(summary["recommended_next_phase"])

OUT_TXT.write_text(
    "\n".join(lines),
    encoding="utf-8",
)

print(json.dumps({

    "phase":PHASE,
    "certified":summary["certified"],
    "training_ready":summary["training_ready"],
    "recommended_next_phase":
        summary["recommended_next_phase"],
    "out_json":str(OUT_JSON),
    "out_txt":str(OUT_TXT),

},indent=2))

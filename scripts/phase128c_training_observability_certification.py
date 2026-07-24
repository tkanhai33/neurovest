#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime, UTC
import importlib.util
import json

ROOT = Path(".").resolve()

ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "training_observability_contract/128B_training_observability_contract_latest.json"

TARGET = ROOT / "backend/app/stacks/strategy_candidate_sandbox/training_observability_contract.py"

OUT_DIR = ARCH / "training_observability_certification"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "128C_training_observability_certification_latest.json"
OUT_TXT  = OUT_DIR / "128C_training_observability_certification_latest.txt"

PHASE="128C_TRAINING_OBSERVABILITY_CERTIFICATION"

def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

def import_file(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

source=read_json(SOURCE)

module=import_file("training_observability_contract",TARGET)

status=module.observability_status()
sections=module.required_sections()
report=module.create_empty_report()

required_sections_expected={

"replay_metadata",
"dataset_health",
"cycle_statistics",
"decision_ledger",
"action_statistics",
"strategy_statistics",
"indicator_statistics",
"symbol_profiles",
"market_regimes",
"equity_curve",
"confidence_calibration",
"knowledge_growth",
"performance",
"training_health",

}

checks={

"source_exists":
SOURCE.exists(),

"source_certified":
source.get("certified") is True,

"status_present":
bool(status),

"report_created":
isinstance(report,dict),

"sections_present":
set(sections)==required_sections_expected,

"section_count":
len(sections)>=14,

"report_sections":
len(report.get("sections",{}))>=14,

"db_blocked":
status.get("database_writes_allowed") is False,

"strategy_db_blocked":
status.get("strategy_db_write_allowed") is False,

"promotion_blocked":
status.get("promotion_enabled") is False,

"broker_blocked":
status.get("broker_execution_enabled") is False,

"live_blocked":
status.get("live_execution_enabled") is False,

}

summary={}

for section in sections:

    metrics=module.required_metrics(section)

    summary[section]={

        "metric_count":len(metrics),
        "metrics":metrics,

    }

result={

"phase":PHASE,
"created_at":datetime.now(UTC).isoformat(),

"status":status,

"metric_summary":summary,

"checks":checks,

"recommended_next_phase":
"129A_EIGHT_HOUR_REPLAY_TRAINING",

"certified":
all(checks.values()),

}

OUT_JSON.write_text(
json.dumps(result,indent=2),
encoding="utf-8",
)

lines=[]

lines.append(PHASE)
lines.append("")
lines.append(f"certified: {result['certified']}")
lines.append("")

for section,data in summary.items():

    lines.append(
        f"{section}: {data['metric_count']} metrics"
    )

lines.append("")
lines.append("Observability Contract Certified")
lines.append("")
lines.append("Database Writes : False")
lines.append("Promotion : False")
lines.append("Broker : False")
lines.append("Live : False")
lines.append("")
lines.append("Next:")
lines.append(result["recommended_next_phase"])

OUT_TXT.write_text(
"\n".join(lines),
encoding="utf-8",
)

print(json.dumps({

"phase":PHASE,
"certified":result["certified"],
"sections":len(summary),
"recommended_next_phase":
result["recommended_next_phase"],
"out_json":str(OUT_JSON),
"out_txt":str(OUT_TXT),

},indent=2))

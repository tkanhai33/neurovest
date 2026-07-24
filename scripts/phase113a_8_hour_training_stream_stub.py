#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json
import py_compile

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "eight_hour_training_run_manifest" / \
    "112A_8_hour_read_only_training_run_manifest_latest.json"

TARGET = ROOT / \
"backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/eight_hour_training_stream.py"

OUT_DIR = ARCH / "eight_hour_training_stream_stub"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "113A_8_hour_training_stream_stub_latest.json"
OUT_TXT = OUT_DIR / "113A_8_hour_training_stream_stub_latest.txt"

PHASE = "113A_8_HOUR_TRAINING_STREAM_STUB"


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


manifest = read_json(SOURCE)

SOURCE_TEXT = '''
from pathlib import Path
from datetime import datetime, UTC
import json

STREAM_ENABLED = True

TRAINING_EXECUTION_ENABLED = False
LEARNER_WRITE_ENABLED = False
MUTATION_ALLOWED = False
QUEUE_WRITE_ENABLED = False
STRATEGY_DB_WRITE_ALLOWED = False
PROMOTION_ENABLED = False
BROKER_EXECUTION_ENABLED = False
LIVE_EXECUTION_ENABLED = False


def append_stream_event(stream_file: Path, event_type: str, payload: dict):

    stream_file.parent.mkdir(parents=True, exist_ok=True)

    record = {
        "timestamp": datetime.now(UTC).isoformat(),
        "event": event_type,
        "payload": payload,
    }

    with stream_file.open("a", encoding="utf-8") as fp:
        fp.write(json.dumps(record))
        fp.write("\\n")


def stream_status():

    return {
        "stream_enabled": STREAM_ENABLED,
        "training_execution_enabled": TRAINING_EXECUTION_ENABLED,
        "learner_write_enabled": LEARNER_WRITE_ENABLED,
        "mutation_allowed": MUTATION_ALLOWED,
        "queue_write_enabled": QUEUE_WRITE_ENABLED,
        "strategy_db_write_allowed": STRATEGY_DB_WRITE_ALLOWED,
        "promotion_enabled": PROMOTION_ENABLED,
        "broker_execution_enabled": BROKER_EXECUTION_ENABLED,
        "live_execution_enabled": LIVE_EXECUTION_ENABLED,
    }
'''

TARGET.parent.mkdir(parents=True, exist_ok=True)
TARGET.write_text(SOURCE_TEXT, encoding="utf-8")

compile_ok = False
compile_error = None

try:
    py_compile.compile(str(TARGET), doraise=True)
    compile_ok = True
except Exception as exc:
    compile_error = {
        "type": type(exc).__name__,
        "message": str(exc),
    }

text = TARGET.read_text()

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": manifest.get("certified") is True,
    "target_written": TARGET.exists(),
    "compile_ok": compile_ok,
    "append_stream_event_present": "append_stream_event" in text,
    "stream_status_present": "stream_status" in text,
    "stream_enabled": "STREAM_ENABLED = True" in text,
    "training_blocked": "TRAINING_EXECUTION_ENABLED = False" in text,
    "db_write_blocked": "STRATEGY_DB_WRITE_ALLOWED = False" in text,
    "promotion_blocked": "PROMOTION_ENABLED = False" in text,
    "broker_live_blocked":
        "BROKER_EXECUTION_ENABLED = False" in text and
        "LIVE_EXECUTION_ENABLED = False" in text,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "target_file": str(TARGET),
    "compile_error": compile_error,
    "checks": checks,
    "policy": {
        "stream_stub_created": True,
        "stream_enabled": True,
        "training_execution_enabled": False,
        "learner_write_enabled": False,
        "mutation_allowed": False,
        "queue_write_enabled": False,
        "strategy_db_write_allowed": False,
        "promotion_enabled": False,
        "broker_execution_enabled": False,
        "live_execution_enabled": False,
    },
    "recommended_next_phase":
        "114A_8_HOUR_SANDBOX_TRAINING_EXECUTION",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2))

OUT_TXT.write_text(
    "\\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"compile_ok: {compile_ok}",
        "",
        "8-hour training stream stub created.",
        "Streaming enabled.",
        "Training remains disabled.",
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "compile_ok": compile_ok,
    "recommended_next_phase":
        result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))

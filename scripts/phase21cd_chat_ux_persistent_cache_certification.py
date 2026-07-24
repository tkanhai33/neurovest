#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
FRONTEND = ROOT / "frontend"
PAGE = ROOT / "frontend/app/page.tsx"
OUT = ROOT / "runtime/certifications/phase21cd_chat_ux_persistent_cache_certification_latest.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

def run(cmd, cwd=ROOT):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return {
        "cmd": " ".join(cmd),
        "returncode": r.returncode,
        "stdout": r.stdout[-5000:],
        "stderr": r.stderr[-5000:],
    }

steps = {
    "patch": run(["python3", "scripts/phase21cd_chat_ux_persistent_cache.py"]),
    "chat_cache_history_cert": run(["python3", "scripts/phase21ab_chat_cache_history_certification.py"]),
    "floating_chat_cert": run(["python3", "scripts/phase20f_floating_chat_widget_certification.py"]),
    "endpoint_activation_cert": run(["python3", "scripts/phase19c_endpoint_activation_certification.py"]),
    "lint": run(["npm", "run", "lint"], cwd=FRONTEND),
    "build": run(["npm", "run", "build"], cwd=FRONTEND),
    "graph_reset": run(["./neuro", "graph_reset"]),
    "simulate_trade": run(["./neuro", "simulate_trade", "AAPL"]),
    "graph_validate": run(["./neuro", "graph_validate"]),
}

page_text = PAGE.read_text() if PAGE.exists() else ""

checks = {
    "patch_ok": steps["patch"]["returncode"] == 0,
    "uses_local_storage": "neuro_chat_history_v1" in page_text,
    "uses_scroll_ref": "scrollRef" in page_text,
    "has_enter_to_send": 'event.key === "Enter"' in page_text,
    "has_shift_enter_guard": "!event.shiftKey" in page_text,
    "has_clear_history": "clearHistory" in page_text,
    "has_timestamps": "toLocaleTimeString" in page_text,
    "chat_cache_history_certified": '"certified": true' in steps["chat_cache_history_cert"]["stdout"],
    "floating_chat_certified": '"certified": true' in steps["floating_chat_cert"]["stdout"],
    "endpoint_activation_certified": '"certified": true' in steps["endpoint_activation_cert"]["stdout"],
    "lint_ok": steps["lint"]["returncode"] == 0,
    "build_ok": steps["build"]["returncode"] == 0,
    "simulate_trade_ok": '"trade_simulated"' in steps["simulate_trade"]["stdout"],
    "graph_validate_ok": '"valid": true' in steps["graph_validate"]["stdout"],
}

certified = all(checks.values())

report = {
    "phase": "21CD_CHAT_UX_PERSISTENT_CACHE_CERTIFICATION",
    "generated_at": datetime.now(UTC).isoformat(),
    "certified": certified,
    "checks": checks,
    "steps": steps,
}

OUT.write_text(json.dumps(report, indent=2))

print(json.dumps({
    "phase": report["phase"],
    "certified": certified,
    "checks": checks,
    "output": str(OUT),
}, indent=2))

if not certified:
    sys.exit(1)

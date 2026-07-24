#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
OUT = ROOT / "runtime/certifications/phase27a_strategy_proposal_capture_certification_latest.json"
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
    "phase26f_cert": run(["python3", "scripts/phase26f_chat_ui_state_cleanup_metadata_rendering_certification.py"]),
    "patch": run(["python3", "scripts/phase27a_strategy_proposal_capture.py"]),
    "compile_capture": run(["python3", "-m", "py_compile", "backend/app/stacks/chat_public/strategy_proposal_capture.py"]),
    "compile_runtime": run(["python3", "-m", "py_compile", "backend/app/stacks/chat_public/chat_runtime.py"]),
    "capture_unit": run([
        "python3", "-c",
        "from backend.app.stacks.chat_public.strategy_proposal_capture import capture_strategy_proposal; r=capture_strategy_proposal('create a strategy for RY.TO','Use RSI entry with stop-loss and take-profit', intent='trading_conversation'); print(r)"
    ]),
    "blocked_live_trade": run([
        "curl", "-s", "-X", "POST", "http://127.0.0.1:8000/api/v1/chat",
        "-H", "Content-Type: application/json",
        "-d", '{"message":"can you place a real trade for me?"}'
    ]),
}

capture = (ROOT / "backend/app/stacks/chat_public/strategy_proposal_capture.py").read_text()
runtime = (ROOT / "backend/app/stacks/chat_public/chat_runtime.py").read_text()

checks = {
    "phase26f_certified": '"certified": true' in steps["phase26f_cert"]["stdout"],
    "patch_ok": steps["patch"]["returncode"] == 0,
    "capture_module_exists": "capture_strategy_proposal" in capture,
    "capture_requires_review": "requires_promotion_review" in capture,
    "capture_simulation_only": '"simulation_only": True' in capture,
    "runtime_imports_capture": "capture_strategy_proposal" in runtime,
    "runtime_returns_strategy_capture": '"strategy_capture": strategy_capture' in runtime,
    "compile_capture_ok": steps["compile_capture"]["returncode"] == 0,
    "compile_runtime_ok": steps["compile_runtime"]["returncode"] == 0,
    "capture_unit_ok": "captured_pending_review" in steps["capture_unit"]["stdout"],
    "live_trade_still_blocked": '"status":"blocked"' in steps["blocked_live_trade"]["stdout"].replace(" ", ""),
}

certified = all(checks.values())

report = {
    "phase": "27A_STRATEGY_PROPOSAL_CAPTURE_CERTIFICATION",
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

#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
FRONTEND = ROOT / "frontend"
OUT = ROOT / "runtime/certifications/phase26d_frontend_chat_response_normalizer_certification_latest.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

def run(cmd, cwd=ROOT):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return {"cmd": " ".join(cmd), "returncode": r.returncode, "stdout": r.stdout[-5000:], "stderr": r.stderr[-5000:]}

steps = {
    "phase26c_cert": run(["python3", "scripts/phase26c_chat_safety_prompt_live_execution_guard_certification.py"]),
    "patch": run(["python3", "scripts/phase26d_frontend_chat_response_normalizer.py"]),
    "lint": run(["npm", "run", "lint"], cwd=FRONTEND),
    "build": run(["npm", "run", "build"], cwd=FRONTEND),
    "chat_test": run([
        "curl", "-s", "-X", "POST", "http://127.0.0.1:8000/api/v1/chat",
        "-H", "Content-Type: application/json",
        "-d", '{"message":"is the stock market currently open for TSX?"}'
    ]),
}

chat = (ROOT / "frontend/services/chatService.ts").read_text()

checks = {
    "phase26c_certified": '"certified": true' in steps["phase26c_cert"]["stdout"],
    "patch_ok": steps["patch"]["returncode"] == 0,
    "normalizer_exists": "normalizeChatReply" in chat,
    "normalizer_handles_nested_response": "const nested = second.response" in chat,
    "normalizer_avoids_json_dump_fallback": "no readable message" in chat,
    "lint_ok": steps["lint"]["returncode"] == 0,
    "build_ok": steps["build"]["returncode"] == 0,
    "chat_backend_ok": '"status":"ok"' in steps["chat_test"]["stdout"].replace(" ", ""),
}

certified = all(checks.values())

report = {
    "phase": "26D_FRONTEND_CHAT_RESPONSE_NORMALIZER_CERTIFICATION",
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

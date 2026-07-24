#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
FRONTEND = ROOT / "frontend"
OUT = ROOT / "runtime/certifications/phase21ab_chat_cache_history_certification_latest.json"
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
    "patch": run(["python3", "scripts/phase21ab_chat_cache_history.py"]),
    "floating_chat_cert": run(["python3", "scripts/phase20f_floating_chat_widget_certification.py"]),
    "endpoint_activation_cert": run(["python3", "scripts/phase19c_endpoint_activation_certification.py"]),
    "lint": run(["npm", "run", "lint"], cwd=FRONTEND),
    "build": run(["npm", "run", "build"], cwd=FRONTEND),
    "graph_reset": run(["./neuro", "graph_reset"]),
    "simulate_trade": run(["./neuro", "simulate_trade", "AAPL"]),
    "graph_validate": run(["./neuro", "graph_validate"]),
}

service = ROOT / "frontend/services/chatService.ts"
page = ROOT / "frontend/app/page.tsx"

service_text = service.read_text() if service.exists() else ""
page_text = page.read_text() if page.exists() else ""

checks = {
    "patch_ok": steps["patch"]["returncode"] == 0,
    "chat_message_type_exists": "export type ChatMessage" in service_text,
    "create_chat_message_exists": "createChatMessage" in service_text,
    "normalize_reply_exists": "normalizeChatReply" in service_text,
    "widget_has_message_cache": "useState<ChatMessage[]>" in page_text,
    "widget_renders_message_history": "messages.map" in page_text,
    "widget_adds_user_message": 'createChatMessage("user"' in page_text,
    "widget_adds_assistant_message": 'createChatMessage("assistant"' in page_text,
    "floating_chat_certified": '"certified": true' in steps["floating_chat_cert"]["stdout"],
    "endpoint_activation_certified": '"certified": true' in steps["endpoint_activation_cert"]["stdout"],
    "lint_ok": steps["lint"]["returncode"] == 0,
    "build_ok": steps["build"]["returncode"] == 0,
    "simulate_trade_ok": '"trade_simulated"' in steps["simulate_trade"]["stdout"],
    "graph_validate_ok": '"valid": true' in steps["graph_validate"]["stdout"],
}

certified = all(checks.values())

report = {
    "phase": "21AB_CHAT_CACHE_HISTORY_CERTIFICATION",
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

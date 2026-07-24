#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
FRONTEND = ROOT / "frontend"
OUT = ROOT / "runtime/certifications/phase26f_chat_ui_state_cleanup_metadata_rendering_certification_latest.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

def run(cmd, cwd=ROOT):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return {"cmd": " ".join(cmd), "returncode": r.returncode, "stdout": r.stdout[-5000:], "stderr": r.stderr[-5000:]}

steps = {
    "patch": run(["python3", "scripts/phase26f_chat_ui_state_cleanup_metadata_rendering.py"]),
    "lint": run(["npm", "run", "lint"], cwd=FRONTEND),
    "build": run(["npm", "run", "build"], cwd=FRONTEND),
}

page = (ROOT / "frontend/app/page.tsx").read_text()
cert26e = ROOT / "runtime/certifications/phase26e_chat_metadata_chips_typing_enter_certification_latest.json"

checks = {
    "phase26e_cert_file_exists": cert26e.exists(),
    "patch_ok": steps["patch"]["returncode"] == 0,
    "normalize_chat_meta_imported": "normalizeChatMeta" in page,
    "chat_meta_state_exists": "chatMeta" in page and "setChatMeta" in page,
    "chat_meta_rendered": "{chatMeta}" in page,
    "chat_thinking_state_removed": "chatThinking" not in page and "setChatThinking" not in page,
    "enter_to_send_preserved": 'event.key === "Enter"' in page and "void send();" in page,
    "typing_indicator_preserved": "Neuro is thinking" in page,
    "lint_ok": steps["lint"]["returncode"] == 0,
    "build_ok": steps["build"]["returncode"] == 0,
}

certified = all(checks.values())

OUT.write_text(json.dumps({
    "phase": "26F_CHAT_UI_STATE_CLEANUP_METADATA_RENDERING_CERTIFICATION",
    "generated_at": datetime.now(UTC).isoformat(),
    "certified": certified,
    "checks": checks,
    "steps": steps,
}, indent=2))

print(json.dumps({
    "phase": "26F_CHAT_UI_STATE_CLEANUP_METADATA_RENDERING_CERTIFICATION",
    "certified": certified,
    "checks": checks,
    "output": str(OUT),
}, indent=2))

if not certified:
    sys.exit(1)

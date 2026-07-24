#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
FRONTEND = ROOT / "frontend"
OUT = ROOT / "runtime/certifications/phase20f_floating_chat_widget_certification_latest.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

GRAPH = ROOT / "runtime/repo_memory/chat_service_chain_graph_v1.json"

def run(cmd, cwd=ROOT):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return {"cmd": " ".join(cmd), "returncode": r.returncode, "stdout": r.stdout[-5000:], "stderr": r.stderr[-5000:]}

steps = {
    "patch": run(["python3", "scripts/phase20_floating_chat_widget_service_chain.py"]),
    "graph_export": run(["python3", "scripts/phase20e_chat_service_chain_graph_export.py"]),
    "lint": run(["npm", "run", "lint"], cwd=FRONTEND),
    "build": run(["npm", "run", "build"], cwd=FRONTEND),
    "route_separation_cert": run(["python3", "scripts/phase16_api_route_separation_certification.py"]),
    "graph_reset": run(["./neuro", "graph_reset"]),
    "simulate_trade": run(["./neuro", "simulate_trade", "AAPL"]),
    "graph_validate": run(["./neuro", "graph_validate"]),
}

files = {
    "frontend_service": ROOT / "frontend/services/chatService.ts",
    "next_route": ROOT / "frontend/app/api/v1/chat/route.ts",
    "page": ROOT / "frontend/app/page.tsx",
}

texts = {k: v.read_text() if v.exists() else "" for k, v in files.items()}
graph = json.loads(GRAPH.read_text()) if GRAPH.exists() else {}

checks = {
    "patch_ok": steps["patch"]["returncode"] == 0,
    "frontend_service_exists": files["frontend_service"].exists(),
    "frontend_service_has_sendChatMessage": "sendChatMessage" in texts["frontend_service"],
    "next_proxy_exists": files["next_route"].exists(),
    "next_proxy_uses_backend_chat": "http://127.0.0.1:8000/api/v1/chat" in texts["next_route"],
    "floating_widget_exists": "function FloatingChatWidget()" in texts["page"],
    "floating_widget_rendered": "<FloatingChatWidget />" in texts["page"],
    "service_graph_exists": GRAPH.exists(),
    "service_graph_node_count_ok": graph.get("node_count") == 4,
    "service_graph_edge_count_ok": graph.get("edge_count") == 3,
    "lint_ok": steps["lint"]["returncode"] == 0,
    "build_ok": steps["build"]["returncode"] == 0,
    "route_separation_certified": '"certified": true' in steps["route_separation_cert"]["stdout"],
    "simulate_trade_ok": '"trade_simulated"' in steps["simulate_trade"]["stdout"],
    "graph_validate_ok": '"valid": true' in steps["graph_validate"]["stdout"],
}

certified = all(checks.values())

report = {
    "phase": "20F_FLOATING_CHAT_WIDGET_CERTIFICATION",
    "generated_at": datetime.now(UTC).isoformat(),
    "certified": certified,
    "checks": checks,
    "service_graph": str(GRAPH.relative_to(ROOT)) if GRAPH.exists() else None,
    "steps": steps,
}

OUT.write_text(json.dumps(report, indent=2))
print(json.dumps({"phase": report["phase"], "certified": certified, "checks": checks, "service_graph": report["service_graph"], "output": str(OUT)}, indent=2))

if not certified:
    sys.exit(1)

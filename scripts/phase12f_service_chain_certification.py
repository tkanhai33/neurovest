#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
FRONTEND = ROOT / "frontend"
OUT = ROOT / "runtime/certifications/phase12f_service_chain_certification_latest.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

SERVICE_GRAPH = ROOT / "runtime/repo_memory/service_chain_graph_v1.json"

FILES = {
    "backend_feed": ROOT / "backend/app/stacks/market_data/feed.py",
    "backend_service": ROOT / "backend/app/stacks/market_data/market_data_service.py",
    "backend_main": ROOT / "backend/app/main.py",
    "frontend_service": ROOT / "frontend/services/marketService.ts",
    "frontend_page": ROOT / "frontend/app/page.tsx",
}

def run(cmd, cwd=ROOT):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return {
        "cmd": " ".join(cmd),
        "cwd": str(cwd),
        "returncode": r.returncode,
        "stdout": r.stdout[-5000:],
        "stderr": r.stderr[-5000:],
    }

steps = {
    "patch": run(["python3", "scripts/phase12_service_layer_alignment.py"]),
    "compile_backend_service": run(["python3", "-m", "py_compile", "backend/app/stacks/market_data/market_data_service.py"]),
    "compile_main": run(["python3", "-m", "py_compile", "backend/app/main.py"]),
    "service_graph": run(["python3", "scripts/phase12e_service_chain_graph_export.py"]),
    "lint": run(["npm", "run", "lint"], cwd=FRONTEND),
    "build": run(["npm", "run", "build"], cwd=FRONTEND),
    "api_bridge_cert": run(["python3", "scripts/phase11_live_market_price_api_bridge_certification.py"]),
    "next_proxy_cert": run(["python3", "scripts/phase11d_next_api_proxy_live_price_certification.py"]),
    "graph_reset": run(["./neuro", "graph_reset"]),
    "simulate_trade": run(["./neuro", "simulate_trade", "AAPL"]),
    "graph_validate": run(["./neuro", "graph_validate"]),
}

texts = {k: v.read_text() if v.exists() else "" for k, v in FILES.items()}
graph = json.loads(SERVICE_GRAPH.read_text()) if SERVICE_GRAPH.exists() else {}

checks = {
    "patch_ok": steps["patch"]["returncode"] == 0,
    "backend_service_exists": FILES["backend_service"].exists(),
    "backend_service_compiles": steps["compile_backend_service"]["returncode"] == 0,
    "main_compiles": steps["compile_main"]["returncode"] == 0,
    "main_uses_service_facade": "get_live_market_price_for_api" in texts["backend_main"],
    "main_no_direct_feed_quote_import": "from backend.app.stacks.market_data.feed import get_live_price_quote" not in texts["backend_main"],
    "frontend_service_exists": FILES["frontend_service"].exists(),
    "frontend_service_has_getLivePrice": "export async function getLivePrice" in texts["frontend_service"],
    "frontend_service_has_getLivePrices": "export async function getLivePrices" in texts["frontend_service"],
    "page_imports_market_service": "getLivePrice" in texts["frontend_page"] and "getLivePrices" in texts["frontend_page"],
    "page_no_direct_live_price_fetch": "fetch(`/api/v1/market/live-price/" not in texts["frontend_page"],
    "service_graph_exists": SERVICE_GRAPH.exists(),
    "service_graph_node_count_ok": graph.get("node_count") == 6,
    "service_graph_edge_count_ok": graph.get("edge_count") == 5,
    "lint_ok": steps["lint"]["returncode"] == 0,
    "build_ok": steps["build"]["returncode"] == 0,
    "api_bridge_certified": '"certified": true' in steps["api_bridge_cert"]["stdout"],
    "next_proxy_certified": '"certified": true' in steps["next_proxy_cert"]["stdout"],
    "simulate_trade_ok": '"trade_simulated"' in steps["simulate_trade"]["stdout"],
    "graph_validate_ok": '"valid": true' in steps["graph_validate"]["stdout"],
}

certified = all(checks.values())

report = {
    "phase": "12F_SERVICE_CHAIN_CERTIFICATION",
    "generated_at": datetime.now(UTC).isoformat(),
    "certified": certified,
    "checks": checks,
    "service_graph": str(SERVICE_GRAPH.relative_to(ROOT)) if SERVICE_GRAPH.exists() else None,
    "steps": steps,
}

OUT.write_text(json.dumps(report, indent=2))

print(json.dumps({
    "phase": report["phase"],
    "certified": certified,
    "checks": checks,
    "service_graph": report["service_graph"],
    "output": str(OUT),
}, indent=2))

if not certified:
    sys.exit(1)

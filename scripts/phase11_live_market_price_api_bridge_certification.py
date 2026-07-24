#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
OUT = ROOT / "runtime/certifications/phase11_live_market_price_api_bridge_certification_latest.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

def run(cmd):
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    return {
        "cmd": " ".join(cmd),
        "returncode": r.returncode,
        "stdout": r.stdout[-4000:],
        "stderr": r.stderr[-4000:],
    }

steps = {
    "patch": run(["python3", "scripts/phase11_live_market_price_api_bridge.py"]),
    "compile_feed": run(["python3", "-m", "py_compile", "backend/app/stacks/market_data/feed.py"]),
    "compile_main": run(["python3", "-m", "py_compile", "backend/app/main.py"]),
    "repo_index": run(["python3", "scripts/phase4_repo_memory_indexer_v2.py"]),
    "repo_file_feed": run(["./neuro", "repo_file", "backend/app/stacks/market_data/feed.py"]),
    "repo_file_main": run(["./neuro", "repo_file", "backend/app/main.py"]),
    "graph_reset": run(["./neuro", "graph_reset"]),
    "simulate_trade": run(["./neuro", "simulate_trade", "AAPL"]),
    "graph_validate": run(["./neuro", "graph_validate"]),
}

feed_text = (ROOT / "backend/app/stacks/market_data/feed.py").read_text()
main_text = (ROOT / "backend/app/main.py").read_text()

checks = {
    "patch_ok": steps["patch"]["returncode"] == 0,
    "feed_compiles": steps["compile_feed"]["returncode"] == 0,
    "main_compiles": steps["compile_main"]["returncode"] == 0,
    "feed_helper_exists": "async def get_live_price_quote" in feed_text,
    "main_route_exists": '"/api/v1/market/live-price/{symbol}"' in main_text,
    "main_import_exists": "get_live_market_price_for_api" in main_text,
    "repo_index_ok": steps["repo_index"]["returncode"] == 0,
    "simulate_trade_ok": '"trade_simulated"' in steps["simulate_trade"]["stdout"],
    "graph_validate_ok": '"valid": true' in steps["graph_validate"]["stdout"],
}

certified = all(checks.values())

report = {
    "phase": "11_LIVE_MARKET_PRICE_API_BRIDGE_CERTIFICATION",
    "generated_at": datetime.now(UTC).isoformat(),
    "certified": certified,
    "checks": checks,
    "endpoint": "/api/v1/market/live-price/{symbol}",
    "example": "/api/v1/market/live-price/AAPL",
    "steps": steps,
}

OUT.write_text(json.dumps(report, indent=2))

print(json.dumps({
    "phase": report["phase"],
    "certified": certified,
    "checks": checks,
    "endpoint": report["endpoint"],
    "output": str(OUT),
}, indent=2))

if not certified:
    sys.exit(1)

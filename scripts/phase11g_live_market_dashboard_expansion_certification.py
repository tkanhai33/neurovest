#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
FRONTEND = ROOT / "frontend"
PAGE = FRONTEND / "app/page.tsx"
OUT = ROOT / "runtime/certifications/phase11g_live_market_dashboard_expansion_certification_latest.json"
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
    "patch": run(["python3", "scripts/phase11g_live_market_dashboard_expansion.py"]),
    "lint": run(["npm", "run", "lint"], cwd=FRONTEND),
    "build": run(["npm", "run", "build"], cwd=FRONTEND),
    "api_bridge_cert": run(["python3", "scripts/phase11_live_market_price_api_bridge_certification.py"]),
    "next_proxy_cert": run(["python3", "scripts/phase11d_next_api_proxy_live_price_certification.py"]),
    "graph_reset": run(["./neuro", "graph_reset"]),
    "simulate_trade": run(["./neuro", "simulate_trade", "AAPL"]),
    "graph_validate": run(["./neuro", "graph_validate"]),
}

text = PAGE.read_text() if PAGE.exists() else ""

checks = {
    "patch_ok": steps["patch"]["returncode"] == 0,
    "watchlist_component_exists": "function LiveMarketWatchlist()" in text,
    "watchlist_rendered": "<LiveMarketWatchlist />" in text,
    "watchlist_symbols_exists": "WATCHLIST_SYMBOLS" in text,
    "relative_api_used": "/api/v1/market/live-price/" in text,
    "lint_ok": steps["lint"]["returncode"] == 0,
    "build_ok": steps["build"]["returncode"] == 0,
    "api_bridge_certified": '"certified": true' in steps["api_bridge_cert"]["stdout"],
    "next_proxy_certified": '"certified": true' in steps["next_proxy_cert"]["stdout"],
    "simulate_trade_ok": '"trade_simulated"' in steps["simulate_trade"]["stdout"],
    "graph_validate_ok": '"valid": true' in steps["graph_validate"]["stdout"],
}

certified = all(checks.values())

report = {
    "phase": "11G_LIVE_MARKET_DASHBOARD_EXPANSION_CERTIFICATION",
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

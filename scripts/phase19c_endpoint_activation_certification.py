#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
OUT = ROOT / "runtime/certifications/phase19c_endpoint_activation_certification_latest.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

ENDPOINTS = {
    "market_aapl": "http://127.0.0.1:3000/api/v1/market/live-price/AAPL",
    "portfolio_positions": "http://127.0.0.1:3000/api/v1/portfolio/positions",
    "strategy_aapl": "http://127.0.0.1:3000/api/v1/strategy/decision/AAPL",
    "risk_aapl": "http://127.0.0.1:3000/api/v1/risk/gate/AAPL",
}

def run(cmd):
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    return {
        "cmd": " ".join(cmd),
        "returncode": r.returncode,
        "stdout": r.stdout[-5000:],
        "stderr": r.stderr[-5000:],
    }

def curl_json(url):
    r = subprocess.run(
        ["curl", "-s", url],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    try:
        payload = json.loads(r.stdout)
    except Exception:
        payload = {}

    return {
        "url": url,
        "returncode": r.returncode,
        "json": payload,
        "stdout": r.stdout[-1000:],
        "stderr": r.stderr[-1000:],
    }

steps = {
    "route_separation_cert": run(["python3", "scripts/phase16_api_route_separation_certification.py"]),
    "dashboard_route_map_cert": run(["python3", "scripts/phase17_dashboard_route_map_certification.py"]),
    "layout_cert": run(["python3", "scripts/phase19_dashboard_visual_layout_certification.py"]),
    "frontend_build": run(["npm", "run", "build"],),
    "graph_reset": run(["./neuro", "graph_reset"]),
    "simulate_trade": run(["./neuro", "simulate_trade", "AAPL"]),
    "graph_validate": run(["./neuro", "graph_validate"]),
}

# build must run in frontend
steps["frontend_build"] = subprocess.run(
    ["npm", "run", "build"],
    cwd=ROOT / "frontend",
    capture_output=True,
    text=True,
)
steps["frontend_build"] = {
    "cmd": "npm run build",
    "returncode": steps["frontend_build"].returncode,
    "stdout": steps["frontend_build"].stdout[-5000:],
    "stderr": steps["frontend_build"].stderr[-5000:],
}

probes = {
    name: curl_json(url)
    for name, url in ENDPOINTS.items()
}

checks = {
    "market_endpoint_active": probes["market_aapl"]["json"].get("status") == "ok"
        and probes["market_aapl"]["json"].get("price") is not None,
    "portfolio_endpoint_active": probes["portfolio_positions"]["json"].get("status") == "ok"
        and isinstance(probes["portfolio_positions"]["json"].get("positions"), list),
    "strategy_endpoint_active": probes["strategy_aapl"]["json"].get("status") in {"ok", "no_action", "error"}
        and probes["strategy_aapl"]["json"].get("provider") in {"strategy_engine", "strategy_service"},
    "risk_endpoint_active": probes["risk_aapl"]["json"].get("status") == "ok"
        and probes["risk_aapl"]["json"].get("allowed") is True,
    "route_separation_certified": '"certified": true' in steps["route_separation_cert"]["stdout"],
    "dashboard_route_map_certified": '"certified": true' in steps["dashboard_route_map_cert"]["stdout"],
    "layout_certified": '"certified": true' in steps["layout_cert"]["stdout"],
    "frontend_build_ok": steps["frontend_build"]["returncode"] == 0,
    "simulate_trade_ok": '"trade_simulated"' in steps["simulate_trade"]["stdout"],
    "graph_validate_ok": '"valid": true' in steps["graph_validate"]["stdout"],
}

certified = all(checks.values())

report = {
    "phase": "19C_ENDPOINT_ACTIVATION_CERTIFICATION",
    "generated_at": datetime.now(UTC).isoformat(),
    "certified": certified,
    "checks": checks,
    "endpoints": ENDPOINTS,
    "probes": probes,
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

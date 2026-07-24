#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
FRONTEND = ROOT / "frontend"
OUT = ROOT / "runtime/certifications/phase17_dashboard_route_map_certification_latest.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

MAP = ROOT / "runtime/repo_memory/dashboard_route_map_v1.json"

def run(cmd, cwd=ROOT):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return {
        "cmd": " ".join(cmd),
        "returncode": r.returncode,
        "stdout": r.stdout[-5000:],
        "stderr": r.stderr[-5000:],
    }

steps = {
    "route_map_export": run(["python3", "scripts/phase17_dashboard_route_map_frontend_card_verification.py"]),
    "route_separation_cert": run(["python3", "scripts/phase16_api_route_separation_certification.py"]),
    "market_chain_cert": run(["python3", "scripts/phase12f_service_chain_certification.py"]),
    "portfolio_chain_cert": run(["python3", "scripts/phase13f_portfolio_positions_service_chain_certification.py"]),
    "strategy_chain_cert": run(["python3", "scripts/phase14f_strategy_decision_service_chain_certification.py"]),
    "risk_chain_cert": run(["python3", "scripts/phase15f_risk_gate_service_chain_certification.py"]),
    "lint": run(["npm", "run", "lint"], cwd=FRONTEND),
    "build": run(["npm", "run", "build"], cwd=FRONTEND),
    "graph_reset": run(["./neuro", "graph_reset"]),
    "simulate_trade": run(["./neuro", "simulate_trade", "AAPL"]),
    "graph_validate": run(["./neuro", "graph_validate"]),
}

data = json.loads(MAP.read_text()) if MAP.exists() else {}
route_map = data.get("route_map", {})

def all_values_true(obj):
    if isinstance(obj, dict):
        return all(all_values_true(v) for v in obj.values())
    return obj is True or isinstance(obj, str)

stack_checks = {}

for stack, item in route_map.items():
    stack_checks[stack] = {
        "components_present": all(item.get("frontend_components", {}).values()),
        "frontend_service_ok": (
            item.get("frontend_service", {}).get("exists") is True
            and all(item.get("frontend_service", {}).get("functions", {}).values())
            and item.get("frontend_service", {}).get("uses_frontend_endpoint") is True
            and item.get("frontend_service", {}).get("does_not_call_chat") is True
        ),
        "next_proxy_ok": (
            item.get("next_proxy", {}).get("exists") is True
            and item.get("next_proxy", {}).get("uses_backend_endpoint") is True
            and item.get("next_proxy", {}).get("does_not_call_chat") is True
        ),
    }

checks = {
    "route_map_exists": MAP.exists(),
    "route_map_has_4_stacks": len(route_map) == 4,
    "market_dashboard_route_ok": all(stack_checks.get("market", {}).values()),
    "portfolio_dashboard_route_ok": all(stack_checks.get("portfolio", {}).values()),
    "strategy_dashboard_route_ok": all(stack_checks.get("strategy", {}).values()),
    "risk_dashboard_route_ok": all(stack_checks.get("risk", {}).values()),
    "route_separation_certified": '"certified": true' in steps["route_separation_cert"]["stdout"],
    "market_chain_certified": '"certified": true' in steps["market_chain_cert"]["stdout"],
    "portfolio_chain_certified": '"certified": true' in steps["portfolio_chain_cert"]["stdout"],
    "strategy_chain_certified": '"certified": true' in steps["strategy_chain_cert"]["stdout"],
    "risk_chain_certified": '"certified": true' in steps["risk_chain_cert"]["stdout"],
    "lint_ok": steps["lint"]["returncode"] == 0,
    "build_ok": steps["build"]["returncode"] == 0,
    "simulate_trade_ok": '"trade_simulated"' in steps["simulate_trade"]["stdout"],
    "graph_validate_ok": '"valid": true' in steps["graph_validate"]["stdout"],
}

certified = all(checks.values())

report = {
    "phase": "17_DASHBOARD_ROUTE_MAP_CERTIFICATION",
    "generated_at": datetime.now(UTC).isoformat(),
    "certified": certified,
    "checks": checks,
    "stack_checks": stack_checks,
    "route_map": route_map,
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

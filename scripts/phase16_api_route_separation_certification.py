#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

from fastapi.routing import APIRoute

ROOT = Path(".").resolve()
OUT = ROOT / "runtime/certifications/phase16_api_route_separation_certification_latest.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

EXPECTED_ROUTES = {
    "/api/v1/market/live-price/{symbol}": "market",
    "/api/v1/portfolio/positions": "portfolio",
    "/api/v1/strategy/decision/{symbol}": "strategy",
    "/api/v1/risk/gate/{symbol}": "risk",
    "/api/v1/chat": "chat",
}

FRONTEND_SERVICES = {
    "market": ROOT / "frontend/services/marketService.ts",
    "portfolio": ROOT / "frontend/services/portfolioService.ts",
    "strategy": ROOT / "frontend/services/strategyService.ts",
    "risk": ROOT / "frontend/services/riskService.ts",
}

NEXT_PROXY_ROUTES = {
    "market": ROOT / "frontend/app/api/v1/market/live-price/[symbol]/route.ts",
    "portfolio": ROOT / "frontend/app/api/v1/portfolio/positions/route.ts",
    "strategy": ROOT / "frontend/app/api/v1/strategy/decision/[symbol]/route.ts",
    "risk": ROOT / "frontend/app/api/v1/risk/gate/[symbol]/route.ts",
}

def run(cmd, cwd=ROOT):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return {
        "cmd": " ".join(cmd),
        "returncode": r.returncode,
        "stdout": r.stdout[-5000:],
        "stderr": r.stderr[-5000:],
    }

def collect_routes():
    from backend.app.main import app

    rows = []
    for route in app.routes:
        if not isinstance(route, APIRoute):
            continue

        rows.append({
            "path": route.path,
            "methods": sorted(route.methods or []),
            "name": route.name,
        })

    return rows

routes = collect_routes()
route_paths = {r["path"] for r in routes}

frontend_service_texts = {
    name: path.read_text() if path.exists() else ""
    for name, path in FRONTEND_SERVICES.items()
}

next_proxy_texts = {
    name: path.read_text() if path.exists() else ""
    for name, path in NEXT_PROXY_ROUTES.items()
}

steps = {
    "market_chain_cert": run(["python3", "scripts/phase12f_service_chain_certification.py"]),
    "portfolio_chain_cert": run(["python3", "scripts/phase13f_portfolio_positions_service_chain_certification.py"]),
    "strategy_chain_cert": run(["python3", "scripts/phase14f_strategy_decision_service_chain_certification.py"]),
    "risk_chain_cert": run(["python3", "scripts/phase15f_risk_gate_service_chain_certification.py"]),
    "graph_reset": run(["./neuro", "graph_reset"]),
    "simulate_trade": run(["./neuro", "simulate_trade", "AAPL"]),
    "graph_validate": run(["./neuro", "graph_validate"]),
}

service_route_checks = {
    stack: path in route_paths
    for path, stack in EXPECTED_ROUTES.items()
}

frontend_no_chat_calls = {
    name: "/api/v1/chat" not in text
    for name, text in frontend_service_texts.items()
}

next_proxy_no_chat_calls = {
    name: "/api/v1/chat" not in text
    for name, text in next_proxy_texts.items()
}

frontend_service_exists = {
    name: path.exists()
    for name, path in FRONTEND_SERVICES.items()
}

next_proxy_exists = {
    name: path.exists()
    for name, path in NEXT_PROXY_ROUTES.items()
}

checks = {
    "market_route_exists": service_route_checks["market"],
    "portfolio_route_exists": service_route_checks["portfolio"],
    "strategy_route_exists": service_route_checks["strategy"],
    "risk_route_exists": service_route_checks["risk"],
    "legacy_positions_route_still_separate": "/api/v1/positions" in route_paths,
    "frontend_services_exist": all(frontend_service_exists.values()),
    "next_proxy_routes_exist": all(next_proxy_exists.values()),
    "frontend_services_do_not_call_chat": all(frontend_no_chat_calls.values()),
    "next_proxy_routes_do_not_call_chat": all(next_proxy_no_chat_calls.values()),
    "market_chain_certified": '"certified": true' in steps["market_chain_cert"]["stdout"],
    "portfolio_chain_certified": '"certified": true' in steps["portfolio_chain_cert"]["stdout"],
    "strategy_chain_certified": '"certified": true' in steps["strategy_chain_cert"]["stdout"],
    "risk_chain_certified": '"certified": true' in steps["risk_chain_cert"]["stdout"],
    "simulate_trade_ok": '"trade_simulated"' in steps["simulate_trade"]["stdout"],
    "graph_validate_ok": '"valid": true' in steps["graph_validate"]["stdout"],
}

certified = all(checks.values())

report = {
    "phase": "16_API_ROUTE_SEPARATION_CERTIFICATION",
    "generated_at": datetime.now(UTC).isoformat(),
    "certified": certified,
    "checks": checks,
    "routes": routes,
    "expected_routes": EXPECTED_ROUTES,
    "frontend_service_exists": frontend_service_exists,
    "next_proxy_exists": next_proxy_exists,
    "frontend_no_chat_calls": frontend_no_chat_calls,
    "next_proxy_no_chat_calls": next_proxy_no_chat_calls,
    "steps": steps,
}

OUT.write_text(json.dumps(report, indent=2))

print(json.dumps({
    "phase": report["phase"],
    "certified": certified,
    "checks": checks,
    "route_count": len(routes),
    "output": str(OUT),
}, indent=2))

if not certified:
    sys.exit(1)

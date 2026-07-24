#!/usr/bin/env python3
import json
import re
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
OUT = ROOT / "runtime/repo_memory/dashboard_route_map_v1.json"

PAGE = ROOT / "frontend/app/page.tsx"

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

EXPECTED = {
    "market": {
        "component_markers": ["LivePriceCard", "LiveMarketWatchlist"],
        "frontend_service_functions": ["getLivePrice", "getLivePrices"],
        "frontend_endpoint": "/api/v1/market/live-price/",
        "backend_endpoint": "http://127.0.0.1:8000/api/v1/market/live-price",
    },
    "portfolio": {
        "component_markers": ["PositionsPanel"],
        "frontend_service_functions": ["getPortfolioPositions"],
        "frontend_endpoint": "/api/v1/portfolio/positions",
        "backend_endpoint": "http://127.0.0.1:8000/api/v1/portfolio/positions",
    },
    "strategy": {
        "component_markers": ["StrategyDecisionCard"],
        "frontend_service_functions": ["getStrategyDecision"],
        "frontend_endpoint": "/api/v1/strategy/decision/",
        "backend_endpoint": "http://127.0.0.1:8000/api/v1/strategy/decision",
    },
    "risk": {
        "component_markers": ["RiskGateCard"],
        "frontend_service_functions": ["getRiskGate"],
        "frontend_endpoint": "/api/v1/risk/gate/",
        "backend_endpoint": "http://127.0.0.1:8000/api/v1/risk/gate",
    },
}

page_text = PAGE.read_text() if PAGE.exists() else ""

route_map = {}

for name, expected in EXPECTED.items():
    service_path = FRONTEND_SERVICES[name]
    proxy_path = NEXT_PROXY_ROUTES[name]

    service_text = service_path.read_text() if service_path.exists() else ""
    proxy_text = proxy_path.read_text() if proxy_path.exists() else ""

    route_map[name] = {
        "frontend_components": {
            marker: marker in page_text
            for marker in expected["component_markers"]
        },
        "frontend_service": {
            "path": str(service_path.relative_to(ROOT)),
            "exists": service_path.exists(),
            "functions": {
                fn: fn in service_text
                for fn in expected["frontend_service_functions"]
            },
            "uses_frontend_endpoint": expected["frontend_endpoint"] in service_text,
            "does_not_call_chat": "/api/v1/chat" not in service_text,
        },
        "next_proxy": {
            "path": str(proxy_path.relative_to(ROOT)),
            "exists": proxy_path.exists(),
            "uses_backend_endpoint": expected["backend_endpoint"] in proxy_text,
            "does_not_call_chat": "/api/v1/chat" not in proxy_text,
        },
    }

report = {
    "phase": "17_DASHBOARD_ROUTE_MAP_FRONTEND_CARD_VERIFICATION",
    "generated_at": datetime.now(UTC).isoformat(),
    "dashboard_page": str(PAGE.relative_to(ROOT)),
    "route_map": route_map,
}

OUT.write_text(json.dumps(report, indent=2))

print(json.dumps({
    "phase": report["phase"],
    "route_count": len(route_map),
    "output": str(OUT),
}, indent=2))
